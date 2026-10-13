"""
Model de Veículos refatorado com SQLAlchemy 2.0 ORM
Garante sessões atômicas, consultas tipadas e integridade referencial
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func
from src.config import DB_PATH
from src.models.database import get_db, init_db, get_engine
from src.models.entities import Veiculo


class VeiculoModel:
    """Gerencia o acesso aos Veículos da frota via SQLAlchemy ORM"""

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
            logging.error(f"Erro ao inicializar tabela veículos via SQLAlchemy: {e}")
            return False

    def obter_todos(self) -> List[Dict[str, Any]]:
        """Retorna todos os veículos ordenados por placa"""
        try:
            with get_db(self.db_path) as session:
                stmt = select(Veiculo).order_by(Veiculo.placa)
                veiculos = session.scalars(stmt).all()
                return [v.to_dict() for v in veiculos]
        except Exception as e:
            logging.error(f"Erro ao obter veículos: {e}")
            return []

    def obter_ativos(self) -> List[Dict[str, Any]]:
        """Retorna veículos ativos ordenados por placa"""
        try:
            with get_db(self.db_path) as session:
                stmt = select(Veiculo).where(Veiculo.ativo == 1).order_by(Veiculo.placa)
                veiculos = session.scalars(stmt).all()
                return [v.to_dict() for v in veiculos]
        except Exception as e:
            logging.error(f"Erro ao obter veículos ativos: {e}")
            return []

    def obter_por_placa(self, placa: str) -> Optional[Dict[str, Any]]:
        """Retorna dados de um veículo pela placa"""
        if not placa:
            return None
        try:
            with get_db(self.db_path) as session:
                v = session.get(Veiculo, placa.strip().upper())
                return v.to_dict() if v else None
        except Exception as e:
            logging.error(f"Erro ao obter veículo por placa: {e}")
            return None

    def inserir(self, tipo: str, placa: str, descricao: str = '', km_inicial: float = 0) -> bool:
        """Adiciona novo veículo via ORM"""
        try:
            with get_db(self.db_path) as session:
                novo = Veiculo(
                    placa=placa.strip().upper(),
                    tipo_veiculo=tipo.strip().upper(),
                    descricao=descricao.strip() if descricao else None,
                    ultima_km=int(float(km_inicial or 0)),
                    data_cadastro=datetime.now().strftime('%d/%m/%Y'),
                    ativo=1
                )
                session.add(novo)
            return True
        except Exception as e:
            logging.error(f"Erro ao inserir veículo: {e}")
            raise

    def atualizar(self, placa_antiga: str, tipo: str, nova_placa: str, descricao: str, ativo: bool, ultima_km: Optional[float] = None) -> bool:
        """Atualiza dados do veículo"""
        try:
            with get_db(self.db_path) as session:
                v = session.get(Veiculo, placa_antiga.strip().upper())
                if not v:
                    return False

                placa_antiga_fmt = placa_antiga.strip().upper()
                nova_placa_fmt = nova_placa.strip().upper()

                if nova_placa_fmt != placa_antiga_fmt:
                    km_final = int(float(ultima_km if ultima_km is not None else (v.ultima_km or 0)))
                    data_cad = v.data_cadastro
                    session.delete(v)
                    session.flush()

                    substituto = Veiculo(
                        placa=nova_placa_fmt,
                        tipo_veiculo=tipo.strip().upper(),
                        descricao=descricao.strip() if descricao else None,
                        ultima_km=km_final,
                        data_cadastro=data_cad,
                        ativo=1 if ativo else 0
                    )
                    session.add(substituto)
                else:
                    v.tipo_veiculo = tipo.strip().upper()
                    v.descricao = descricao.strip() if descricao else None
                    v.ativo = 1 if ativo else 0
                    if ultima_km is not None:
                        v.ultima_km = int(float(ultima_km))
            return True
        except Exception as e:
            logging.error(f"Erro ao atualizar veículo: {e}")
            return False

    def atualizar_km(self, placa: str, nova_km: float) -> bool:
        """Atualiza o KM do veículo"""
        try:
            with get_db(self.db_path) as session:
                v = session.get(Veiculo, placa.strip().upper())
                if v:
                    v.ultima_km = int(float(nova_km))
                    return True
                return False
        except Exception as e:
            logging.error(f"Erro ao atualizar KM: {e}")
            return False

    def desativar(self, placa: str) -> bool:
        """Desativa logicamente o veículo"""
        try:
            with get_db(self.db_path) as session:
                v = session.get(Veiculo, placa.strip().upper())
                if v:
                    v.ativo = 0
                    return True
                return False
        except Exception as e:
            logging.error(f"Erro ao desativar veículo: {e}")
            return False

    def deletar(self, placa: str) -> bool:
        """Exclui permanentemente o veículo pela placa"""
        try:
            with get_db(self.db_path) as session:
                v = session.get(Veiculo, placa.strip().upper())
                if v:
                    session.delete(v)
                    return True
                return False
        except Exception as e:
            logging.error(f"Erro ao deletar veículo: {e}")
            return False

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna métricas agregadas da frota"""
        try:
            with get_db(self.db_path) as session:
                total = session.scalar(select(func.count(Veiculo.placa))) or 0
                ativos = session.scalar(select(func.count(Veiculo.placa)).where(Veiculo.ativo == 1)) or 0
                stmt = (
                    select(Veiculo.tipo_veiculo, func.count(Veiculo.placa))
                    .where(Veiculo.ativo == 1)
                    .group_by(Veiculo.tipo_veiculo)
                    .order_by(func.count(Veiculo.placa).desc())
                )
                por_tipo = dict(session.execute(stmt).all())
                return {
                    'total': total,
                    'ativos': ativos,
                    'inativos': total - ativos,
                    'por_tipo': por_tipo
                }
        except Exception as e:
            logging.error(f"Erro ao obter estatísticas de veículos: {e}")
            return {'total': 0, 'ativos': 0, 'inativos': 0, 'por_tipo': {}}
