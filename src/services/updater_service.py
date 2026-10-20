"""
Módulo de Atualização Automática (Auto-Update) do Sistema ALS
Gerencia verificação de releases no GitHub, download em segundo plano com progresso,
garantia de integridade, backup preventivo e execução silenciosa do instalador Inno Setup.
"""
import os
import sys
import json
import logging
import shutil
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Callable
from PySide6.QtCore import QThread, Signal

from src.config import (
    APP_VERSION,
    GITHUB_REPO,
    UPDATE_FLAG_MANDATORY,
    DB_PATH,
    BACKUP_DIR
)


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
    def baixar_instalador(
        download_url: str, 
        destino_path: str, 
        token: Optional[str] = None, 
        progresso_callback: Optional[Callable[[int], None]] = None
    ) -> bool:
        """Baixa o instalador do GitHub em blocos com relatório de progresso percentual"""
        try:
            os.makedirs(os.path.dirname(destino_path), exist_ok=True)
            req = urllib.request.Request(
                download_url,
                headers={"User-Agent": "SistemaALS-AutoUpdater"}
            )
            if token:
                req.add_header("Authorization", f"Bearer {token}")

            with urllib.request.urlopen(req, timeout=30) as resp, open(destino_path, "wb") as f_out:
                total_bytes = int(resp.headers.get("Content-Length", 0))
                baixados = 0
                chunk_size = 64 * 1024  # 64 KB

                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f_out.write(chunk)
                    baixados += len(chunk)
                    if total_bytes > 0 and progresso_callback:
                        porcentagem = int((baixados / total_bytes) * 100)
                        progresso_callback(min(porcentagem, 100))

            return os.path.exists(destino_path) and os.path.getsize(destino_path) > 0
        except Exception:
            return False

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
    def aplicar_atualizacao(caminho_instalador: str):
        """
        Fecha todas as conexões com o banco, aciona o instalador Inno Setup em modo silencioso
        e finaliza o aplicativo atual para substituição segura dos arquivos.
        """
        # Desconecta o pool do SQLAlchemy para liberar locks de arquivo SQLite WAL
        try:
            from src.models.database import get_engine
            get_engine().dispose()
        except Exception:
            pass

        # Encerra o servidor do dashboard: o processo filho mantem o .exe bloqueado
        try:
            from PySide6.QtWidgets import QApplication
            for w in QApplication.topLevelWidgets():
                dash = getattr(w, "dashboard_view", None)
                if dash is not None:
                    dash.encerrar_servidor()
        except Exception:
            pass

        # Instala na pasta do exe em execucao: assim a atualizacao vale para a copia que o usuario
        # realmente abre (instalada, portatil ou de desenvolvimento), sem criar uma 2a instalacao
        pasta_app = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, "frozen", False) else None
        log_instalador = os.path.join(os.path.dirname(caminho_instalador), "instalador.log")
        comando = UpdaterService.montar_comando_instalador(caminho_instalador, pasta_app, log_instalador)
        logging.info("Iniciando instalador: %s", comando)
        flags = 0
        if os.name == "nt":
            flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        # O exe reaberto pelo instalador NAO pode herdar o ambiente do PyInstaller deste processo:
        # senao tenta usar a pasta _MEI atual (apagada ao sair) e falha com "Failed to load Python DLL"
        env = {k: v for k, v in os.environ.items() if not k.startswith("_PYI") and k != "_MEIPASS2"}
        env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
        subprocess.Popen(comando, shell=False, close_fds=True, creationflags=flags, env=env)

        # Encerramento imediato (sys.exit dentro de slot Qt nao finaliza o processo)
        os._exit(0)


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

    def __init__(self, download_url: str, destino_path: str, token: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.destino_path = destino_path
        self.token = token

    def run(self):
        # 1. Faz backup de segurança do banco local
        UpdaterService.fazer_backup_preventivo()

        # 2. Baixa o instalador
        ok = UpdaterService.baixar_instalador(
            self.download_url,
            self.destino_path,
            self.token,
            lambda pct: self.progresso.emit(pct)
        )

        if ok:
            self.sucesso.emit(self.destino_path)
        else:
            self.falha.emit("Falha no download da atualização. Verifique sua conexão com a internet.")
