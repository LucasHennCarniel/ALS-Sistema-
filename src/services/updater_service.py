"""
Módulo de Atualização Automática (Auto-Update) do Sistema ALS
Gerencia verificação de releases no GitHub, download em segundo plano com progresso,
garantia de integridade, backup preventivo e execução silenciosa do instalador Inno Setup.
"""
import os
import sys
import hashlib
import http.client
import json
import logging
import shutil
import socket
import time
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Callable, Tuple
from PySide6.QtCore import QThread, Signal

from src.config import (
    APP_VERSION,
    GITHUB_REPO,
    UPDATE_FLAG_MANDATORY,
    DB_PATH,
    BACKUP_DIR
)


NOME_INSTALADOR = "Instalador_SistemaALS_Setup.exe"
NOME_MARCADOR = "instalacao_em_andamento.json"
NOME_LOG_INSTALADOR = "instalador.log"
TAMANHO_BLOCO = 256 * 1024
STILL_ACTIVE = 259


def pasta_atualizacao() -> str:
    """Pasta temporária usada pelo updater (instalador baixado, log e marcador de instalação)"""
    return os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "ALS_Update")


def processo_ativo(pid: int) -> bool:
    """True se existe um processo em execução com esse PID"""
    if not pid or pid <= 0:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32
    kernel32.OpenProcess.restype = wintypes.HANDLE
    handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return False
    try:
        codigo = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(codigo)):
            return False
        return codigo.value == STILL_ACTIVE
    finally:
        kernel32.CloseHandle(handle)


class _ErroGravacao(Exception):
    """Falha ao escrever o instalador no disco (não é problema de rede)"""


@dataclass
class UpdateInfo:
    """Informações estruturadas sobre uma nova versão disponível"""
    disponivel: bool
    versao: str
    obrigatoria: bool
    download_url: str
    notas_versao: str
    tamanho_bytes: int = 0


def parse_versao(versao_str: str) -> tuple:
    """Converte string de versão (ex: 'v1.2.3' ou '1.2.3') em tupla de inteiros (1, 2, 3)"""
    limpa = versao_str.strip().lstrip("vV")
    partes = []
    for p in limpa.split("."):
        try:
            partes.append(int(p))
        except ValueError:
            partes.append(0)
    return tuple(partes)


def versao_maior(remota: str, local: str) -> bool:
    """Retorna True se a versão remota for estritamente mais recente que a local"""
    return parse_versao(remota) > parse_versao(local)


class UpdaterService:
    """Serviço com regras de negócio para verificação e aplicação de atualizações"""

    @staticmethod
    def checar_atualizacao(token: Optional[str] = None) -> Optional[UpdateInfo]:
        """
        Consulta a API do GitHub Releases buscando a versão mais recente publicada.
        Não bloqueia se não houver internet (retorna None de forma segura).
        """
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "SistemaALS-AutoUpdater",
                "Accept": "application/vnd.github.v3+json",
            }
        )
        if token:
            req.add_header("Authorization", f"Bearer {token}")

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status != 200:
                    return None
                dados = json.loads(response.read().decode("utf-8"))

            tag_name = dados.get("tag_name", "")
            nome_release = dados.get("name", "")
            corpo = dados.get("body", "")

            logging.info("Checagem de atualizacao: local=%s remota=%s", APP_VERSION, tag_name)
            if not tag_name or not versao_maior(tag_name, APP_VERSION):
                return None

            # Detecta se a atualização é mandatória (Opção A: flag nas notas ou título)
            is_obrigatoria = (
                UPDATE_FLAG_MANDATORY in nome_release or 
                UPDATE_FLAG_MANDATORY in corpo
            )

            # Localiza o executável do instalador nos assets da release
            download_url = ""
            tamanho = 0
            for asset in dados.get("assets", []):
                nome_asset = asset.get("name", "")
                if nome_asset.lower().endswith(".exe") and "instalador" in nome_asset.lower():
                    download_url = asset.get("browser_download_url", "")
                    tamanho = asset.get("size", 0)
                    break
                elif nome_asset.lower().endswith(".exe"):
                    download_url = asset.get("browser_download_url", "")
                    tamanho = asset.get("size", 0)

            if not download_url:
                return None

            return UpdateInfo(
                disponivel=True,
                versao=tag_name,
                obrigatoria=is_obrigatoria,
                download_url=download_url,
                notas_versao=corpo or "Melhorias de desempenho e correções gerais.",
                tamanho_bytes=tamanho
            )

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            # Se estiver sem internet ou o repositório estiver inacessível, falha silenciosamente
            return None

    @staticmethod
    def fazer_backup_preventivo() -> Optional[str]:
        """Copia o banco SQLite para a pasta de backup antes de aplicar a atualização"""
        if not os.path.exists(DB_PATH):
            return None

        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = os.path.join(BACKUP_DIR, f"sistema_als_pre_update_{timestamp}.db")
        try:
            shutil.copy2(DB_PATH, destino)
            return destino
        except Exception:
            return None

    @staticmethod
    def _liberar_destino(destino_path: str) -> str:
        """
        Garante um caminho livre para o instalador. Se o arquivo antigo estiver em uso
        (ex.: instalador anterior ainda rodando), usa um nome alternativo em vez de falhar.
        """
        if not os.path.exists(destino_path):
            return destino_path
        try:
            os.remove(destino_path)
            return destino_path
        except OSError:
            base, ext = os.path.splitext(destino_path)
            alternativo = f"{base}_{int(time.time())}{ext}"
            logging.warning("Instalador anterior em uso (%s); usando %s", destino_path, alternativo)
            return alternativo

    @staticmethod
    def _limpar_downloads_antigos(pasta: str, manter: Tuple[str, ...]):
        """Remove instaladores e parciais de tentativas anteriores (os que estiverem em uso são ignorados)"""
        try:
            for nome in os.listdir(pasta):
                caminho = os.path.join(pasta, nome)
                if caminho in manter or not nome.startswith("Instalador_SistemaALS_Setup"):
                    continue
                try:
                    os.remove(caminho)
                except OSError:
                    pass
        except OSError:
            pass

    @staticmethod
    def baixar_instalador_robusto(
        download_url: str,
        destino_path: str,
        token: Optional[str] = None,
        progresso_callback: Optional[Callable[[int], None]] = None,
        tamanho_esperado: int = 0,
        tentativas: int = 3,
        espera_base: float = 2.0,
    ) -> Tuple[bool, str]:
        """
        Baixa o instalador com tentativas automáticas e retomada (Range) do ponto onde parou.
        Retorna (True, caminho_final) ou (False, mensagem_clara_para_o_usuario).
        """
        pasta = os.path.dirname(destino_path)
        try:
            os.makedirs(pasta, exist_ok=True)
        except OSError as e:
            return False, f"Não foi possível criar a pasta temporária {pasta}: {e}"

        destino_path = UpdaterService._liberar_destino(destino_path)
        # O parcial leva o hash da URL (que inclui a versão): nunca retoma download de outra versão
        sufixo = hashlib.sha1(download_url.encode("utf-8")).hexdigest()[:8]
        parcial = f"{destino_path}.{sufixo}.part"
        UpdaterService._limpar_downloads_antigos(pasta, (destino_path, parcial))

        erro = "Falha desconhecida no download."
        concluido = False
        for tentativa in range(1, tentativas + 1):
            try:
                ja_baixado = os.path.getsize(parcial) if os.path.exists(parcial) else 0
                if tamanho_esperado and ja_baixado > tamanho_esperado:
                    os.remove(parcial)
                    ja_baixado = 0
                if tamanho_esperado and ja_baixado == tamanho_esperado:
                    concluido = True
                    break

                req = urllib.request.Request(download_url, headers={"User-Agent": "SistemaALS-AutoUpdater"})
                if ja_baixado:
                    req.add_header("Range", f"bytes={ja_baixado}-")
                if token:
                    req.add_header("Authorization", f"Bearer {token}")

                logging.info("Download (tentativa %d/%d) a partir de %d bytes: %s",
                             tentativa, tentativas, ja_baixado, download_url)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if ja_baixado and getattr(resp, "status", 200) != 206:
                        ja_baixado = 0  # o servidor ignorou o Range: recomeça do zero
                    restante = int(resp.headers.get("Content-Length", 0) or 0)
                    total = ja_baixado + restante if restante else tamanho_esperado
                    try:
                        arquivo = open(parcial, "ab" if ja_baixado else "wb")
                    except OSError as e:
                        raise _ErroGravacao(str(e))
                    with arquivo:
                        baixados = ja_baixado
                        while True:
                            bloco = resp.read(TAMANHO_BLOCO)
                            if not bloco:
                                break
                            try:
                                arquivo.write(bloco)
                            except OSError as e:
                                raise _ErroGravacao(str(e))
                            baixados += len(bloco)
                            if total and progresso_callback:
                                progresso_callback(min(int(baixados * 100 / total), 100))

                tamanho_final = os.path.getsize(parcial)
                esperado = tamanho_esperado or total
                if esperado and tamanho_final != esperado:
                    erro = f"Download incompleto ({tamanho_final} de {esperado} bytes)."
                    if tamanho_final > esperado:
                        os.remove(parcial)
                else:
                    concluido = True
                    break

            except _ErroGravacao as e:
                return False, (f"Não foi possível gravar o instalador em {pasta}: {e}. "
                               "Verifique o espaço em disco e se o antivírus não está bloqueando a pasta.")
            except urllib.error.HTTPError as e:
                if e.code == 416:  # intervalo inválido: descarta o parcial e recomeça
                    try:
                        os.remove(parcial)
                    except OSError:
                        pass
                    erro = "O servidor não aceitou retomar o download; recomeçando."
                elif 400 <= e.code < 500 and e.code not in (408, 429):
                    return False, f"O GitHub recusou o download (HTTP {e.code}). A versão pode ter sido removida."
                else:
                    erro = f"Servidor do GitHub indisponível (HTTP {e.code})."
            except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError,
                    http.client.HTTPException, OSError) as e:
                motivo = getattr(e, "reason", None) or e
                erro = f"Falha de conexão com o GitHub: {motivo}."
            logging.warning("Download falhou (tentativa %d/%d): %s", tentativa, tentativas, erro)
            if tentativa < tentativas:
                time.sleep(espera_base * tentativa)

        if not concluido:
            return False, (f"Não foi possível baixar a atualização após {tentativas} tentativas. {erro} "
                           "Verifique a internet, o proxy e o antivírus. Ao tentar novamente, "
                           "o download continua de onde parou.")
        try:
            os.replace(parcial, destino_path)
        except OSError as e:
            return False, f"Não foi possível finalizar o instalador em {pasta}: {e}"
        logging.info("Instalador baixado: %s (%d bytes)", destino_path, os.path.getsize(destino_path))
        return True, destino_path

    @staticmethod
    def baixar_instalador(
        download_url: str,
        destino_path: str,
        token: Optional[str] = None,
        progresso_callback: Optional[Callable[[int], None]] = None
    ) -> bool:
        """Versão simplificada (True/False) de baixar_instalador_robusto"""
        ok, _ = UpdaterService.baixar_instalador_robusto(
            download_url, destino_path, token, progresso_callback, tentativas=1
        )
        return ok

    @staticmethod
    def montar_comando_instalador(caminho_instalador: str, pasta_app: Optional[str], log_instalador: str) -> str:
        """
        Linha de comando do instalador Inno Setup (silenciosa). Montada como texto porque o Inno
        exige /DIR="caminho com espacos" com as aspas dentro do valor.
        """
        comando = f'"{caminho_instalador}" /SILENT /SUPPRESSMSGBOXES /NORESTART'
        if pasta_app:
            comando += f' /DIR="{pasta_app.rstrip(chr(92))}"'
        return comando + f' /LOG="{log_instalador}"'

    @staticmethod
    def _liberar_recursos_do_app():
        """Solta o banco e o servidor do dashboard: o processo filho mantém o .exe bloqueado"""
        try:
            from src.models.database import get_engine
            get_engine().dispose()
        except Exception:
            pass
        try:
            from PySide6.QtWidgets import QApplication
            for w in QApplication.topLevelWidgets():
                dash = getattr(w, "dashboard_view", None)
                if dash is not None:
                    dash.encerrar_servidor()
        except Exception:
            pass

    @staticmethod
    def registrar_instalacao(pid: int, versao: str, log_path: str):
        """Marca que um instalador está rodando, para o app não abrir no meio da substituição dos arquivos"""
        try:
            os.makedirs(pasta_atualizacao(), exist_ok=True)
            with open(os.path.join(pasta_atualizacao(), NOME_MARCADOR), "w", encoding="utf-8") as f:
                json.dump({"pid": pid, "versao": versao, "inicio": time.time(), "log": log_path}, f)
        except OSError as e:
            logging.warning("Não foi possível gravar o marcador de instalação: %s", e)

    @staticmethod
    def limpar_marcador_instalacao():
        try:
            os.remove(os.path.join(pasta_atualizacao(), NOME_MARCADOR))
        except OSError:
            pass

    @staticmethod
    def instalacao_em_andamento(max_minutos: int = 15, versao_atual: Optional[str] = None) -> Optional[dict]:
        """
        Dados da instalação em curso (pid, versao, log) ou None. Marcadores velhos ou órfãos são removidos.
        versao_atual: só uma cópia MAIS ANTIGA que a versão sendo instalada deve esperar; a versão nova
        (recém-aberta pelo instalador) ou uma mais recente ignora e limpa o marcador.
        """
        caminho = os.path.join(pasta_atualizacao(), NOME_MARCADOR)
        if not os.path.exists(caminho):
            return None
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            recente = (time.time() - float(dados.get("inicio", 0))) < max_minutos * 60
            esta_desatualizada = versao_atual is None or versao_maior(str(dados.get("versao", "")), versao_atual)
            if recente and esta_desatualizada and processo_ativo(int(dados.get("pid", 0))):
                return dados
        except (OSError, ValueError):
            pass
        UpdaterService.limpar_marcador_instalacao()
        return None

    @staticmethod
    def instalacao_foi_concluida(log_path: str) -> Optional[bool]:
        """Lê o log do Inno Setup: True = concluiu, False = falhou, None = log indisponível"""
        try:
            with open(log_path, "rb") as f:
                texto = f.read().decode("latin-1")
        except OSError:
            return None
        return "Installation process succeeded" in texto

    @staticmethod
    def iniciar_instalador(caminho_instalador: str, versao: str = ""):
        """
        Dispara o instalador Inno Setup (silencioso) SEM encerrar o app, para a interface poder
        acompanhar se ele realmente iniciou. Retorna (processo, caminho_do_log).
        """
        UpdaterService._liberar_recursos_do_app()

        # Instala na pasta do exe em execucao: assim a atualizacao vale para a copia que o usuario
        # realmente abre (instalada, portatil ou de desenvolvimento), sem criar uma 2a instalacao
        pasta_app = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, "frozen", False) else None
        log_instalador = os.path.join(pasta_atualizacao(), NOME_LOG_INSTALADOR)
        try:
            os.remove(log_instalador)
        except OSError:
            pass
        comando = UpdaterService.montar_comando_instalador(caminho_instalador, pasta_app, log_instalador)
        logging.info("Iniciando instalador: %s", comando)
        flags = 0
        if os.name == "nt":
            flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        # O exe reaberto pelo instalador NAO pode herdar o ambiente do PyInstaller deste processo:
        # senao tenta usar a pasta _MEI atual (apagada ao sair) e falha com "Failed to load Python DLL"
        env = {k: v for k, v in os.environ.items() if not k.startswith("_PYI") and k != "_MEIPASS2"}
        env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
        processo = subprocess.Popen(comando, shell=False, close_fds=True, creationflags=flags, env=env)
        UpdaterService.registrar_instalacao(processo.pid, versao, log_instalador)
        return processo, log_instalador

    @staticmethod
    def finalizar_para_instalacao():
        """Encerra o app de imediato para o instalador substituir os arquivos"""
        logging.info("Encerrando o app para a atualizacao")
        logging.shutdown()
        # sys.exit dentro de slot Qt nao finaliza o processo
        os._exit(0)

    @staticmethod
    def aplicar_atualizacao(caminho_instalador: str):
        """Compatibilidade: inicia o instalador e encerra o app imediatamente"""
        UpdaterService.iniciar_instalador(caminho_instalador)
        UpdaterService.finalizar_para_instalacao()


class CheckUpdateThread(QThread):
    """Thread em segundo plano para consultar novidades sem congelar a interface gráfica"""
    resultado = Signal(object)  # Emite UpdateInfo ou None

    def __init__(self, token: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.token = token

    def run(self):
        # Rodando pelo codigo-fonte, APP_VERSION (config.py) nao acompanha as releases: checar geraria
        # um aviso eterno. Para testar o fluxo pelo codigo-fonte, defina ALS_VERIFICAR_UPDATE=1.
        if not getattr(sys, "frozen", False) and not os.environ.get("ALS_VERIFICAR_UPDATE"):
            logging.info("Execucao pelo codigo-fonte: checagem de atualizacao ignorada")
            self.resultado.emit(None)
            return
        info = UpdaterService.checar_atualizacao(self.token)
        self.resultado.emit(info)


class DownloadUpdateThread(QThread):
    """Thread para realizar o download com emissão de progresso e conclusão"""
    progresso = Signal(int)       # 0 a 100%
    sucesso = Signal(str)         # Caminho do instalador baixado
    falha = Signal(str)           # Mensagem de erro

    def __init__(self, download_url: str, destino_path: str, token: Optional[str] = None,
                 parent=None, tamanho_esperado: int = 0):
        super().__init__(parent)
        self.download_url = download_url
        self.destino_path = destino_path
        self.token = token
        self.tamanho_esperado = tamanho_esperado

    def run(self):
        try:
            # 1. Faz backup de segurança do banco local (não impede a atualização se falhar)
            try:
                UpdaterService.fazer_backup_preventivo()
            except Exception as e:
                logging.warning("Backup preventivo falhou: %s", e)

            # 2. Baixa o instalador
            ok, resultado = UpdaterService.baixar_instalador_robusto(
                self.download_url,
                self.destino_path,
                self.token,
                lambda pct: self.progresso.emit(pct),
                tamanho_esperado=self.tamanho_esperado,
            )
        except Exception as e:
            logging.exception("Erro inesperado no download da atualizacao")
            ok, resultado = False, f"Erro inesperado ao baixar a atualização: {e}"

        if ok:
            self.sucesso.emit(resultado)
        else:
            self.falha.emit(resultado)
