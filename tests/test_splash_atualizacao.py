"""
Testes do fluxo de atualização na janela única: a interface nunca deve ficar muda ou congelada
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from src.services.updater_service import UpdateInfo, UpdaterService
from src.views_qt import splash_screen
from src.views_qt.splash_screen import ModernSplashScreen


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


class _Processo:
    def __init__(self, codigo=None, pid=1234):
        self._codigo = codigo
        self.pid = pid

    def poll(self):
        return self._codigo


@pytest.fixture
def janela(app, monkeypatch):
    """Janela já no aviso de nova versão, sem rede e sem encerrar o processo de teste"""
    saidas = []
    monkeypatch.setattr(UpdaterService, "finalizar_para_instalacao", staticmethod(lambda: saidas.append("saiu")))
    monkeypatch.setattr(UpdaterService, "limpar_marcador_instalacao", staticmethod(lambda: saidas.append("limpou")))
    info = UpdateInfo(True, "v9.9.9", False, "http://x/y.exe", "notas", 10)
    w = ModernSplashScreen(update_info=info)
    w._caminho_instalador = r"C:\temp\Instalador_SistemaALS_Setup.exe"
    w.saidas = saidas
    yield w
    w.close()


def test_instalador_que_nao_inicia_mostra_o_motivo_e_opcoes(janela, monkeypatch):
    def falha(*a, **k):
        raise PermissionError("Acesso negado")

    monkeypatch.setattr(UpdaterService, "iniciar_instalador", staticmethod(falha))
    janela._iniciar_instalador()
    assert "Não foi possível iniciar o instalador" in janela.lbl_status.text()
    assert "Acesso negado" in janela.lbl_status.text()
    assert not janela.linha_erro.isHidden()
    assert janela.saidas == []  # não encerrou o app


def test_instalador_com_erro_de_saida_mostra_codigo_e_log(janela, tmp_path, monkeypatch):
    log = tmp_path / "instalador.log"
    monkeypatch.setattr(UpdaterService, "iniciar_instalador",
                        staticmethod(lambda *a, **k: (_Processo(codigo=5), str(log))))
    janela._iniciar_instalador()
    janela._monitorar_instalador()
    assert "código 5" in janela.lbl_status.text()
    assert str(log) in janela.lbl_status.text()
    assert not janela.linha_erro.isHidden()
    assert "saiu" not in janela.saidas
    assert "limpou" in janela.saidas  # o marcador não deixa o próximo start esperando à toa


def test_so_encerra_o_app_depois_que_o_instalador_realmente_iniciou(janela, tmp_path, monkeypatch):
    log = tmp_path / "instalador.log"
    monkeypatch.setattr(UpdaterService, "iniciar_instalador",
                        staticmethod(lambda *a, **k: (_Processo(codigo=None), str(log))))
    janela._iniciar_instalador()

    janela._monitorar_instalador()  # processo vivo, mas ainda sem log: o antivírus pode estar escaneando
    assert "Aguardando o instalador iniciar" in janela.lbl_status.text()
    QTest.qWait(1700)
    assert "saiu" not in janela.saidas

    log.write_text("Setup version 6.x\n")  # o instalador começou a trabalhar
    janela._monitorar_instalador()
    assert "Instalando a atualização" in janela.lbl_status.text()
    QTest.qWait(1800)
    assert "saiu" in janela.saidas


def test_instalador_que_nunca_inicia_vira_erro_apos_o_tempo_limite(janela, tmp_path, monkeypatch):
    monkeypatch.setattr(UpdaterService, "iniciar_instalador",
                        staticmethod(lambda *a, **k: (_Processo(codigo=None), str(tmp_path / "nao_existe.log"))))
    janela._iniciar_instalador()
    janela._tempo_instalador = splash_screen.TIMEOUT_INICIO_INSTALADOR_MS - splash_screen.INTERVALO_MONITOR_MS
    janela._monitorar_instalador()
    assert "não iniciou em 3 minutos" in janela.lbl_status.text()
    assert not janela.linha_erro.isHidden()


def test_tentar_novamente_repete_a_ultima_etapa(janela, monkeypatch):
    chamadas = []
    monkeypatch.setattr(UpdaterService, "iniciar_instalador",
                        staticmethod(lambda *a, **k: chamadas.append(1) or (_ for _ in ()).throw(OSError("x"))))
    janela._iniciar_instalador()
    janela._tentar_novamente()
    assert len(chamadas) == 2


def test_falha_de_download_mostra_a_mensagem_especifica(janela):
    janela._on_download_falha("Falha de conexão com o GitHub: timed out.")
    assert "timed out" in janela.lbl_status.text()
    assert not janela.linha_erro.isHidden()


# --------------------------------------------- reabrir o app durante uma instalação
@pytest.fixture
def janela_com_instalacao_pendente(app, monkeypatch):
    estado = {"saidas": [], "checagens": 0}
    monkeypatch.setattr(UpdaterService, "instalacao_em_andamento",
                        staticmethod(lambda *a, **k: estado.get("dados")))
    monkeypatch.setattr(UpdaterService, "limpar_marcador_instalacao", staticmethod(lambda: None))
    monkeypatch.setattr(UpdaterService, "finalizar_para_instalacao",
                        staticmethod(lambda: estado["saidas"].append("saiu")))
    monkeypatch.setattr(ModernSplashScreen, "_iniciar_checagem",
                        lambda self: estado.__setitem__("checagens", estado["checagens"] + 1))
    estado["dados"] = {"pid": 4321, "versao": "v9.9.9", "log": "x.log"}
    w = ModernSplashScreen()
    w.estado = estado
    yield w
    w.close()


def test_nao_abre_o_app_no_meio_da_instalacao(janela_com_instalacao_pendente):
    w = janela_com_instalacao_pendente
    assert "sendo instalada" in w.lbl_status.text()
    assert w.estado["checagens"] == 0  # esperou em vez de seguir o fluxo normal
    assert w.timer_espera.isActive()


def test_instalacao_concluida_fecha_a_copia_antiga(janela_com_instalacao_pendente, monkeypatch):
    w = janela_com_instalacao_pendente
    w.estado["dados"] = None  # o instalador terminou
    monkeypatch.setattr(UpdaterService, "instalacao_foi_concluida", staticmethod(lambda log: True))
    w._verificar_instalacao()
    assert "Atualização concluída" in w.lbl_status.text()
    QTest.qWait(1800)
    assert w.estado["saidas"] == ["saiu"]
    assert w.estado["checagens"] == 0


def test_instalacao_que_falhou_segue_o_fluxo_normal(janela_com_instalacao_pendente, monkeypatch):
    w = janela_com_instalacao_pendente
    w.estado["dados"] = None
    monkeypatch.setattr(UpdaterService, "instalacao_foi_concluida", staticmethod(lambda log: False))
    w._verificar_instalacao()
    assert w.estado["checagens"] == 1  # abre normalmente e volta a oferecer a atualização
    assert w.estado["saidas"] == []
