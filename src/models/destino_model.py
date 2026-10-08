import sqlite3
import os
from datetime import datetime
from src.config import DB_PATH

class DestinoModel:
    """
    Gerencia o cadastro de destinos de manutenção no SQLite
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
            self.conn.execute("PRAGMA journal_mode=WAL;") # Retorna dicionarios ao invez de tuplas
            return True
        except Exception as e:
            import logging
            logging.error(f"Erro ao conectar no banco Destinos: {e}")
            return False
    
    def criar_tabela(self):
        """Cria tabela de destinos se não existir"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS destinos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_destino TEXT NOT NULL UNIQUE,
                    data_cadastro TEXT,
                    ativo INTEGER DEFAULT 1
                )
            """)
            self.conn.commit()
            return True
        except Exception as e:
            import logging
            logging.error(f"Erro ao criar tabela destinos: {e}")
            return False
    
    def obter_todos(self):
        """Retorna todos os destinos ordenados por nome"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM destinos ORDER BY nome_destino")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            import logging
            logging.error(f"Erro ao obter destinos: {e}")
            return []
            
    def obter_ativos(self):
        """Retorna apenas os destinos ativos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM destinos WHERE ativo = 1 ORDER BY nome_destino")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            import logging
            logging.error(f"Erro ao obter destinos ativos: {e}")
            return []
            
    def obter_por_nome(self, nome):
        """Busca destino pelo nome exato (case-insensitive)"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM destinos WHERE UPPER(nome_destino) = ?", (nome.upper(),))
        row = cursor.fetchone()
        return dict(row) if row else None
            
    def inserir(self, nome):
        """Insere um novo destino"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO destinos (nome_destino, data_cadastro, ativo)
            VALUES (?, ?, 1)
        """, (nome.upper(), datetime.now().strftime('%d/%m/%Y')))
        self.conn.commit()
        return cursor.lastrowid
        
    def atualizar(self, id_destino, nome, ativo):
        """Atualiza nome e status do destino pelo ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE destinos 
            SET nome_destino = ?, ativo = ?
            WHERE id = ?
        """, (nome.upper(), 1 if ativo else 0, int(id_destino)))
        self.conn.commit()
        return cursor.rowcount > 0
        
    def desativar(self, id_destino):
        """Marca destino como inativo (exclusão lógica)"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE destinos SET ativo = 0 WHERE id = ?", (int(id_destino),))
        self.conn.commit()
        return cursor.rowcount > 0
