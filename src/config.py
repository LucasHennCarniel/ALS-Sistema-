import os
import sys

# Define caminhos base
if getattr(sys, 'frozen', False):
    # Se estiver rodando como executável
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diretórios
DATA_DIR = os.path.join(BASE_PATH, 'data')
OUTPUT_DIR = os.path.join(BASE_PATH, 'output')
BACKUP_DIR = os.path.join(BASE_PATH, 'backup')

# Caminhos de arquivos
DB_PATH = os.path.join(DATA_DIR, 'sistema_als.db')

# Versão do Aplicativo e Repositório Oficial
APP_VERSION = "1.0.2"
GITHUB_REPO = "LucasHennCarniel/ALS-Sistema-"
UPDATE_FLAG_MANDATORY = "[OBRIGATORIA]"

# Garante a existência dos diretórios
for path in [DATA_DIR, OUTPUT_DIR, BACKUP_DIR]:
    os.makedirs(path, exist_ok=True)

