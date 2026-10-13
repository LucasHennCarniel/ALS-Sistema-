import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Testaremos as novas classes
from src.models.veiculo_model import VeiculoModel
from src.controllers.veiculo_controller import VeiculoController

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        try:
            os.remove(path)
        except PermissionError:
            pass

@pytest.fixture
def controller(temp_db):
    model = VeiculoModel(db_path=temp_db)
    controller = VeiculoController(model=model)
    yield controller
    if model.conn:
        model.conn.close()

def test_adicionar_veiculo(controller):
    sucesso, msg = controller.adicionar_veiculo("CAVALO", "ABC1234", "Descricao 1", 1000)
    assert sucesso is True
    
    veiculo = controller.obter_veiculo_por_placa("ABC1234")
    assert veiculo is not None
    assert veiculo['tipo_veiculo'] == "CAVALO"
    assert veiculo['ultima_km'] == 1000

def test_adicionar_veiculo_duplicado(controller):
    controller.adicionar_veiculo("CAVALO", "ABC1234", "Descricao 1", 1000)
    sucesso, msg = controller.adicionar_veiculo("CARRETA 1", "abc1234", "Outra", 0)
    assert sucesso is False

def test_atualizar_km(controller):
    controller.adicionar_veiculo("CAVALO", "XYZ9876", "", 500)
    controller.atualizar_km("XYZ9876", 1200)
    
    veiculo = controller.obter_veiculo_por_placa("XYZ9876")
    assert veiculo['ultima_km'] == 1200

def test_obter_veiculos_ativos(controller):
    controller.adicionar_veiculo("CAVALO", "AAA1111")
    controller.adicionar_veiculo("CARRETA 1", "BBB2222", "Teste")
    
    ativos = controller.obter_veiculos_ativos_formatado()
    assert len(ativos) == 2
    assert "AAA1111 - CAVALO" in ativos
    assert "BBB2222 - CARRETA 1 - Teste" in ativos
    
def test_excluir_veiculo(controller):
    controller.adicionar_veiculo("CAVALO", "CCC3333")
    
    # Exclusão agora usa a Placa e não o Indice do Pandas!
    sucesso, msg = controller.excluir_veiculo("CCC3333")
    assert sucesso is True
    
    veiculo = controller.obter_veiculo_por_placa("CCC3333")
    assert veiculo is None

def test_extrair_placa(controller):
    placa = controller.extrair_placa_da_selecao("ABC1234 - CAVALO - Desc")
    assert placa == "ABC1234"

