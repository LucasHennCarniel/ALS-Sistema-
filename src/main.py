"""
Sistema de Gestão de Manutenção de Frota - ALS
Interface Gráfica Principal
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import pandas as pd
import os
import sys
import sqlite3
from PIL import Image, ImageTk

# Adiciona o diretório pai ao path (necessário para importações)
if getattr(sys, 'frozen', False):
    # Se estiver rodando como executável
    application_path = sys._MEIPASS
    base_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_path = application_path

sys.path.insert(0, application_path)

# Define caminho absoluto para o banco de dados
DB_PATH = os.path.join(base_path, 'data', 'sistema_als.db')

from src.controllers.manutencao_controller import ManutencaoController
from src.utils import formatar_data_br, validar_data, validar_numero, limpar_texto, gerar_relatorio_pdf, gerar_relatorio_word
from src.controllers.veiculo_controller import VeiculoController
from src.views.form_veiculos import JanelaCadastroVeiculos
from src.controllers.destino_controller import DestinoController


from src.views.form_registro import FormularioRegistro
from src.views.form_nota import FormularioNota

class SistemaManutencao:
    """
    Classe principal da interface gráfica
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Manutenção - ALS")
        self.root.geometry("1400x800")
        
        # Inicializa banco de dados
        try:
            self.db = ManutencaoController()
        except Exception as e:
            messagebox.showerror(
                "Erro ao Inicializar",
                f"Não foi possível carregar o banco de dados:\n{e}\n\nVerifique se a pasta 'data' existe."
            )
            sys.exit(1)
        
        from src.controllers.nota_controller import NotaController
        self.nota_controller = NotaController()
        
        # Inicializa gerenciador de veículos
        try:
            self.gerenciador_veiculos = VeiculoController()
        except Exception as e:
            messagebox.showerror(
                "Erro ao Inicializar",
                f"Não foi possível carregar o cadastro de veículos:\n{e}"
            )
            self.gerenciador_veiculos = VeiculoController()  # Cria novo vazio
        
        # Inicializa gerenciador de destinos
        try:
            self.gerenciador_destinos = DestinoController()
        except Exception as e:
            messagebox.showerror(
                "Erro ao Inicializar",
                f"Não foi possível carregar o cadastro de destinos:\n{e}"
            )
            self.gerenciador_destinos = DestinoController()  # Cria novo vazio
        
        # Variável para índice selecionado
        self.indice_selecionado = None
        
        # Controle de ordenação das colunas
        self.ordem_colunas = {}  # Armazena estado de ordenação de cada coluna
        self.df_original = None  # Guarda ordem original dos dados
        
        # Controle de reordenação de colunas (drag-and-drop)
        self.coluna_arrastada = None
        self.posicao_original_x = None
        self.ordem_colunas_preferida = self.carregar_ordem_colunas()
        
        # Configura estilo
        self.configurar_estilo()
        
        # Cria interface
        self.criar_interface()
        
        # Carrega dados iniciais
        self.atualizar_tabela()
        
        # Atualiza estatísticas
        self.atualizar_estatisticas()
        
        # Carrega notas
        self.atualizar_notas()
        
        # Configura fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)
    
    
    def configurar_estilo(self):
        """
        Configura estilo visual
        """
        style = ttk.Style()
        style.theme_use('clam')
        
        # Aumenta fonte dos botões para emojis ficarem maiores e mais visíveis
        style.configure('TButton', padding=6, font=('Segoe UI Emoji', 11))
        style.configure('TLabel', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'))  # Reduzido de 12 para 11
        style.configure('Treeview', rowheight=25, font=('Arial', 9))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    
    def criar_interface(self):
        """
        Cria interface completa
        """
        # ==== FRAME TOPO ====
        frame_topo = ttk.Frame(self.root, padding="3")
        frame_topo.pack(fill=tk.X)
        
        # Frame para logo e título
        frame_header = ttk.Frame(frame_topo)
        frame_header.pack(fill=tk.X, pady=(0, 3))
        
        # Logo ALS à esquerda
        try:
            # Determina caminho da logo
            if getattr(sys, 'frozen', False):
                logo_path = os.path.join(sys._MEIPASS, 'img', 'logo ALS.png')
            else:
                logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img', 'logo ALS.png')
            
            # Carrega e redimensiona logo
            logo_original = Image.open(logo_path)
            # Redimensiona mantendo proporção - LOGO COMPACTA (50px)
            altura_nova = 50  # Reduzido de 70 para 50 pixels
            proporcao = altura_nova / logo_original.height
            largura_nova = int(logo_original.width * proporcao)
            logo_redimensionada = logo_original.resize((largura_nova, altura_nova), Image.Resampling.LANCZOS)
            
            self.logo_photo = ImageTk.PhotoImage(logo_redimensionada)
            
            logo_label = ttk.Label(frame_header, image=self.logo_photo)
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            print(f"Aviso: Não foi possível carregar logo: {e}")
        
        # Título à direita da logo
        titulo_frame = ttk.Frame(frame_header)
        titulo_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        
        ttk.Label(
            titulo_frame,
            text="SISTEMA DE GESTÃO DE MANUTENÇÃO - ALS",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(15, 0))  # Ajustado para centralizar com logo compacta
        
        # Estatísticas
        self.frame_stats = ttk.Frame(frame_topo)
        self.frame_stats.pack(pady=3)
        
        self.label_stats = ttk.Label(self.frame_stats, text="", font=('Arial', 9))
        self.label_stats.pack()
        
        # ==== FRAME FILTROS ====
        frame_filtros = ttk.LabelFrame(self.root, text="[Filtros de Busca]", padding="5")
        frame_filtros.pack(fill=tk.X, padx=10, pady=3)
        
        filtro_linha = ttk.Frame(frame_filtros)
        filtro_linha.pack(fill=tk.X)
        
        ttk.Label(filtro_linha, text="Placa:").pack(side=tk.LEFT, padx=5)
        self.filtro_placa = ttk.Entry(filtro_linha, width=12)
        self.filtro_placa.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filtro_linha, text="Veículo:").pack(side=tk.LEFT, padx=5)
        self.filtro_veiculo = ttk.Entry(filtro_linha, width=12)
        self.filtro_veiculo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filtro_linha, text="Status:").pack(side=tk.LEFT, padx=5)
        self.filtro_status = ttk.Combobox(
            filtro_linha,
            values=['', 'EM TRÂNSITO', 'EM SERVIÇO', 'FINALIZADO'],
            width=12
        )
        self.filtro_status.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filtro_linha, text="Data Entrada:").pack(side=tk.LEFT, padx=5)
        self.filtro_data_entrada = ttk.Entry(filtro_linha, width=12)
        self.filtro_data_entrada.pack(side=tk.LEFT, padx=5)

        ttk.Label(filtro_linha, text="Data Saída:").pack(side=tk.LEFT, padx=5)
        self.filtro_data_saida = ttk.Entry(filtro_linha, width=12)
        self.filtro_data_saida.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filtro_linha, text="🔍  Buscar", command=self.aplicar_filtros).pack(side=tk.LEFT, padx=5)
        ttk.Button(filtro_linha, text="🧹  Limpar", command=self.limpar_filtros).pack(side=tk.LEFT, padx=5)
        
        # ==== FRAME AÇÕES ====
        frame_acoes = ttk.Frame(self.root, padding="10")
        frame_acoes.pack(fill=tk.X)
        
        ttk.Button(frame_acoes, text="➕  Novo Registro", command=self.novo_registro).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="✏️  Editar", command=self.editar_registro).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="🗑️  Excluir Selecionado", command=self.excluir_registro).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="🗑️❌  Excluir Múltiplos", command=self.excluir_multiplos).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="💾  Salvar", command=self.salvar_dados).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="🔄  Atualizar", command=self.atualizar_tabela).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="🚛  Veículos", command=self.gerenciar_veiculos).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="📊  Relatório", command=self.gerar_relatorio).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="📤  Exportar", command=self.exportar_dados).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="📥  Importar", command=self.importar_dados).pack(side=tk.LEFT, padx=5)
        
        # ==== NOTEBOOK (ABAS) ====
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # ABA 1: Registros de Manutenção
        frame_tabela = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame_tabela, text="📋 Registros de Manutenção")
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame_tabela, orient=tk.HORIZONTAL)
        
        # Treeview
        self.tree = ttk.Treeview(
            frame_tabela,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode='extended'  # Permite seleção múltipla com Ctrl e Shift
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Colunas
        colunas = ['DATA', 'PLACA', 'KM', 'VEÍCULO', 'DESTINO PROGRAMADO',
                   'SERVIÇO A EXECUTAR', 'STATUS', 'DATA ENTRADA', 'DATA SAÍDA',
                   'DIAS', 'NR° OF', 'OBS']
        
        # Aplica ordem personalizada se existir
        if self.ordem_colunas_preferida:
            colunas = self.ordem_colunas_preferida
        
        self.tree['columns'] = colunas
        self.tree.column('#0', width=0, stretch=tk.NO)
        
        larguras = {'DATA': 90, 'PLACA': 80, 'KM': 70, 'VEÍCULO': 100,
                    'DESTINO PROGRAMADO': 130, 'SERVIÇO A EXECUTAR': 200,
                    'STATUS': 100, 'DATA ENTRADA': 100, 'DATA SAÍDA': 100,
                    'DIAS': 50, 'NR° OF': 70, 'OBS': 150}
        
        for col in colunas:
            self.tree.column(col, width=larguras.get(col, 100), anchor=tk.W)
            self.tree.heading(
                col, 
                text=col, 
                anchor=tk.W,
                command=lambda c=col: self.ordenar_por_coluna(c)
            )
        
        # Configura eventos de drag-and-drop nas colunas
        self.tree.bind('<Button-1>', self.iniciar_arraste_coluna)
        self.tree.bind('<B1-Motion>', self.arrastar_coluna)
        self.tree.bind('<ButtonRelease-1>', self.finalizar_arraste_coluna)
        self.tree.bind('<Double-1>', lambda e: self.editar_registro())
        self.tree.bind('<<TreeviewSelect>>', self.on_selecionar)
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # ABA 2: Notas / Anotações
        frame_notas = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame_notas, text="📝 Notas e Anotações")
        
        # Frame de ações das notas
        frame_acoes_notas = ttk.Frame(frame_notas)
        frame_acoes_notas.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(frame_acoes_notas, text="➕  Nova Nota", command=self.nova_nota).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes_notas, text="✏️  Editar Nota", command=self.editar_nota).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes_notas, text="🗑️  Excluir Nota", command=self.excluir_nota).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes_notas, text="🔄  Atualizar", command=self.atualizar_notas).pack(side=tk.LEFT, padx=5)
        
        # Tabela de notas
        frame_tabela_notas = ttk.Frame(frame_notas)
        frame_tabela_notas.pack(fill=tk.BOTH, expand=True)
        
        scroll_y_notas = ttk.Scrollbar(frame_tabela_notas, orient=tk.VERTICAL)
        scroll_x_notas = ttk.Scrollbar(frame_tabela_notas, orient=tk.HORIZONTAL)
        
        self.tree_notas = ttk.Treeview(
            frame_tabela_notas,
            yscrollcommand=scroll_y_notas.set,
            xscrollcommand=scroll_x_notas.set,
            selectmode='browse'
        )
        
        scroll_y_notas.config(command=self.tree_notas.yview)
        scroll_x_notas.config(command=self.tree_notas.xview)
        
        # Colunas das notas: Data Programada, Placa, Status, Observação
        colunas_notas = ['DATA PROGRAMADA', 'PLACA', 'STATUS', 'OBSERVAÇÃO']
        
        self.tree_notas['columns'] = colunas_notas
        self.tree_notas.column('#0', width=0, stretch=tk.NO)
        
        larguras_notas = {'DATA PROGRAMADA': 150, 'PLACA': 120, 'STATUS': 150, 'OBSERVAÇÃO': 500}
        
        for col in colunas_notas:
            self.tree_notas.column(col, width=larguras_notas.get(col, 150), anchor=tk.W)
            self.tree_notas.heading(col, text=col, anchor=tk.W)
        
        self.tree_notas.bind('<Double-1>', lambda e: self.editar_nota())
        
        scroll_y_notas.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x_notas.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_notas.pack(fill=tk.BOTH, expand=True)
        
        # ==== STATUS BAR ====
        self.label_status = ttk.Label(
            self.root,
            text="✅  Sistema pronto",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.label_status.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
    
    
    def on_selecionar(self, event):
        """
        Callback quando linha é selecionada
        """
        selecao = self.tree.selection()
        if selecao:
            item = self.tree.item(selecao[0])
            self.indice_selecionado = item['tags'][0] if item['tags'] else None
    
    
    def carregar_ordem_colunas(self):
        """
        Carrega ordem personalizada das colunas do arquivo de configuração
        """
        config_file = 'data/config_colunas.txt'
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    colunas = f.read().strip().split(',')
                    if len(colunas) == 12:  # Valida se tem todas as 12 colunas
                        return colunas
        except:
            pass
        return None
    
    
    def salvar_ordem_colunas(self, colunas):
        """
        Salva ordem personalizada das colunas em arquivo de configuração
        """
        config_file = 'data/config_colunas.txt'
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(','.join(colunas))
        except Exception as e:
            print(f"Erro ao salvar ordem das colunas: {e}")
    
    
    def iniciar_arraste_coluna(self, event):
        """
        Inicia arraste de coluna (quando clica no cabeçalho)
        """
        # Identifica se clicou no cabeçalho
        regiao = self.tree.identify_region(event.x, event.y)
        if regiao == 'heading':
            coluna = self.tree.identify_column(event.x)
            if coluna != '#0':  # Ignora coluna invisível
                # Converte #1, #2, etc para índice numérico
                indice_coluna = int(coluna.replace('#', '')) - 1
                colunas_atuais = list(self.tree['columns'])
                if 0 <= indice_coluna < len(colunas_atuais):
                    self.coluna_arrastada = colunas_atuais[indice_coluna]
                    self.posicao_original_x = event.x
                    self.tree.config(cursor='hand2')
    
    
    def arrastar_coluna(self, event):
        """
        Movimenta coluna durante arraste
        """
        if self.coluna_arrastada:
            # Mostra cursor de movimento
            self.tree.config(cursor='fleur')
    
    
    def finalizar_arraste_coluna(self, event):
        """
        Finaliza arraste e reordena colunas
        """
        if self.coluna_arrastada and self.posicao_original_x is not None:
            # Restaura cursor
            self.tree.config(cursor='')
            
            # Identifica coluna de destino
            regiao = self.tree.identify_region(event.x, event.y)
            if regiao == 'heading':
                coluna_destino = self.tree.identify_column(event.x)
                if coluna_destino != '#0':
                    indice_destino = int(coluna_destino.replace('#', '')) - 1
                    colunas_atuais = list(self.tree['columns'])
                    
                    if 0 <= indice_destino < len(colunas_atuais):
                        # Reordena colunas
                        coluna_destino_nome = colunas_atuais[indice_destino]
                        
                        # Remove coluna arrastada da posição original
                        indice_original = colunas_atuais.index(self.coluna_arrastada)
                        colunas_atuais.pop(indice_original)
                        
                        # Insere na nova posição
                        indice_destino_ajustado = colunas_atuais.index(coluna_destino_nome)
                        
                        # Se arrastou da esquerda para direita, ajusta índice
                        if indice_original < indice_destino_ajustado + 1:
                            colunas_atuais.insert(indice_destino_ajustado + 1, self.coluna_arrastada)
                        else:
                            colunas_atuais.insert(indice_destino_ajustado, self.coluna_arrastada)
                        
                        # Aplica nova ordem
                        self.aplicar_nova_ordem_colunas(colunas_atuais)
                        
                        # Salva configuração
                        self.salvar_ordem_colunas(colunas_atuais)
                        self.ordem_colunas_preferida = colunas_atuais
                        
                        self.label_status.config(text=f"✅  Coluna '{self.coluna_arrastada}' movida com sucesso!")
        
        # Reseta variáveis
        self.coluna_arrastada = None
        self.posicao_original_x = None
        self.tree.config(cursor='')
    
    
    def aplicar_nova_ordem_colunas(self, novas_colunas):
        """
        Aplica nova ordem de colunas à TreeView
        """
        # Guarda dados atuais
        dados_atuais = []
        for item in self.tree.get_children():
            valores = self.tree.item(item)['values']
            tags = self.tree.item(item)['tags']
            dados_atuais.append((valores, tags))
        
        # Mapa de colunas antigas para novas
        colunas_antigas = list(self.tree['columns'])
        
        # Larguras das colunas
        larguras = {'DATA': 90, 'PLACA': 80, 'KM': 70, 'VEÍCULO': 100,
                    'DESTINO PROGRAMADO': 130, 'SERVIÇO A EXECUTAR': 200,
                    'STATUS': 100, 'DATA ENTRADA': 100, 'DATA SAÍDA': 100,
                    'DIAS': 50, 'NR° OF': 70, 'OBS': 150}
        
        # Atualiza configuração de colunas
        self.tree['columns'] = novas_colunas
        
        for col in novas_colunas:
            self.tree.column(col, width=larguras.get(col, 100), anchor=tk.W)
            self.tree.heading(
                col,
                text=col,
                anchor=tk.W,
                command=lambda c=col: self.ordenar_por_coluna(c)
            )
        
        # Reinsere dados com nova ordem de colunas
        self.tree.delete(*self.tree.get_children())
        
        # Mapa de índices: coluna_antiga -> posição
        mapa_indices = {col: idx for idx, col in enumerate(colunas_antigas)}
        
        for valores_antigos, tags in dados_atuais:
            # Reordena valores conforme nova ordem de colunas
            valores_novos = []
            for nova_col in novas_colunas:
                idx_antigo = mapa_indices.get(nova_col, 0)
                if idx_antigo < len(valores_antigos):
                    valores_novos.append(valores_antigos[idx_antigo])
                else:
                    valores_novos.append('')
            
            self.tree.insert('', tk.END, values=valores_novos, tags=tags)
    
    
    def ordenar_por_coluna(self, coluna):
        """
        Ordena tabela clicando no cabeçalho da coluna
        Estados: None (original) -> 'asc' (crescente) -> 'desc' (decrescente) -> None (volta ao original)
        """
        # Guarda DataFrame original na primeira ordenação
        if self.df_original is None:
            self.df_original = self.db.df.copy()
        
        # Verifica estado atual da coluna
        estado_atual = self.ordem_colunas.get(coluna, None)
        
        # Mapeia coluna visual para coluna do DataFrame
        mapa_colunas = {
            'DATA': 'DATA',
            'PLACA': 'PLACA',
            'KM': 'KM',
            'VEÍCULO': 'VEÍCULO',
            'DESTINO PROGRAMADO': 'DESTINO PROGRAMADO',
            'SERVIÇO A EXECUTAR': 'SERVIÇO A EXECUTAR',
            'STATUS': 'STATUS',
            'DATA ENTRADA': 'DATA ENTRADA',
            'DATA SAÍDA': 'DATA SAÍDA',
            'DIAS': 'TOTAL DE DIAS EM MANUTENÇÃO',
            'NR° OF': 'NR° OF',
            'OBS': 'OBS'
        }
        
        coluna_df = mapa_colunas.get(coluna, coluna)
        
        # Define próximo estado
        if estado_atual is None:
            # Primeira vez: ordena crescente
            novo_estado = 'asc'
            df_ordenado = self.db.df.copy()
            
            # Tratamento especial para datas
            if coluna in ['DATA', 'DATA ENTRADA', 'DATA SAÍDA']:
                df_ordenado[coluna_df] = pd.to_datetime(df_ordenado[coluna_df], format='%d/%m/%Y', errors='coerce')
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=True, na_position='last')
            # Tratamento especial para números
            elif coluna in ['KM', 'DIAS']:
                df_ordenado[coluna_df] = pd.to_numeric(df_ordenado[coluna_df], errors='coerce')
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=True, na_position='last')
            # Tratamento especial para STATUS (preenche vazios)
            elif coluna == 'STATUS':
                df_ordenado[coluna_df] = df_ordenado[coluna_df].fillna('').astype(str)
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=True, na_position='last')
            # Ordenação alfabética para texto
            else:
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=True, na_position='last')
            
            # Atualiza indicador visual no cabeçalho
            self.tree.heading(coluna, text=f"{coluna} ▲")
            
        elif estado_atual == 'asc':
            # Segunda vez: ordena decrescente
            novo_estado = 'desc'
            df_ordenado = self.db.df.copy()
            
            # Tratamento especial para datas
            if coluna in ['DATA', 'DATA ENTRADA', 'DATA SAÍDA']:
                df_ordenado[coluna_df] = pd.to_datetime(df_ordenado[coluna_df], format='%d/%m/%Y', errors='coerce')
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=False, na_position='last')
            # Tratamento especial para números
            elif coluna in ['KM', 'DIAS']:
                df_ordenado[coluna_df] = pd.to_numeric(df_ordenado[coluna_df], errors='coerce')
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=False, na_position='last')
            # Tratamento especial para STATUS (preenche vazios)
            elif coluna == 'STATUS':
                df_ordenado[coluna_df] = df_ordenado[coluna_df].fillna('').astype(str)
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=False, na_position='last')
            # Ordenação alfabética para texto
            else:
                df_ordenado = df_ordenado.sort_values(by=coluna_df, ascending=False, na_position='last')
            
            # Atualiza indicador visual no cabeçalho
            self.tree.heading(coluna, text=f"{coluna} ▼")
            
        else:  # estado_atual == 'desc'
            # Terceira vez: volta à ordem original (recarrega do banco)
            novo_estado = None
            # self.db.carregar_dados() no longer needed  # Recarrega do SQLite
            df_ordenado = self.db.df.copy()
            
            # Remove indicador visual do cabeçalho
            self.tree.heading(coluna, text=coluna)
        
        # Atualiza estado da coluna
        self.ordem_colunas[coluna] = novo_estado
        
        # Remove indicadores de outras colunas
        colunas_visiveis = ['DATA', 'PLACA', 'KM', 'VEÍCULO', 'DESTINO PROGRAMADO',
                           'SERVIÇO A EXECUTAR', 'STATUS', 'DATA ENTRADA', 'DATA SAÍDA',
                           'DIAS', 'NR° OF', 'OBS']
        for outra_col in colunas_visiveis:
            if outra_col != coluna and self.ordem_colunas.get(outra_col) is not None:
                self.ordem_colunas[outra_col] = None
                self.tree.heading(outra_col, text=outra_col)
        
        # Atualiza a exibição com DataFrame ordenado
        # NOTA: Apenas reordena visualização, não altera dados no SQLite
        if novo_estado is None:
            # Se voltou ao normal, mantém o DataFrame recarregado
            self.atualizar_tabela()
        else:
            # Se ordenou, usa o DataFrame ordenado
            self.db.df = df_ordenado.reset_index(drop=True)
            self.atualizar_tabela()
    
    
    def atualizar_tabela(self, df=None):
        """
        Atualiza dados na tabela
        """
        # Limpa tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Usa DataFrame fornecido ou completo
        if df is None:
            df = self.db.obter_dataframe_exibicao()
            # Salva ordem original na primeira vez
            if self.df_original is None:
                self.df_original = self.db.df.copy()
        
        # Mapa de colunas visuais para dados
        mapa_dados = {
            'DATA': 'DATA',
            'PLACA': 'PLACA',
            'KM': 'KM',
            'VEÍCULO': 'VEÍCULO',
            'DESTINO PROGRAMADO': 'DESTINO PROGRAMADO',
            'SERVIÇO A EXECUTAR': 'SERVIÇO A EXECUTAR',
            'STATUS': 'STATUS',
            'DATA ENTRADA': 'DATA ENTRADA',
            'DATA SAÍDA': 'DATA SAÍDA',
            'DIAS': 'TOTAL DE DIAS EM MANUTENÇÃO',
            'NR° OF': 'NR° OF',
            'OBS': 'OBS'
        }
        
        # Obtém ordem atual das colunas
        colunas_atuais = list(self.tree['columns'])
        
        # Popula tabela respeitando ordem das colunas
        for idx, row in df.iterrows():
            # Constrói valores na ordem das colunas atuais
            valores = []
            for col in colunas_atuais:
                col_dado = mapa_dados.get(col, col)
                
                # Tratamento especial para datas
                if col in ['DATA', 'DATA ENTRADA', 'DATA SAÍDA']:
                    valores.append(formatar_data_br(row.get(col_dado, '')))
                # Tratamento especial para DIAS
                elif col == 'DIAS':
                    valores.append(row.get('DIAS', row.get('TOTAL DE DIAS EM MANUTENÇÃO', '0')))
                else:
                    valores.append(row.get(col_dado, ''))
            
            # Define cor baseada no status
            status_upper = row.get('STATUS', '').upper()
            if status_upper == 'EM TRÂNSITO':
                tag = 'em_transito'
            elif status_upper == 'EM SERVIÇO':
                tag = 'em_servico'
            else:
                tag = 'finalizado'
            
            self.tree.insert('', tk.END, values=valores, tags=(idx, tag))
        
        # Configura cores
        self.tree.tag_configure('em_transito', background='#f0f0f0')  # Cinza mais claro
        self.tree.tag_configure('em_servico', background='#fff3cd')   # Amarelo claro
        self.tree.tag_configure('finalizado', background='#d1e7dd')   # Verde claro
        
        self.label_status.config(text=f"📋  {len(df)} registros carregados")
    
    
    def atualizar_estatisticas(self):
        """
        Atualiza estatísticas no topo
        """
        stats = self.db.obter_estatisticas()
        
        texto = f"📊  Total: {stats['total']}  |  "
        texto += f"🔧  Em Serviço: {stats['em_servico']}  |  "
        texto += f"✅  Finalizados: {stats['finalizados']}  |  "
        texto += f"⏱️  Tempo Médio: {stats['tempo_medio']:.1f} dias  |  "
        texto += f"🚗  Placas: {stats['placas_unicas']}"
        
        self.label_stats.config(text=texto)
    
    
    def aplicar_filtros(self):
        """
        Aplica filtros de busca
        """
        filtros = {}
        if self.filtro_placa.get():
            filtros['PLACA'] = self.filtro_placa.get()
        if self.filtro_veiculo.get():
            filtros['VEÍCULO'] = self.filtro_veiculo.get()
        if self.filtro_status.get():
            filtros['STATUS'] = self.filtro_status.get()
        if self.filtro_data_entrada.get():
            filtros['DATA ENTRADA'] = self.filtro_data_entrada.get()
        if self.filtro_data_saida.get():
            filtros['DATA SAÍDA'] = self.filtro_data_saida.get()
        df_filtrado = self.db.buscar_registros(filtros)
        self.atualizar_tabela(df_filtrado)
        self.label_status.config(text=f"🔍  {len(df_filtrado)} registros encontrados")
    
    
    def limpar_filtros(self):
        """
        Limpa filtros e mostra todos os registros
        """
        self.filtro_placa.delete(0, tk.END)
        self.filtro_veiculo.delete(0, tk.END)
        self.filtro_status.set('')
        self.filtro_data_entrada.delete(0, tk.END)
        self.filtro_data_saida.delete(0, tk.END)
        self.atualizar_tabela()
    
    
    def novo_registro(self):
        """
        Abre formulário para novo registro
        """
        def callback(dados):
            try:
                sucesso, msg = self.db.adicionar_registro(dados)
                if sucesso:
                    self.atualizar_tabela()
                    self.atualizar_estatisticas()
                    messagebox.showinfo("Sucesso", msg)
                else:
                    messagebox.showerror("Erro", msg)
            except Exception as e:
                messagebox.showerror("Erro ao adicionar registro", str(e))
        FormularioRegistro(self.root, self.db, self.gerenciador_veiculos, self.gerenciador_destinos, callback=callback)
    
    
    def editar_registro(self):
        """
        Edita registro selecionado
        """
        if self.indice_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um registro para editar")
            return
        
        registro = self.db.df.iloc[self.indice_selecionado].to_dict()
        id_registro = registro.get('ID')
        
        def callback(dados):
            sucesso, msg = self.db.atualizar_registro(id_registro, dados)
            if sucesso:
                self.atualizar_tabela()
                self.atualizar_estatisticas()
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Erro", msg)
        
        FormularioRegistro(self.root, self.db, self.gerenciador_veiculos, self.gerenciador_destinos, registro=registro, callback=callback)
    
    
    def excluir_registro(self):
        """Exclui o registro selecionado."""
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um registro para excluir")
            return
            
        if len(selecao) > 1:
            messagebox.showinfo("Dica", "Você selecionou múltiplos registros.\n\nUse o botão '🗑️ Excluir Múltiplos' para excluir vários de uma vez.")
            return
            
        item = self.tree.item(selecao[0])
        indice = item['tags'][0] if item['tags'] else None
        
        if indice is None:
            messagebox.showwarning("Aviso", "Não foi possível identificar o registro")
            return
            
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este registro?"
        )
        
        if resposta:
            try:
                # indice é o índice do dataframe Pandas
                registro = self.db.df.iloc[int(indice)].to_dict()
                id_registro = registro.get('ID')
                
                sucesso = self.db.excluir_registro(id_registro)
                if sucesso:
                    self.atualizar_tabela()
                    self.atualizar_estatisticas()
                    self.indice_selecionado = None
                    messagebox.showinfo("Sucesso", "Registro excluído com sucesso!")
                else:
                    messagebox.showerror("Erro", "Erro ao excluir no banco de dados")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
    
    
    def excluir_multiplos(self):
        """
        Exclui múltiplos registros selecionados
        """
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um ou mais registros para excluir\n\n💡 Dica: Use Ctrl+Clique ou Shift+Clique para selecionar múltiplos")
            return
        
        qtd = len(selecao)
        
        resposta = messagebox.askyesno(
            "Confirmar Exclusão Múltipla",
            f"Tem certeza que deseja excluir {qtd} registro(s) selecionado(s)?\n\n⚠️ Esta ação não pode ser desfeita!"
        )
        
        if resposta:
            # Coleta todos os índices dos registros selecionados
            indices_para_excluir = []
            for item_id in selecao:
                item = self.tree.item(item_id)
                indice = item['tags'][0] if item['tags'] else None
                if indice is not None:
                    indices_para_excluir.append(indice)
            
            # Ordena em ordem decrescente para não afetar os índices durante exclusão
            indices_para_excluir.sort(reverse=True)
            
            # Exclui cada registro
            excluidos = 0
            for indice in indices_para_excluir:
                if self.db.excluir_registro(indice):
                    excluidos += 1
            
            # Salva alterações
            if self.db.salvar_dados():
                self.atualizar_tabela()
                self.atualizar_estatisticas()
                self.indice_selecionado = None
                messagebox.showinfo("Sucesso", f"{excluidos} registro(s) excluído(s) com sucesso!")
            else:
                messagebox.showerror("Erro", f"{excluidos} registro(s) excluído(s) mas não foi possível salvar no banco de dados")
    
    
    def salvar_dados(self):
        """
        Salva dados no Excel
        """
        if self.db.salvar_dados():
            self.atualizar_estatisticas()
            messagebox.showinfo("Sucesso", "Dados salvos com sucesso!\n\nBackup criado na pasta 'backup'")
        else:
            messagebox.showerror("Erro", "Não foi possível salvar os dados")
    
    
    def gerenciar_veiculos(self):
        """
        Abre janela de gerenciamento de veículos
        """
        JanelaCadastroVeiculos(self.root, self.gerenciador_veiculos)
    
    
    def gerar_relatorio(self):
        from src.views.modal_relatorio import ModalRelatorio
        ModalRelatorio(self.root, self.db)

    def nova_nota(self):
        """Abre formulário para nova nota"""
        FormularioNota(self.root, self.db, self.gerenciador_veiculos, callback=self.atualizar_notas)
    
    
    def editar_nota(self):
        """Edita nota selecionada"""
        selecao = self.tree_notas.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione uma nota para editar!")
            return
        
        item = self.tree_notas.item(selecao[0])
        id_nota = item['tags'][0] if item['tags'] else None
        
        if id_nota is None:
            return
        
        # Busca dados da nota no banco
        nota = self.nota_controller.obter_por_id(id_nota)
        
        if nota:
            nota_dict = {
                'id': nota[0],
                'data_programada': nota[1],
                'placa': nota[2],
                'status': nota[3],
                'observacao': nota[4]
            }
            FormularioNota(self.root, self.db, self.gerenciador_veiculos, nota=nota_dict, callback=self.atualizar_notas)
    
    
    def excluir_nota(self):
        """Exclui nota selecionada"""
        selecao = self.tree_notas.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione uma nota para excluir!")
            return
        
        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir esta nota?"):
            return
        
        item = self.tree_notas.item(selecao[0])
        id_nota = item['tags'][0] if item['tags'] else None
        
        try:
            self.nota_controller.excluir_nota(id_nota)
            self.atualizar_notas()
            messagebox.showinfo("Sucesso", "Nota excluída com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir nota: {e}")
    
    
    def atualizar_notas(self):
        """Atualiza tabela de notas"""
        # Limpa tabela
        for item in self.tree_notas.get_children():
            self.tree_notas.delete(item)
        
        try:
            # Carrega notas do banco
            notas = self.nota_controller.obter_todas()

            for nota in notas:
                id_nota = nota['id']
                data_prog = nota['data_programada']
                placa = nota['placa']
                status = nota['status']
                obs = nota['observacao']
                self.tree_notas.insert(
                    '', 
                    'end',
                    values=(data_prog, placa, status or '', obs or ''),
                    tags=(id_nota,)
                )
        except Exception as e:
            print(f"Erro ao carregar notas: {e}")
    
    
    def exportar_dados(self):
        from src.views.modal_exportar import ModalExportar
        from src.services.export_service import ExportService
        ModalExportar(self.root, self.db, self.tree, ExportService)

    def importar_dados(self):
        """Importa dados de arquivo Excel para o banco SQLite"""
        # Janela de opções
        dialog = tk.Toplevel(self.root)
        dialog.title("Importar Dados")
        dialog.geometry("550x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (275)
        y = (dialog.winfo_screenheight() //  2) - (225)
        dialog.geometry(f"550x450+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame,
            text="📥 Importar Dados do Excel",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 15))
        
        ttk.Label(
            frame,
            text="Use esta função para importar registros antigos do Excel\npara o banco de dados SQLite.",
            font=('Arial', 10),
            justify=tk.CENTER
       
        ).pack(pady=(0, 20))
        
        # Modo de importação
        modo_frame = ttk.LabelFrame(frame, text="🔄 Modo de Importação", padding="10")
        modo_frame.pack(fill=tk.X, pady=(0, 10))
        
        modo_var = tk.StringVar(value="novo")
        
        ttk.Radiobutton(
            modo_frame,
            text="📝 Substituir tudo (apaga dados atuais e importa do zero)",
            variable=modo_var,
            value="substituir"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            modo_frame,
            text="➕ Apenas registros novos (ignora duplicados)",
            variable=modo_var,
            value="novo"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            modo_frame,
            text="🔄 Atualizar existentes (substitui duplicados e adiciona novos)",
            variable=modo_var,
            value="atualizar"
        ).pack(anchor=tk.W, pady=2)
        
        # Informações
        info_frame = ttk.LabelFrame(frame, text="ℹ️ Importante", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            info_frame,
            text="• O arquivo Excel deve ter as mesmas colunas da planilha original\n"
                 "• Veículos e destinos serão cadastrados automaticamente\n"
                 "• Um backup do banco atual será criado antes da importação",
            font=('Arial', 9),
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        def selecionar_arquivo():
            arquivo = filedialog.askopenfilename(
                title="Selecione o arquivo Excel",
                filetypes=[("Excel", "*.xlsx *.xls"), ("Todos", "*.*")],
                initialdir="data"
            )
            
            if not arquivo:
                return
            
            # Confirma importação
            resposta = messagebox.askyesno(
                "Confirmar Importação",
                f"Deseja importar dados do arquivo:\n\n{os.path.basename(arquivo)}\n\n"
                "⚠️ Um backup será criado automaticamente.",
                parent=dialog
            )
            
            if not resposta:
                return
            
            # Pega o modo selecionado
            modo = modo_var.get()
            
            try:
                dialog.destroy()
                
                # Mostra progresso
                progress_win = tk.Toplevel(self.root)
                progress_win.title("Importando...")
                progress_win.geometry("400x150")
                progress_win.transient(self.root)
                progress_win.grab_set()
                
                # Centraliza
                progress_win.update_idletasks()
                px = (progress_win.winfo_screenwidth() // 2) - 200
                py = (progress_win.winfo_screenheight() // 2) - 75
                progress_win.geometry(f"400x150+{px}+{py}")
                
                ttk.Label(
                    progress_win,
                    text="📥 Importando dados...",
                    font=('Arial', 12, 'bold')
                ).pack(pady=20)
                
                label_status = ttk.Label(progress_win, text="Lendo arquivo Excel...", font=('Arial', 10))
                label_status.pack(pady=10)
                
                progress_win.update()
                
                # Tenta ler Excel (header=1 pula linha de título)
                try:
                    # Copia arquivo temporariamente se estiver no OneDrive
                    import tempfile
                    if 'OneDrive' in arquivo or 'onedrive' in arquivo.lower():
                        label_status.config(text="Copiando arquivo do OneDrive...")
                        progress_win.update()
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                            arquivo_temp = tmp.name
                            import shutil
                            shutil.copy2(arquivo, arquivo_temp)
                            arquivo = arquivo_temp
                    
                    df_excel = pd.read_excel(arquivo, header=1)
                except PermissionError as e:
                    progress_win.destroy()
                    messagebox.showerror(
                        "Erro de Permissão",
                        f"Não foi possível acessar o arquivo:\n\n{os.path.basename(arquivo)}\n\n"
                        "💡 Dicas:\n"
                        "• Feche o arquivo no Excel se estiver aberto\n"
                        "• Se o arquivo estiver no OneDrive, copie para a pasta 'data' do sistema\n"
                        "• Verifique se você tem permissão de leitura no arquivo"
                    )
                    return
                except Exception as e:
                    progress_win.destroy()
                    messagebox.showerror(
                        "Erro ao Ler Arquivo",
                        f"Erro ao ler o arquivo Excel:\n\n{str(e)}\n\n"
                        "Verifique se o arquivo está no formato correto."
                    )
                    return
                
                # Limpa nomes de colunas (remove espaços extras)
                df_excel.columns = df_excel.columns.str.strip()
                
                label_status.config(text=f"Encontrados {len(df_excel)} registros")
                progress_win.update()
                
                # Faz backup do banco atual
                import shutil
                backup_path = f"backup/database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                os.makedirs('backup', exist_ok=True)
                shutil.copy2('data/sistema_als.db', backup_path)
                
                label_status.config(text=f"Modo: {modo.upper()} - Processando...")
                progress_win.update()
                
                # Importa dados
                cursor = self.db.model.conn.cursor()
                contador = 0
                atualizados = 0
                erros = 0
                
                # Se modo for "substituir", limpa a tabela
                if modo == "substituir":
                    label_status.config(text="Limpando dados antigos...")
                    progress_win.update()
                    cursor.execute("DELETE FROM manutencoes")
                    cursor.execute("DELETE FROM notas")
                    self.db.model.conn.commit()
                
                for idx, row in df_excel.iterrows():
                    try:
                        # Converte datas do pandas Timestamp para string formatada
                        data_val = row.get('DATA')
                        if pd.notna(data_val):
                            if isinstance(data_val, pd.Timestamp):
                                data_str = data_val.strftime('%d/%m/%Y')
                            else:
                                data_str = str(data_val).strip()
                        else:
                            data_str = ''
                        
                        placa = str(row.get('PLACA', '')).strip()
                        
                        data_entrada_val = row.get('DATA ENTRADA')
                        if pd.notna(data_entrada_val):
                            if isinstance(data_entrada_val, pd.Timestamp):
                                data_entrada = data_entrada_val.strftime('%d/%m/%Y')
                            else:
                                data_entrada = str(data_entrada_val).strip()
                        else:
                            data_entrada = ''
                        
                        data_saida_val = row.get('DATA SAÍDA')
                        if pd.notna(data_saida_val):
                            if isinstance(data_saida_val, pd.Timestamp):
                                data_saida = data_saida_val.strftime('%d/%m/%Y')
                            else:
                                data_saida = str(data_saida_val).strip()
                        else:
                            data_saida = ''
                        
                        # Converte KM para inteiro (remove decimais)
                        km_val = row.get('KM')
                        if pd.notna(km_val) and km_val != 'xxx':
                            try:
                                km = int(float(km_val))
                            except:
                                km = 0
                        else:
                            km = 0
                        
                        # Pula linhas completamente vazias (não conta como erro)
                        if not placa and not data_str and not data_entrada:
                            continue
                        
                        # Valida campos obrigatórios
                        if not placa or not data_str or not data_entrada:
                            erros += 1
                            print(f"⚠️ Linha {idx+2}: Dados incompletos - Placa: '{placa}', Data: '{data_str}', Data Entrada: '{data_entrada}'")
                            continue
                        
                        # Verifica se registro já existe (por PLACA + DATA + DATA_ENTRADA)
                        cursor.execute("""
                            SELECT id FROM manutencoes 
                            WHERE placa = ? AND data = ? AND data_entrada = ?
                        """, (placa, data_str, data_entrada))
                        
                        existe = cursor.fetchone()
                        
                        if modo == "novo" and existe:
                            # Modo "novo" - ignora se já existe
                            erros += 1
                            continue
                        elif modo == "atualizar" and existe:
                            # Atualiza registro existente
                            cursor.execute("""
                                UPDATE manutencoes SET
                                    km = ?,
                                    veiculo = ?,
                                    destino_programado = ?,
                                    servico_executar = ?,
                                    status = ?,
                                    data_saida = ?,
                                    total_dias_manutencao = ?,
                                    nr_of = ?,
                                    obs = ?
                                WHERE id = ?
                            """, (
                                km,
                                str(row.get('VEÍCULO', '')),
                                str(row.get('DESTINO PROGRAMADO', '')),
                                str(row.get('SERVIÇO A EXECUTAR', '')),
                                str(row.get('STATUS', '')),
                                data_saida,
                                int(row.get('TOTAL DE DIAS EM MANUTENÇÃO', 0)) if pd.notna(row.get('TOTAL DE DIAS EM MANUTENÇÃO')) else 0,
                                str(row.get('NR° OF', '')),
                                str(row.get('OBS', '')),
                                existe[0]
                            ))
                            atualizados += 1
                        else:
                            # Insere novo registro (quando não existe)
                            cursor.execute("""
                                INSERT INTO manutencoes (
                                    data, placa, km, veiculo, destino_programado,
                                    servico_executar, status, data_entrada, data_saida,
                                    total_dias_manutencao, nr_of, obs
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                data_str,
                                placa,
                                km,
                                str(row.get('VEÍCULO', '')),
                                str(row.get('DESTINO PROGRAMADO', '')),
                                str(row.get('SERVIÇO A EXECUTAR', '')),
                                str(row.get('STATUS', '')),
                                data_entrada,
                                data_saida,
                                int(row.get('TOTAL DE DIAS EM MANUTENÇÃO', 0)) if pd.notna(row.get('TOTAL DE DIAS EM MANUTENÇÃO')) else 0,
                                str(row.get('NR° OF', '')),
                                str(row.get('OBS', ''))
                            ))
                            contador += 1
                    except Exception as e:
                        erros += 1
                        print(f"Erro no registro {idx}: {e}")
                
                # Auto-cadastra veículos
                cursor.execute("""
                    INSERT OR IGNORE INTO veiculos (placa, tipo_veiculo, descricao, data_cadastro)
                    SELECT DISTINCT 
                        placa,
                        veiculo,
                        'Importado do Excel',
                        ?
                    FROM manutencoes
                    WHERE placa IS NOT NULL AND placa != ''
                """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
                
                veiculos_novos = cursor.rowcount
                
                # Auto-cadastra destinos
                cursor.execute("""
                    INSERT OR IGNORE INTO destinos (nome_destino, data_cadastro)
                    SELECT DISTINCT 
                        destino_programado,
                        ?
                    FROM manutencoes
                    WHERE destino_programado IS NOT NULL AND destino_programado != ''
                """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
                
                destinos_novos = cursor.rowcount
                
                self.db.model.conn.commit()
                
                progress_win.destroy()
                
                # Atualiza interface
                # self.db.carregar_dados() no longer needed
                self.atualizar_tabela()
                self.atualizar_estatisticas()
                
                # Mostra resultado
                msg_modo = {
                    "substituir": "Todos os dados foram substituídos",
                    "novo": "Apenas registros novos foram importados",
                    "atualizar": "Registros foram atualizados/adicionados"
                }
                
                resultado = f"✅ Importação concluída com sucesso!\n\n"
                resultado += f"🔄 Modo: {msg_modo[modo]}\n\n"
                resultado += f"📊 Registros novos: {contador}\n"
                
                if modo == "atualizar":
                    resultado += f"🔄 Registros atualizados: {atualizados}\n"
                
                resultado += f"⚠️ Erros/duplicados: {erros}\n"
                resultado += f"🚛 Veículos cadastrados: {veiculos_novos}\n"
                resultado += f"📍 Destinos cadastrados: {destinos_novos}\n\n"
                resultado += f"💾 Backup salvo em:\n{backup_path}"
                
                messagebox.showinfo(
                    "Importação Concluída",
                    resultado
                )
                
            except PermissionError as e:
                if 'progress_win' in locals() and progress_win.winfo_exists():
                    progress_win.destroy()
                messagebox.showerror(
                    "Erro de Permissão",
                    f"Acesso negado ao arquivo:\n\n{str(e)}\n\n"
                    "💡 Feche o arquivo no Excel e tente novamente.",
                    parent=dialog if 'dialog' in locals() and dialog.winfo_exists() else self.root
                )
            except Exception as e:
                # Faz rollback se houver erro
                if 'cursor' in locals():
                    try:
                        self.db.model.conn.rollback()
                    except:
                        pass
                
                if 'progress_win' in locals() and progress_win.winfo_exists():
                    progress_win.destroy()
                
                messagebox.showerror(
                    "Erro na Importação",
                    f"Erro ao importar dados:\n\n{str(e)}\n\n"
                    "⚠️ Nenhuma alteração foi feita no banco de dados.",
                    parent=dialog if 'dialog' in locals() and dialog.winfo_exists() else self.root
                )
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="📂  Selecionar Arquivo Excel",
            command=selecionar_arquivo,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            btn_frame,
            text="❌  Cancelar",
            command=dialog.destroy,
            width=25
        ).pack(pady=5)
    
    
    def fechar_aplicacao(self):
        """
        Fecha aplicação com confirmação
        """
        resposta = messagebox.askyesnocancel(
            "Fechar Sistema",
            "Deseja salvar os dados antes de sair?"
        )
        
        if resposta is None:  # Cancelar
            return
        elif resposta:  # Sim
            self.db.salvar_dados()
        
        self.root.destroy()


def main():
    """
    Função principal
    """
    root = tk.Tk()
    app = SistemaManutencao(root)
    root.mainloop()


if __name__ == "__main__":
    main()
