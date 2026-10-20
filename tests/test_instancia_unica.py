import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QLockFile

from src.app_qt import _pid_da_instancia_aberta


def test_segunda_instancia_e_barrada_e_o_dono_e_identificado(tmp_path):
    caminho = str(tmp_path / "instancia.lock")
    primeira, segunda = QLockFile(caminho), QLockFile(caminho)
    primeira.setStaleLockTime(0)
    segunda.setStaleLockTime(0)
    assert primeira.tryLock(100) is True
    assert segunda.tryLock(100) is False
    assert _pid_da_instancia_aberta(segunda) == os.getpid()
    primeira.unlock()
    assert segunda.tryLock(100) is True  # liberou: a próxima abertura funciona
    segunda.unlock()


def test_pid_indisponivel_nao_derruba_o_app():
    class SemInfo:
        def getLockInfo(self):
            raise RuntimeError("sem informacao")

    assert _pid_da_instancia_aberta(SemInfo()) is None
