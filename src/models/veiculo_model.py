import sqlite3
from datetime import datetime
from src.config import DB_PATH
import logging

class VeiculoModel:
    """
    Gerencia o cadastro de veículos da frota no SQLite
    """
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.conectar()
        self.criar_tabela()
    
    def conectar(self):
        """Conecta ao banco SQLite e configura para retornar dicionários"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA journal_mode=WAL;")
            return True
        except Exception as e:
            logging.error(f"Erro ao conectar no banco Veículos: {e}")
            return False
            
    def criar_tabela(self):
        """Cria tabela de veículos se não existir"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS veiculos (
                    placa TEXT PRIMARY KEY,
                    tipo_veiculo TEXT NOT NULL,
                    descricao TEXT,
                    ultima_km INTEGER DEFAULT 0,
                    data_cadastro TEXT,
                    ativo INTEGER DEFAULT 1
                )
            """)
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Erro ao criar tabela veículos: {e}")
            return False

    def obter_todos(self):
        """Retorna todos os veículos ordenados por placa"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM veiculos ORDER BY placa")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Erro ao obter veículos: {e}")
            return []
            
    def obter_ativos(self):
        """Retorna veículos ativos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM veiculos WHERE ativo = 1 ORDER BY placa")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Erro ao obter veículos ativos: {e}")
            return []
            
    def obter_por_placa(self, placa):
        """Retorna dados de um veículo pela placa"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM veiculos WHERE UPPER(TRIM(placa)) = ?", (placa.strip().upper(),))
        row = cursor.fetchone()
        return dict(row) if row else None
        
    def inserir(self, tipo, placa, descricao='', km_inicial=0):
        """Adiciona novo veículo"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO veiculos (placa, tipo_veiculo, descricao, ultima_km, data_cadastro, ativo)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (placa.strip().upper(), tipo.strip().upper(), descricao.strip() if descricao else None, int(float(km_inicial or 0)), datetime.now().strftime('%d/%m/%Y')))
        self.conn.commit()
        return True
        
    def atualizar(self, placa_antiga, tipo, nova_placa, descricao, ativo, ultima_km=None):
        """Atualiza dados de um veículo (incluindo KM se fornecida)"""
        cursor = self.conn.cursor()
        if ultima_km is not None:
            cursor.execute("""
                UPDATE veiculos 
                SET tipo_veiculo = ?, placa = ?, descricao = ?, ativo = ?, ultima_km = ?
                WHERE UPPER(TRIM(placa)) = ?
            """, (tipo.strip().upper(), nova_placa.strip().upper(), descricao if descricao else None, 1 if ativo else 0, int(float(ultima_km)), placa_antiga.strip().upper()))
        else:
            cursor.execute("""
                UPDATE veiculos 
                SET tipo_veiculo = ?, placa = ?, descricao = ?, ativo = ?
                WHERE UPPER(TRIM(placa)) = ?
            """, (tipo.strip().upper(), nova_placa.strip().upper(), descricao if descricao else None, 1 if ativo else 0, placa_antiga.strip().upper()))
        self.conn.commit()
        return cursor.rowcount > 0
        
    def atualizar_km(self, placa, nova_km):
        """Atualiza a KM de um veículo"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE veiculos SET ultima_km = ? WHERE UPPER(TRIM(placa)) = ?", 
                     (int(float(nova_km)), placa.strip().upper()))
        self.conn.commit()
        return cursor.rowcount > 0
        
    def desativar(self, placa):
        """Desativa um veículo"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE veiculos SET ativo = 0 WHERE UPPER(TRIM(placa)) = ?", (placa.strip().upper(),))
        self.conn.commit()
        return cursor.rowcount > 0

    def deletar(self, placa):
        """Exclui permanentemente um veículo pela placa"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM veiculos WHERE UPPER(TRIM(placa)) = ?", (placa.strip().upper(),))
        self.conn.commit()
        return cursor.rowcount > 0

    def obter_estatisticas(self):
        """Retorna estatísticas do cadastro"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM veiculos WHERE ativo = 1")
            ativos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM veiculos")
            total = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT tipo_veiculo, COUNT(*) 
                FROM veiculos 
                WHERE ativo = 1 
                GROUP BY tipo_veiculo 
                ORDER BY COUNT(*) DESC
            """)
            por_tipo = dict(cursor.fetchall())
            
            return {
                'total': total,
                'ativos': ativos,
                'inativos': total - ativos,
                'por_tipo': por_tipo
            }
        except Exception as e:
            logging.error(f"Erro ao obter estatísticas: {e}")
            return {'total': 0, 'ativos': 0, 'inativos': 0, 'por_tipo': {}}
