"""
Entidades ORM do SQLAlchemy 2.0 para o Sistema ALS
Mapeamento de Veículos, Manutenções, Destinos e Notas
"""
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.models.database import Base


class Veiculo(Base):
    __tablename__ = "veiculos"

    placa: Mapped[str] = mapped_column(String(20), primary_key=True)
    tipo_veiculo: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ultima_km: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    data_cadastro: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ativo: Mapped[int] = mapped_column(Integer, default=1, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "placa": self.placa,
            "tipo_veiculo": self.tipo_veiculo,
            "descricao": self.descricao,
            "ultima_km": self.ultima_km or 0,
            "data_cadastro": self.data_cadastro,
            "ativo": self.ativo if self.ativo is not None else 1
        }


class Manutencao(Base):
    __tablename__ = "manutencoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data: Mapped[str] = mapped_column(String(20), nullable=False)
    placa: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    km: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    veiculo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    destino_programado: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    servico_executar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    data_entrada: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    data_saida: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    total_dias_manutencao: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    nr_of: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    obs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "data": self.data,
            "placa": self.placa,
            "km": self.km if self.km is not None else 0.0,
            "veiculo": self.veiculo,
            "destino_programado": self.destino_programado,
            "servico_executar": self.servico_executar,
            "status": self.status,
            "data_entrada": self.data_entrada,
            "data_saida": self.data_saida,
            "total_dias_manutencao": self.total_dias_manutencao if self.total_dias_manutencao is not None else 0,
            "nr_of": self.nr_of,
            "obs": self.obs
        }


class Destino(Base):
    __tablename__ = "destinos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome_destino: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    data_cadastro: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ativo: Mapped[int] = mapped_column(Integer, default=1, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome_destino": self.nome_destino,
            "data_cadastro": self.data_cadastro,
            "ativo": self.ativo if self.ativo is not None else 1
        }


class Nota(Base):
    __tablename__ = "notas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data_programada: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    placa: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_criacao: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "data_programada": self.data_programada,
            "placa": self.placa,
            "status": self.status,
            "observacao": self.observacao,
            "data_criacao": self.data_criacao
        }
