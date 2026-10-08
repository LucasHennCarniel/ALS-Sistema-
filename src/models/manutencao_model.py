import sqlite3
import logging
from src.config import DB_PATH

class ManutencaoModel:
    """
    Gerencia o acesso ao banco de dados para Registros de Manutenção
    """
    
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
            logging.error(f"Erro ao conectar banco Manutenção: {e}")
            return False
            
    def criar_tabela(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS manutencoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT,
                    placa TEXT,
                    km REAL,
                    veiculo TEXT,
                    destino_programado TEXT,
                    servico_executar TEXT,
                    status TEXT,
                    data_entrada TEXT,
                    data_saida TEXT,
                    total_dias_manutencao INTEGER,
                    nr_of TEXT,
                    obs TEXT
                )
            """)
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Erro ao criar tabela de manutenção: {e}")
            return False
            
    def obter_todos(self):
        """
        Retorna todos os registros ordenados por id descrescente
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM manutencoes ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Erro ao obter manutenções: {e}")
            return []
            
    def obter_por_id(self, id_registro):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM manutencoes WHERE id = ?", (int(id_registro),))
        row = cursor.fetchone()
        return dict(row) if row else None
        
    def inserir(self, dados):
        """
        Insere um novo registro de manutenção no banco
        `dados` é um dicionário com chaves minúsculas combinando com as colunas do DB
        """
        colunas = [
            'data', 'placa', 'km', 'veiculo', 'destino_programado',
            'servico_executar', 'status', 'data_entrada', 'data_saida',
            'total_dias_manutencao', 'nr_of', 'obs'
        ]
        
        # Prepara valores na mesma ordem das colunas, substituindo KeyError por None
        valores = [dados.get(col, None) for col in colunas]
        placeholders = ', '.join(['?'] * len(colunas))
        cols_str = ', '.join(colunas)
        
        cursor = self.conn.cursor()
        cursor.execute(f"INSERT INTO manutencoes ({cols_str}) VALUES ({placeholders})", valores)
        self.conn.commit()
        return cursor.lastrowid
        
    def atualizar(self, id_registro, dados):
        """Atualiza registro inteiro"""
        colunas = [
            'data', 'placa', 'km', 'veiculo', 'destino_programado',
            'servico_executar', 'status', 'data_entrada', 'data_saida',
            'total_dias_manutencao', 'nr_of', 'obs'
        ]
        
        set_str = ', '.join([f"{col} = ?" for col in colunas])
        valores = [dados.get(col, None) for col in colunas]
        valores.append(int(id_registro))
        
        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE manutencoes SET {set_str} WHERE id = ?", valores)
        self.conn.commit()
        return cursor.rowcount > 0
        
    def deletar(self, id_registro):
        """Exclui registro permanentemente"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM manutencoes WHERE id = ?", (int(id_registro),))
        self.conn.commit()
        return cursor.rowcount > 0
