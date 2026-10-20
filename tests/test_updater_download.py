"""
Testes do download robusto e do controle de instalação em andamento (UpdaterService)
Usam um servidor HTTP local para simular conexão cortada, erros HTTP e retomada (Range)
"""
import json
import os
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from src.services import updater_service
from src.services.updater_service import UpdaterService, processo_ativo

CONTEUDO = os.urandom(300_000)


class _Servidor:
    def __init__(self, conteudo=CONTEUDO, cortar_primeira=False, status_fixo=None):
        self.conteudo = conteudo
        self.cortar_primeira = cortar_primeira
        self.status_fixo = status_fixo
        self.requisicoes = []  # cabeçalho Range de cada requisição
        servidor = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                servidor.requisicoes.append(self.headers.get("Range"))
                if servidor.status_fixo:
                    self.send_error(servidor.status_fixo)
                    return
                inicio = 0
                faixa = self.headers.get("Range")
                if faixa and faixa.startswith("bytes="):
                    inicio = int(faixa[6:].split("-")[0])
                corpo = servidor.conteudo[inicio:]
                self.send_response(206 if inicio else 200)
                self.send_header("Content-Length", str(len(corpo)))
                if inicio:
                    self.send_header("Content-Range", f"bytes {inicio}-{len(servidor.conteudo) - 1}/{len(servidor.conteudo)}")
                self.end_headers()
                if servidor.cortar_primeira and len(servidor.requisicoes) == 1:
                    self.wfile.write(corpo[: len(corpo) // 2])  # conexão cai no meio do download
                    self.wfile.flush()
                    return
                self.wfile.write(corpo)

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}/Instalador_SistemaALS_Setup.exe"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def parar(self):
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture
def servidor():
    criados = []

    def criar(**kwargs):
        s = _Servidor(**kwargs)
        criados.append(s)
        return s

    yield criar
    for s in criados:
        s.parar()


def _baixar(url, pasta, **kwargs):
    kwargs.setdefault("espera_base", 0)
    return UpdaterService.baixar_instalador_robusto(
        url, os.path.join(str(pasta), "Instalador_SistemaALS_Setup.exe"), **kwargs
    )


def test_download_completo_com_progresso(servidor, tmp_path):
    s = servidor()
    progresso = []
    ok, resultado = _baixar(s.url, tmp_path, progresso_callback=progresso.append, tamanho_esperado=len(CONTEUDO))
    assert ok is True
    assert open(resultado, "rb").read() == CONTEUDO
    assert progresso[-1] == 100
    assert not [f for f in os.listdir(tmp_path) if f.endswith(".part")]


def test_download_retoma_de_onde_parou_apos_queda_de_conexao(servidor, tmp_path):
    s = servidor(cortar_primeira=True)
    ok, resultado = _baixar(s.url, tmp_path, tamanho_esperado=len(CONTEUDO))
    assert ok is True
    assert open(resultado, "rb").read() == CONTEUDO
    assert len(s.requisicoes) == 2
    assert s.requisicoes[0] is None
    assert s.requisicoes[1] == f"bytes={len(CONTEUDO) // 2}-"  # retomou, não recomeçou


def test_http_404_falha_na_hora_com_mensagem_clara(servidor, tmp_path):
    s = servidor(status_fixo=404)
    ok, mensagem = _baixar(s.url, tmp_path)
    assert ok is False
    assert "HTTP 404" in mensagem
    assert len(s.requisicoes) == 1  # erro do cliente não adianta repetir


def test_servidor_indisponivel_tenta_de_novo_e_explica(servidor, tmp_path):
    s = servidor(status_fixo=503)
    ok, mensagem = _baixar(s.url, tmp_path, tentativas=2)
    assert ok is False
    assert len(s.requisicoes) == 2
    assert "indisponível" in mensagem and "2 tentativas" in mensagem


def test_conexao_recusada_aponta_problema_de_conexao(tmp_path):
    with socket.socket() as sk:
        sk.bind(("127.0.0.1", 0))
        porta = sk.getsockname()[1]
    ok, mensagem = _baixar(f"http://127.0.0.1:{porta}/x.exe", tmp_path, tentativas=2)
    assert ok is False
    assert "conexão" in mensagem.lower()
    assert "continua de onde parou" in mensagem


def test_download_incompleto_e_rejeitado(servidor, tmp_path):
    s = servidor()
    ok, mensagem = _baixar(s.url, tmp_path, tamanho_esperado=len(CONTEUDO) + 1000, tentativas=2)
    assert ok is False
    assert "incompleto" in mensagem.lower()


def test_instalador_antigo_em_uso_nao_impede_o_download(servidor, tmp_path, monkeypatch):
    """Antes, qualquer arquivo travado no destino virava 'verifique sua conexão' e repetir nunca resolvia"""
    destino = tmp_path / "Instalador_SistemaALS_Setup.exe"
    destino.write_bytes(b"instalador anterior ainda em execucao")
    remover_real = os.remove

    def remover(caminho, *a, **k):
        if os.path.abspath(caminho) == str(destino):
            raise PermissionError("em uso por outro processo")
        return remover_real(caminho, *a, **k)

    monkeypatch.setattr(os, "remove", remover)
    s = servidor()
    ok, resultado = _baixar(s.url, tmp_path)
    assert ok is True
    assert os.path.abspath(resultado) != str(destino)
    assert open(resultado, "rb").read() == CONTEUDO


def test_parcial_de_outra_versao_nunca_e_retomado(servidor, tmp_path):
    lixo = tmp_path / "Instalador_SistemaALS_Setup.exe.deadbeef.part"
    lixo.write_bytes(b"x" * 1000)  # restos de um download de outra versao
    s = servidor()
    ok, resultado = _baixar(s.url, tmp_path)
    assert ok is True
    assert open(resultado, "rb").read() == CONTEUDO
    assert s.requisicoes == [None]  # nao pediu Range
    assert not lixo.exists()


def test_wrapper_booleano_continua_funcionando(servidor, tmp_path):
    s = servidor()
    assert UpdaterService.baixar_instalador(s.url, str(tmp_path / "i.exe")) is True


# ------------------------------------------------------- instalação em andamento
@pytest.fixture
def pasta_update(tmp_path, monkeypatch):
    monkeypatch.setattr(updater_service, "pasta_atualizacao", lambda: str(tmp_path))
    return tmp_path


def _pid_encerrado():
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    return p.pid


def test_processo_ativo():
    assert processo_ativo(os.getpid()) is True
    assert processo_ativo(_pid_encerrado()) is False
    assert processo_ativo(0) is False


def test_instalacao_em_andamento_reconhece_instalador_vivo(pasta_update):
    UpdaterService.registrar_instalacao(os.getpid(), "v1.2.3", str(pasta_update / "i.log"))
    dados = UpdaterService.instalacao_em_andamento()
    assert dados["versao"] == "v1.2.3" and dados["pid"] == os.getpid()


def test_versao_nova_nao_espera_a_propria_instalacao_terminar(pasta_update):
    """O instalador abre o app novo enquanto ainda está finalizando: o novo não pode se encerrar por isso"""
    UpdaterService.registrar_instalacao(os.getpid(), "v1.2.3", "")
    assert UpdaterService.instalacao_em_andamento(versao_atual="1.2.3") is None
    assert not (pasta_update / updater_service.NOME_MARCADOR).exists()


def test_copia_antiga_espera_a_instalacao_da_versao_nova(pasta_update):
    UpdaterService.registrar_instalacao(os.getpid(), "v1.2.3", "")
    assert UpdaterService.instalacao_em_andamento(versao_atual="1.1.2") is not None


def test_marcador_de_instalador_morto_e_removido(pasta_update):
    UpdaterService.registrar_instalacao(_pid_encerrado(), "v1.2.3", "")
    assert UpdaterService.instalacao_em_andamento() is None
    assert not (pasta_update / updater_service.NOME_MARCADOR).exists()


def test_marcador_antigo_demais_e_ignorado(pasta_update):
    (pasta_update / updater_service.NOME_MARCADOR).write_text(
        json.dumps({"pid": os.getpid(), "versao": "v1", "inicio": time.time() - 3600, "log": ""})
    )
    assert UpdaterService.instalacao_em_andamento(max_minutos=15) is None


def test_marcador_corrompido_nao_derruba_o_app(pasta_update):
    (pasta_update / updater_service.NOME_MARCADOR).write_text("{isso nao e json")
    assert UpdaterService.instalacao_em_andamento() is None


def test_leitura_do_log_do_instalador(tmp_path):
    ok = tmp_path / "ok.log"
    ok.write_text("...\nInstallation process succeeded.\nLog closed.")
    falhou = tmp_path / "falhou.log"
    falhou.write_text("...\nSetup aborted\n")
    assert UpdaterService.instalacao_foi_concluida(str(ok)) is True
    assert UpdaterService.instalacao_foi_concluida(str(falhou)) is False
    assert UpdaterService.instalacao_foi_concluida(str(tmp_path / "nao_existe.log")) is None
