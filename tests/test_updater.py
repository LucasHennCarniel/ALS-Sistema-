"""
Testes unitários do serviço de atualização (UpdaterService)
"""
import os
import pytest
from src.services.updater_service import parse_versao, versao_maior, UpdaterService


def test_parse_versao():
    assert parse_versao("1.0.0") == (1, 0, 0)
    assert parse_versao("v1.2.3") == (1, 2, 3)
    assert parse_versao("V2.10.5") == (2, 10, 5)
    assert parse_versao("1.0") == (1, 0)
    assert parse_versao("invalido") == (0,)


def test_versao_maior():
    assert versao_maior("1.0.1", "1.0.0") is True
    assert versao_maior("v1.1.0", "1.0.9") is True
    assert versao_maior("2.0.0", "1.99.99") is True
    assert versao_maior("1.0.0", "1.0.0") is False
    assert versao_maior("0.9.5", "1.0.0") is False


def test_backup_preventivo(tmp_path, monkeypatch):
    test_db = tmp_path / "data" / "sistema_als.db"
    test_backup = tmp_path / "backup"
    test_db.parent.mkdir(parents=True, exist_ok=True)
    test_db.write_text("conteudo sqlite de teste", encoding="utf-8")

    monkeypatch.setattr("src.services.updater_service.DB_PATH", str(test_db))
    monkeypatch.setattr("src.services.updater_service.BACKUP_DIR", str(test_backup))

    backup_gerado = UpdaterService.fazer_backup_preventivo()
    assert backup_gerado is not None
    assert os.path.exists(backup_gerado)
    with open(backup_gerado, "r", encoding="utf-8") as f:
        assert f.read() == "conteudo sqlite de teste"
