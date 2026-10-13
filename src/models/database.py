"""
Módulo Central de Banco de Dados com SQLAlchemy 2.0
Gerencia Engine, Sessões ORM, Pool e Configurações de Integridade SQLite (WAL)
"""
import os
from contextlib import contextmanager
from typing import Dict, Generator
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from src.config import DB_PATH


class Base(DeclarativeBase):
    """Classe base declarativa para todas as entidades ORM"""
    pass


# Cache de engines e sessionmakers por caminho de banco (essencial para testes com temp_db)
_engines: Dict[str, Engine] = {}
_sessionmakers: Dict[str, sessionmaker] = {}


def get_engine(db_path: str = None) -> Engine:
    """Retorna uma Engine SQLAlchemy configurada com SQLite WAL e timeout"""
    caminho = db_path or DB_PATH
    caminho_abs = os.path.abspath(caminho)

    if caminho_abs not in _engines:
        os.makedirs(os.path.dirname(caminho_abs), exist_ok=True)
        engine = create_engine(
            f"sqlite:///{caminho_abs}",
            echo=False,
            future=True,
            connect_args={"timeout": 15, "check_same_thread": False}
        )

        @event.listens_for(engine, "connect")
        def _configurar_sqlite_pragmas(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        _engines[caminho_abs] = engine

    return _engines[caminho_abs]


def get_session_factory(db_path: str = None) -> sessionmaker:
    """Retorna o sessionmaker associado ao banco de dados especificado"""
    caminho = db_path or DB_PATH
    caminho_abs = os.path.abspath(caminho)

    if caminho_abs not in _sessionmakers:
        engine = get_engine(caminho_abs)
        _sessionmakers[caminho_abs] = sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
            class_=Session
        )

    return _sessionmakers[caminho_abs]


@contextmanager
def get_db(db_path: str = None) -> Generator[Session, None, None]:
    """
    Context manager transacional para sessões SQLAlchemy.
    Garante commit em caso de sucesso e rollback em caso de falha.
    """
    factory = get_session_factory(db_path)
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(db_path: str = None):
    """Cria todas as tabelas declaradas se ainda não existirem"""
    # Importa entidades para registrar no metadata do Base
    import src.models.entities  # noqa
    engine = get_engine(db_path)
    Base.metadata.create_all(bind=engine)
