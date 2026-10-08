import sqlite3
import logging
from src.config import DB_PATH

class NotaModel:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.conectar()
        self.criar_tabela()
        
    def conectar(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA journal_mode=WAL;")
            return True
        except Exception as e:
            logging.error(f"Erro conectar notas: {e}")
            return False
            
    def criar_tabela(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_programada TEXT NOT NULL,
                    placa TEXT NOT NULL,
                    status TEXT,
                    observacao TEXT,
                    data_criacao TEXT,
                    UNIQUE(placa, data_programada)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notas_placa ON notas(placa)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notas_data ON notas(data_programada)")
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Erro criar tabela notas: {e}")
            return False
            
    def obter_todas(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, data_programada, placa, status, observacao FROM notas ORDER BY data_programada DESC")
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
            
    def obter_por_id(self, id_nota):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM notas WHERE id = ?", (int(id_nota),))
        row = cursor.fetchone()
        return dict(row) if row else None
        
    def inserir(self, dados):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO notas (data_programada, placa, status, observacao, data_criacao)
            VALUES (?, ?, ?, ?, ?)
        """, (
            dados.get('data_programada'), 
            dados.get('placa'), 
            dados.get('status'), 
            dados.get('observacao'), 
            dados.get('data_criacao')
        ))
        self.conn.commit()
        return cursor.lastrowid
        
    def atualizar(self, id_nota, dados):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE notas 
            SET data_programada=?, placa=?, status=?, observacao=?
            WHERE id=?
        """, (
            dados.get('data_programada'), 
            dados.get('placa'), 
            dados.get('status'), 
            dados.get('observacao'), 
            int(id_nota)
        ))
        self.conn.commit()
        return cursor.rowcount > 0
        
    def deletar(self, id_nota):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notas WHERE id = ?", (int(id_nota),))
        self.conn.commit()
        return cursor.rowcount > 0
