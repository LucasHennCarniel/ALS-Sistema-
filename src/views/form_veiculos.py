"""
Interface para Gestão de Cadastro de Veículos
"""
import tkinter as tk
from tkinter import ttk, messagebox


class JanelaCadastroVeiculos(tk.Toplevel):
    """
    Janela para gerenciar cadastro de veículos
    """
    
    def __init__(self, parent, gerenciador_veiculos):
        super().__init__(parent)
        
        self.gerenciador = gerenciador_veiculos
        
        # Configura janela
        self.title("Cadastro de Veículos")
        self.geometry("1000x600")
        self.resizable(True, True)
        
        # Centraliza janela
        self.transient(parent)
        self.grab_set()
        
        self.criar_interface()
        self.atualizar_tabela()
    
    
    def criar_interface(self):
        """
        Cria interface da janela
        """
        # Frame superior - Botões de ação
        frame_acoes = ttk.Frame(self, padding="10")
        frame_acoes.pack(fill=tk.X)
        
        ttk.Label(
            frame_acoes,
            text="📋 Gestão de Veículos da Frota",
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            frame_acoes,
            text="[+] Novo Veículo",
            command=self.novo_veiculo
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            frame_acoes,
            text="[Edit] Editar",
            command=self.editar_veiculo
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            frame_acoes,
            text="[Save] Salvar Tudo",
            command=self.salvar_dados
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            frame_acoes, 
            text="📥 Importar", 
            command=self.importar_veiculos
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            frame_acoes, 
            text="📤 Exportar", 
            command=self.exportar_veiculos
        ).pack(side=tk.RIGHT, padx=5)

        
        # Frame pesquisa
        frame_pesquisa = ttk.Frame(self, padding="10")
        frame_pesquisa.pack(fill=tk.X)
        
        ttk.Label(frame_pesquisa, text="🔍 Pesquisar:").pack(side=tk.LEFT, padx=(0,5))
        
        self.entrada_pesquisa = ttk.Entry(frame_pesquisa, width=30)
        self.entrada_pesquisa.pack(side=tk.LEFT, padx=5)
        self.entrada_pesquisa.bind('<KeyRelease>', lambda e: self.filtrar_veiculos())
        
        ttk.Button(
            frame_pesquisa,
            text="Limpar",
            command=self.limpar_pesquisa
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame estatísticas
        frame_stats = ttk.Frame(self, padding="10")
        frame_stats.pack(fill=tk.X)
        
        self.label_stats = ttk.Label(frame_stats, text="", font=('Arial', 9))
        self.label_stats.pack()
        
        # Frame tabela
        frame_tabela = ttk.Frame(self, padding="10")
        frame_tabela.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame_tabela, orient=tk.HORIZONTAL)
        
        # Treeview
        self.tree = ttk.Treeview(
            frame_tabela,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode='browse'
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Colunas
        colunas = ['TIPO', 'PLACA', 'DESCRIÇÃO', 'ÚLTIMA KM', 'DATA CADASTRO', 'STATUS']
        
        self.tree['columns'] = colunas
        self.tree.column('#0', width=0, stretch=tk.NO)
        
        larguras = {
            'TIPO': 120,
            'PLACA': 100,
            'DESCRIÇÃO': 250,
            'ÚLTIMA KM': 100,
            'DATA CADASTRO': 120,
            'STATUS': 80
        }
        
        for col in colunas:
            self.tree.column(col, width=larguras.get(col, 100), anchor=tk.W)
            self.tree.heading(col, text=col, anchor=tk.W)
        
        self.tree.bind('<Double-1>', lambda e: self.editar_veiculo())
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Frame inferior - Info
        frame_info = ttk.Frame(self, padding="5")
        frame_info.pack(fill=tk.X)
        
        ttk.Label(
            frame_info,
            text="💡 Dica: Cadastre seus veículos aqui uma única vez. Ao criar manutenção, basta selecionar o veículo e os dados serão preenchidos automaticamente!",
            font=('Arial', 8, 'italic'),
            foreground='gray'
        ).pack()
    
    

    def exportar_veiculos(self):
        """Exporta os veículos para Excel"""
        from tkinter import filedialog, messagebox
        import pandas as pd
        
        veiculos = self.gerenciador.obter_todos()
        if not veiculos:
            messagebox.showwarning("Aviso", "Não há veículos para exportar!")
            return
            
        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Exportar Veículos"
        )
        
        if not caminho:
            return
            
        try:
            df = pd.DataFrame(veiculos)
            df.to_excel(caminho, index=False)
            messagebox.showinfo("Sucesso", f"Veículos exportados com sucesso para:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar veículos:\n{e}")

    def importar_veiculos(self):
        """Importa veículos de uma planilha Excel ou CSV"""
        from tkinter import filedialog, messagebox
        import pandas as pd
        
        caminho = filedialog.askopenfilename(
            filetypes=[
                ("Planilhas", "*.xlsx;*.xls;*.csv"),
                ("Excel", "*.xlsx;*.xls"),
                ("CSV", "*.csv")
            ],
            title="Selecione a planilha de Veículos"
        )
        
        if not caminho:
            return
            
        try:
            if caminho.endswith('.csv'):
                df = pd.read_csv(caminho)
            else:
                df = pd.read_excel(caminho)
                
            # Limpa espaços nas colunas
            df.columns = df.columns.str.strip().str.upper()
            
            # Mapeamento para PLACA
            col_placa = 'PLACA' if 'PLACA' in df.columns else None
            if not col_placa:
                messagebox.showerror("Erro", "A planilha não possui a coluna 'PLACA'.")
                return
                
            # Identifica colunas opcionais
            col_tipo = 'MARCA' if 'MARCA' in df.columns else 'TIPO' if 'TIPO' in df.columns else 'FROTA' if 'FROTA' in df.columns else None
            col_km = 'KM ATUAL' if 'KM ATUAL' in df.columns else 'KM' if 'KM' in df.columns else None
            col_modelo = 'MODELO' if 'MODELO' in df.columns else None
            col_cor = 'COR' if 'COR' in df.columns else None
            
            novos = 0
            atualizados = 0
            
            veiculos_atuais = {v['placa'].upper() for v in self.gerenciador.obter_todos()}
            
            for idx, row in df.iterrows():
                placa = str(row.get(col_placa, '')).strip().upper()
                if not placa or placa == 'NAN': continue
                
                # Prepara dados
                tipo = str(row.get(col_tipo, '')) if col_tipo else 'Indefinido'
                
                desc_parts = []
                if col_modelo and pd.notna(row.get(col_modelo)): desc_parts.append(str(row.get(col_modelo)))
                if col_cor and pd.notna(row.get(col_cor)): desc_parts.append(str(row.get(col_cor)))
                descricao = ' - '.join(desc_parts)
                
                try:
                    km = float(row.get(col_km, 0)) if col_km and pd.notna(row.get(col_km)) else 0
                except:
                    km = 0
                    
                if placa in veiculos_atuais:
                    # Opcional: Atualizar km ou não fazer nada. Aqui apenas ignoramos ou contamos como já existente.
                    pass
                else:
                    self.gerenciador.adicionar_veiculo(tipo, placa, descricao, km)
                    novos += 1
                    
            self.atualizar_tabela()
            self.atualizar_estatisticas()
            messagebox.showinfo("Sucesso", f"Importação concluída!\n\nNovos veículos cadastrados: {novos}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler arquivo:\n{e}")

    def atualizar_tabela(self):
        """
        Atualiza dados na tabela
        """
        # Limpa tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Popula tabela
        veiculos = self.gerenciador.obter_todos()
        
        if not veiculos:
            self.label_stats.config(text="📊 Nenhum veículo cadastrado ainda")
            return
        
        for veiculo in veiculos:
            valores = [
                veiculo.get('tipo_veiculo', ''),
                veiculo.get('placa', ''),
                veiculo.get('descricao', ''),
                veiculo.get('ultima_km', '0'),
                veiculo.get('data_cadastro', ''),
                'ATIVO' if veiculo.get('ativo', False) else 'INATIVO'
            ]
            
            # Define cor baseada no status
            tag = 'ativo' if veiculo.get('ativo', False) else 'inativo'
            
            # O tag escondido guardará a placa para edição
            self.tree.insert('', tk.END, values=valores, tags=(veiculo.get('placa'), tag))
        
        # Configura cores
        self.tree.tag_configure('ativo', background='#d1e7dd')
        self.tree.tag_configure('inativo', background='#f8d7da')
        
        # Atualiza estatísticas
        self.atualizar_estatisticas()
    
    
    def atualizar_estatisticas(self):
        """
        Atualiza estatísticas
        """
        stats = self.gerenciador.obter_estatisticas()
        
        texto = f"📊 Total: {stats['total']} | ✅ Ativos: {stats['ativos']} | ❌ Inativos: {stats['inativos']}"
        
        if stats['por_tipo']:
            texto += " | Por Tipo: "
            tipos_texto = [f"{tipo}: {qtd}" for tipo, qtd in stats['por_tipo'].items()]
            texto += ", ".join(tipos_texto)
        
        self.label_stats.config(text=texto)
    
    
    def novo_veiculo(self):
        """
        Abre formulário para novo veículo
        """
        FormularioVeiculo(self, self.gerenciador, callback=self.atualizar_tabela)
    
    
    def editar_veiculo(self):
        """
        Edita veículo selecionado
        """
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um veículo para editar")
            return
        
        item = self.tree.item(selecao[0])
        placa = item['tags'][0] if item['tags'] else None
        
        if placa:
            veiculo = self.gerenciador.obter_veiculo_por_placa(placa)
            if veiculo:
                FormularioVeiculo(
                    self,
                    self.gerenciador,
                    veiculo=veiculo,
                    placa_antiga=placa,
                    callback=self.atualizar_tabela
                )
    
    
    def salvar_dados(self):
        """
        Salva cadastro de veículos (Legado, o novo salva automaticamente a cada ação)
        """
        messagebox.showinfo("Sucesso", "O sistema salva automaticamente cada alteração no banco de dados!")
        
    
    def filtrar_veiculos(self):
        """
        Filtra veículos conforme texto digitado na pesquisa
        """
        termo = self.entrada_pesquisa.get().upper().strip()
        
        # Limpa tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        veiculos = self.gerenciador.obter_todos()
        
        # Se não há termo, mostra todos
        if not termo:
            self.atualizar_tabela()
            return
        
        # Filtra por placa, tipo ou descrição
        veiculos_filtrados = [
            v for v in veiculos 
            if termo in str(v.get('placa', '')).upper() or 
               termo in str(v.get('tipo_veiculo', '')).upper() or 
               termo in str(v.get('descricao', '')).upper()
        ]
        
        if not veiculos_filtrados:
            self.label_stats.config(text="❌ Nenhum veículo encontrado")
            return
        
        # Popula tabela filtrada
        for veiculo in veiculos_filtrados:
            valores = [
                veiculo.get('tipo_veiculo', ''),
                veiculo.get('placa', ''),
                veiculo.get('descricao', ''),
                veiculo.get('ultima_km', '0'),
                veiculo.get('data_cadastro', ''),
                'ATIVO' if veiculo.get('ativo', False) else 'INATIVO'
            ]
            
            tag = 'ativo' if veiculo.get('ativo', False) else 'inativo'
            self.tree.insert('', tk.END, values=valores, tags=(veiculo.get('placa'), tag))
        
        # Atualiza estatísticas
        self.label_stats.config(
            text=f"🔍 {len(veiculos_filtrados)} veículo(s) encontrado(s) de {len(veiculos)} total"
        )
    
    
    def limpar_pesquisa(self):
        """
        Limpa o campo de pesquisa e mostra todos os veículos
        """
        self.entrada_pesquisa.delete(0, tk.END)
        self.atualizar_tabela()
        

class FormularioVeiculo(tk.Toplevel):
    """
    Formulário para adicionar/editar veículo
    """
    
    def __init__(self, parent, gerenciador, veiculo=None, placa_antiga=None, callback=None):
        super().__init__(parent)
        
        self.gerenciador = gerenciador
        self.veiculo = veiculo
        self.placa_antiga = placa_antiga
        self.callback = callback
        
        # Configura janela
        self.title("Novo Veículo" if veiculo is None else "Editar Veículo")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Centraliza janela
        self.transient(parent)
        self.grab_set()
        
        self.criar_formulario()
        
        # Se é edição, preenche dados
        if veiculo is not None:
            self.preencher_dados(veiculo)
    
    
    def criar_formulario(self):
        """
        Cria formulário
        """
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = "Cadastrar Novo Veículo" if self.veiculo is None else "Editar Veículo"
        ttk.Label(
            main_frame,
            text=titulo,
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Tipo de Veículo
        ttk.Label(main_frame, text="Tipo de Veículo:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.combo_tipo = ttk.Combobox(
            main_frame,
            width=38,
            values=['CAVALO', 'CARRETA 1', 'CARRETA 2', 'BUG 1', 'BUG 2', 'LS'],
            state='readonly'
        )
        self.combo_tipo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Placa
        ttk.Label(main_frame, text="Placa:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.entry_placa = ttk.Entry(main_frame, width=40)
        self.entry_placa.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Descrição
        ttk.Label(main_frame, text="Descrição:", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.entry_descricao = ttk.Entry(main_frame, width=40)
        self.entry_descricao.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(
            main_frame,
            text="(Ex: Volvo FH 540, Scania R450, etc)",
            font=('Arial', 8, 'italic'),
            foreground='gray'
        ).grid(row=4, column=1, sticky=tk.W, padx=5)
        
        # KM Inicial (só para novo veículo)
        if self.veiculo is None:
            ttk.Label(main_frame, text="KM Inicial:", font=('Arial', 10, 'bold')).grid(
                row=5, column=0, sticky=tk.W, pady=5
            )
            self.entry_km = ttk.Entry(main_frame, width=40)
            self.entry_km.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
            self.entry_km.insert(0, "0")
        
        # Status (só para edição)
        if self.veiculo is not None:
            ttk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(
                row=5, column=0, sticky=tk.W, pady=5
            )
            self.combo_status = ttk.Combobox(
                main_frame,
                width=38,
                values=['ATIVO', 'INATIVO'],
                state='readonly'
            )
            self.combo_status.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            frame_botoes,
            text="[Save] Salvar",
            command=self.salvar,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_botoes,
            text="[X] Cancelar",
            command=self.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    
    def preencher_dados(self, veiculo):
        """
        Preenche formulário com dados existentes
        """
        self.combo_tipo.set(veiculo.get('tipo_veiculo', ''))
        self.entry_placa.insert(0, veiculo.get('placa', ''))
        self.entry_descricao.insert(0, veiculo.get('descricao', ''))
        
        if hasattr(self, 'combo_status'):
            status = 'ATIVO' if veiculo.get('ativo', False) else 'INATIVO'
            self.combo_status.set(status)
    
    
    def salvar(self):
        """
        Salva veículo
        """
        # Valida campos
        tipo = self.combo_tipo.get()
        placa = self.entry_placa.get().strip()
        descricao = self.entry_descricao.get().strip()
        
        if not tipo:
            messagebox.showerror("Erro", "Selecione o tipo de veículo")
            return
        
        if not placa:
            messagebox.showerror("Erro", "Informe a placa do veículo")
            return
        
        # Novo veículo
        if self.veiculo is None:
            km_inicial = self.entry_km.get().strip()
            try:
                km_inicial = float(km_inicial) if km_inicial else 0
            except:
                km_inicial = 0
            
            sucesso, mensagem = self.gerenciador.adicionar_veiculo(
                tipo, placa, descricao, km_inicial
            )
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erro", mensagem)
        
        # Editar veículo
        else:
            ativo = self.combo_status.get() == 'ATIVO'
            
            sucesso, mensagem = self.gerenciador.atualizar_veiculo(
                self.placa_antiga, tipo, placa, descricao, ativo
            )
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erro", mensagem)
