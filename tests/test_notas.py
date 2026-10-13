import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.nota_model import NotaModel
from src.controllers.nota_controller import NotaController


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
    model = NotaModel(db_path=temp_db)
    controller = NotaController(model=model)
    yield controller


def test_adicionar_e_obter_nota(controller):
    dados = {
        'data_programada': '15/10/2026',
        'placa': 'ABC1D23',
        'status': 'PENDENTE',
        'observacao': 'Revisão dos freios traseiros'
    }
    sucesso, msg = controller.adicionar_nota(dados)
    assert sucesso is True

    notas = controller.obter_todas()
    assert len(notas) == 1
    assert notas[0]['placa'] == 'ABC1D23'
    assert notas[0]['status'] == 'PENDENTE'
    assert notas[0]['observacao'] == 'Revisão dos freios traseiros'


def test_ordenacao_cronologica_real(controller):
    """Garante que a ordenação respeite ano e mês reais no formato dd/mm/aaaa"""
    controller.adicionar_nota({'data_programada': '01/12/2026', 'placa': 'NOTA_RECENTE'})
    controller.adicionar_nota({'data_programada': '31/01/2020', 'placa': 'NOTA_ANTIGA'})

    notas = controller.obter_todas()
    assert len(notas) == 2
    # 01/12/2026 deve vir antes de 31/01/2020 mesmo 01 < 31
    assert notas[0]['placa'] == 'NOTA_RECENTE'
    assert notas[1]['placa'] == 'NOTA_ANTIGA'


def test_atualizar_nota(controller):
    controller.adicionar_nota({'data_programada': '10/10/2026', 'placa': 'XYZ9876', 'status': 'PENDENTE'})
    notas = controller.obter_todas()
    id_nota = notas[0]['id']

    sucesso, msg = controller.atualizar_nota(id_nota, {
        'data_programada': '11/10/2026',
        'placa': 'XYZ9876',
        'status': 'CONCLUÍDO',
        'observacao': 'Serviço finalizado com sucesso'
    })
    assert sucesso is True

    nota_atualizada = controller.obter_por_id(id_nota)
    assert nota_atualizada['status'] == 'CONCLUÍDO'
    assert nota_atualizada['data_programada'] == '11/10/2026'


def test_excluir_nota(controller):
    controller.adicionar_nota({'data_programada': '10/10/2026', 'placa': 'DEL9999'})
    notas = controller.obter_todas()
    assert len(notas) == 1

    sucesso, msg = controller.excluir_nota(notas[0]['id'])
    assert sucesso is True
    assert len(controller.obter_todas()) == 0
