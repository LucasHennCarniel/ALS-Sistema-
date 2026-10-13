"""
Model de Manutenção refatorado com SQLAlchemy 2.0 ORM
Garante sessões atômicas, consultas tipadas e integridade referencial
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from src.config import DB_PATH
from src.models.database import get_db, init_db, get_engine
from src.models.entities import Manutencao


class ManutencaoModel:
    """Gerencia o acesso ao banco de dados para Registros de Manutenção via SQLAlchemy"""

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
            logging.error(f"Erro ao inicializar tabela manutenção via SQLAlchemy: {e}")
            return False

    def obter_todos(self) -> List[Dict[str, Any]]:
        """Retorna todos os registros ordenados por id descrescente"""
        try:
            with get_db(self.db_path) as session:
                stmt = select(Manutencao).order_by(Manutencao.id.desc())
                registros = session.scalars(stmt).all()
                return [m.to_dict() for m in registros]
        except Exception as e:
            logging.error(f"Erro ao obter manutenções: {e}")
            return []

    def obter_por_id(self, id_registro: int) -> Optional[Dict[str, Any]]:
        """Retorna um registro específico pelo ID"""
        try:
            with get_db(self.db_path) as session:
                m = session.get(Manutencao, int(id_registro))
                return m.to_dict() if m else None
        except Exception as e:
            logging.error(f"Erro ao obter manutenção por ID {id_registro}: {e}")
            return None

    def inserir(self, dados: Dict[str, Any]) -> Optional[int]:
        """Insere um novo registro de manutenção no banco via ORM"""
        try:
            with get_db(self.db_path) as session:
                novo = Manutencao(
                    data=str(dados.get('data') or ''),
                    placa=str(dados.get('placa') or '').strip().upper(),
                    km=float(dados.get('km') or 0.0),
                    veiculo=dados.get('veiculo'),
                    destino_programado=dados.get('destino_programado'),
                    servico_executar=dados.get('servico_executar'),
                    status=dados.get('status'),
                    data_entrada=dados.get('data_entrada'),
                    data_saida=dados.get('data_saida'),
                    total_dias_manutencao=int(dados.get('total_dias_manutencao') or 0),
                    nr_of=dados.get('nr_of'),
                    obs=dados.get('obs')
                )
                session.add(novo)
                session.flush()
                novo_id = novo.id
            return novo_id
        except Exception as e:
            logging.error(f"Erro ao inserir manutenção: {e}")
            return None

    def atualizar(self, id_registro: int, dados: Dict[str, Any]) -> bool:
        """Atualiza registro inteiro"""
        try:
            with get_db(self.db_path) as session:
                m = session.get(Manutencao, int(id_registro))
                if not m:
                    return False

                campos = [
                    'data', 'placa', 'km', 'veiculo', 'destino_programado',
                    'servico_executar', 'status', 'data_entrada', 'data_saida',
                    'total_dias_manutencao', 'nr_of', 'obs'
                ]
                for c in campos:
                    if c in dados:
                        val = dados[c]
                        if c == 'km':
                            val = float(val or 0.0)
                        elif c == 'total_dias_manutencao':
                            val = int(val or 0)
                        setattr(m, c, val)
            return True
        except Exception as e:
            logging.error(f"Erro ao atualizar manutenção: {e}")
            return False

    def deletar(self, id_registro: int) -> bool:
        """Exclui registro permanentemente"""
        try:
            with get_db(self.db_path) as session:
                m = session.get(Manutencao, int(id_registro))
                if m:
                    session.delete(m)
                    return True
                return False
        except Exception as e:
            logging.error(f"Erro ao deletar manutenção: {e}")
            return False

    def obter_por_placa_e_datas(self, placa: str, data: str, data_entrada: str) -> Optional[int]:
        """Busca ID de manutenção pela combinação de placa e datas"""
        try:
            with get_db(self.db_path) as session:
                stmt = select(Manutencao.id).where(
                    Manutencao.placa == placa.strip().upper(),
                    Manutencao.data == data.strip(),
                    Manutencao.data_entrada == data_entrada.strip()
                ).limit(1)
                return session.scalar(stmt)
        except Exception as e:
            logging.error(f"Erro ao buscar manutenção por placa e datas: {e}")
            return None

    def limpar_todos(self) -> bool:
        """Remove todos os registros de manutenção (usado no modo substituir)"""
        try:
            from sqlalchemy import delete
            with get_db(self.db_path) as session:
                session.execute(delete(Manutencao))
            return True
        except Exception as e:
            logging.error(f"Erro ao limpar manutenções: {e}")
            return False

