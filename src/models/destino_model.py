"""
Model de Destinos refatorado com SQLAlchemy 2.0 ORM
Garante integridade única, sessões atômicas e consultas tipadas
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func
from src.config import DB_PATH
from src.models.database import get_db, init_db, get_engine
from src.models.entities import Destino


class DestinoModel:
    """Gerencia o cadastro de destinos de manutenção no SQLite via SQLAlchemy ORM"""

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
            logging.error(f"Erro ao inicializar tabela destinos via SQLAlchemy: {e}")
            return False

    def obter_todos(self) -> List[Dict[str, Any]]:
        """Retorna todos os destinos ordenados por nome"""
        try:
            with get_db(self.db_path) as session:
                stmt = select(Destino).order_by(Destino.nome_destino)
                destinos = session.scalars(stmt).all()
                return [d.to_dict() for d in destinos]
        except Exception as e:
            logging.error(f"Erro ao obter destinos: {e}")
            return []

    def obter_ativos(self) -> List[Dict[str, Any]]:
        """Retorna apenas os destinos ativos"""
        try:
            with get_db(self.db_path) as session:
                stmt = select(Destino).where(Destino.ativo == 1).order_by(Destino.nome_destino)
                destinos = session.scalars(stmt).all()
                return [d.to_dict() for d in destinos]
        except Exception as e:
            logging.error(f"Erro ao obter destinos ativos: {e}")
            return []

    def obter_por_nome(self, nome: str) -> Optional[Dict[str, Any]]:
        """Busca destino pelo nome exato (case-insensitive)"""
        if not nome:
            return None
        try:
            with get_db(self.db_path) as session:
                stmt = select(Destino).where(func.upper(Destino.nome_destino) == nome.strip().upper()).limit(1)
                d = session.scalars(stmt).first()
                return d.to_dict() if d else None
        except Exception as e:
            logging.error(f"Erro ao buscar destino por nome: {e}")
            return None

    def inserir(self, nome: str) -> Optional[int]:
        """Insere um novo destino"""
        try:
            with get_db(self.db_path) as session:
                novo = Destino(
                    nome_destino=nome.strip().upper(),
                    data_cadastro=datetime.now().strftime('%d/%m/%Y'),
                    ativo=1
                )
                session.add(novo)
                session.flush()
                novo_id = novo.id
            return novo_id
        except Exception as e:
            logging.error(f"Erro ao inserir destino: {e}")
            raise

    def atualizar(self, id_destino: int, nome: str, ativo: bool) -> bool:
        """Atualiza nome e status do destino pelo ID"""
        try:
            with get_db(self.db_path) as session:
                d = session.get(Destino, int(id_destino))
                if not d:
                    return False
                d.nome_destino = nome.strip().upper()
                d.ativo = 1 if ativo else 0
            return True
        except Exception as e:
            logging.error(f"Erro ao atualizar destino: {e}")
            return False

    def desativar(self, id_destino: int) -> bool:
        """Marca destino como inativo (exclusão lógica)"""
        try:
            with get_db(self.db_path) as session:
                d = session.get(Destino, int(id_destino))
                if not d:
                    return False
                d.ativo = 0
            return True
        except Exception as e:
            logging.error(f"Erro ao desativar destino: {e}")
            return False

    def deletar(self, id_destino: int) -> bool:
        """Exclui permanentemente o destino"""
        try:
            with get_db(self.db_path) as session:
                d = session.get(Destino, int(id_destino))
                if d:
                    session.delete(d)
                    return True
                return False
        except Exception as e:
            logging.error(f"Erro ao deletar destino: {e}")
            return False
