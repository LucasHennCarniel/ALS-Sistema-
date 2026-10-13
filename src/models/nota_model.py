"""
Model de Anotações refatorado com SQLAlchemy 2.0 ORM
Garante sessões atômicas, consultas tipadas e ordenação cronológica real
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func
from src.config import DB_PATH
from src.models.database import get_db, init_db, get_engine
from src.models.entities import Nota


class NotaModel:
    """Gerencia as anotações e lembretes da frota via SQLAlchemy ORM"""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.criar_tabela()

    @property
    def conn(self):
        """Conexão bruta para compatibilidade legada"""
        return get_engine(self.db_path).raw_connection()

    def conectar(self):
        return True

    def criar_tabela(self):
        try:
            init_db(self.db_path)
            return True
        except Exception as e:
            logging.error(f"Erro ao inicializar tabela notas via SQLAlchemy: {e}")
            return False

    def obter_todas(self) -> List[Dict[str, Any]]:
        """
        Retorna todas as notas com ordenação cronológica real (Ano-Mês-Dia)
        Resolvendo a fragilidade de ordenação alfabética por dia no formato dd/mm/aaaa
        """
        try:
            with get_db(self.db_path) as session:
                # Expressão SQL para ordenar data dd/mm/aaaa em formato ISO yyyymmdd
                ordem_data = func.concat(
                    func.substr(Nota.data_programada, 7, 4),
                    func.substr(Nota.data_programada, 4, 2),
                    func.substr(Nota.data_programada, 1, 2)
                )
                stmt = select(Nota).order_by(ordem_data.desc(), Nota.id.desc())
                notas = session.scalars(stmt).all()
                return [n.to_dict() for n in notas]
        except Exception as e:
            logging.error(f"Erro ao obter notas: {e}")
            return []

    def obter_por_id(self, id_nota: int) -> Optional[Dict[str, Any]]:
        """Retorna uma anotação específica pelo ID"""
        try:
            with get_db(self.db_path) as session:
                n = session.get(Nota, int(id_nota))
                return n.to_dict() if n else None
        except Exception as e:
            logging.error(f"Erro ao obter nota por ID {id_nota}: {e}")
            return None

    def inserir(self, dados: Dict[str, Any]) -> Optional[int]:
        """Insere uma nova anotação via ORM"""
        try:
            with get_db(self.db_path) as session:
                nova = Nota(
                    data_programada=str(dados.get('data_programada') or '').strip(),
                    placa=str(dados.get('placa') or '').strip().upper(),
                    status=str(dados.get('status') or 'PENDENTE').strip(),
                    observacao=dados.get('observacao') or '',
                    data_criacao=dados.get('data_criacao')
                )
                session.add(nova)
                session.flush()
                nova_id = nova.id
            return nova_id
        except Exception as e:
            logging.error(f"Erro ao inserir nota: {e}")
            return None

    def atualizar(self, id_nota: int, dados: Dict[str, Any]) -> bool:
        """Atualiza uma anotação existente"""
        try:
            with get_db(self.db_path) as session:
                n = session.get(Nota, int(id_nota))
                if not n:
                    return False
                if 'data_programada' in dados:
                    n.data_programada = str(dados['data_programada']).strip()
                if 'placa' in dados:
                    n.placa = str(dados['placa']).strip().upper()
                if 'status' in dados:
                    n.status = str(dados['status']).strip()
                if 'observacao' in dados:
                    n.observacao = str(dados['observacao'])
            return True
        except Exception as e:
            logging.error(f"Erro ao atualizar nota: {e}")
            return False

    def deletar(self, id_nota: int) -> bool:
        """Exclui uma anotação permanentemente"""
        try:
            with get_db(self.db_path) as session:
                n = session.get(Nota, int(id_nota))
                if n:
                    session.delete(n)
                    return True
                return False
        except Exception as e:
            logging.error(f"Erro ao deletar nota: {e}")
            return False
