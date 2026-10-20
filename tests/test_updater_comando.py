from src.services.updater_service import UpdaterService


def test_comando_instala_na_pasta_do_exe_com_aspas_no_valor():
    cmd = UpdaterService.montar_comando_instalador(
        r"C:\Users\A B\Temp\ALS_Update\Instalador_SistemaALS_Setup.exe",
        r"C:\Sistema ALS",
        r"C:\Users\A B\Temp\ALS_Update\instalador.log",
    )
    assert cmd.startswith(r'"C:\Users\A B\Temp\ALS_Update\Instalador_SistemaALS_Setup.exe" /SILENT')
    assert r'/DIR="C:\Sistema ALS"' in cmd
    assert r'/LOG="C:\Users\A B\Temp\ALS_Update\instalador.log"' in cmd


def test_comando_remove_barra_final_que_quebraria_as_aspas():
    cmd = UpdaterService.montar_comando_instalador(r"C:\i.exe", "C:\\Sistema ALS\\", r"C:\l.log")
    assert r'/DIR="C:\Sistema ALS"' in cmd


def test_comando_sem_pasta_nao_forca_diretorio():
    cmd = UpdaterService.montar_comando_instalador(r"C:\i.exe", None, r"C:\l.log")
    assert "/DIR" not in cmd
