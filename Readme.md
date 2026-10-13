# 🚛 Sistema de Manutenção ALS

Sistema completo e profissional para gerenciamento de manutenção de veículos da frota ALS.

## 🌟 Destaques do Sistema

### ✨ Funcionalidades Principais
- 📊 **Dias Correndo Automáticos**: Conta dias até hoje para veículos sem data de saída
- 🔄 **Auto-Preenchimento**: Data de saída preenchida automaticamente ao finalizar
- 📈 **Ordenação Inteligente**: EM SERVIÇO sempre aparece primeiro
- 💾 **Backup Automático**: Cópia de segurança a cada alteração
- 📄 **Relatórios Múltiplos**: Excel, PDF, Word e TXT
- 🎨 **Interface Moderna**: Visual limpo e intuitivo
- 🔍 **Filtros Avançados**: Busca por placa, veículo, status, datas
- 📱 **100% Standalone**: Não precisa instalar nada, apenas executar

## 📦 Conteúdo do Sistema

### Banco de Dados (Já Pré-Carregado)
O sistema já vem com **141 veículos cadastrados**:
- 🚛 **39 Cavalos** (1 vazio)
- 🚚 **46 Carretas 1 Eixo**
- 🚚 **19 Carretas 2 Eixos** (5 vazias)
- 🐛 **21 Bugs** (diversos tipos)
- 🚗 **6 LS**
- ➕ Outros veículos

### Estrutura de Pastas
```
Sistema Manutenção ALS/
├── data/               # Banco de dados e arquivos de configuração
│   ├── sistema_als.db  # Banco SQLite com todos os veículos
│   └── ...
├── img/                # Imagens e logo
├── backup/             # Backups automáticos
├── output/             # Relatórios gerados
└── src/                # Código fonte do sistema
```

## 🚀 Como Gerar o Executável

1. **Execute o arquivo**: `GERAR_EXECUTAVEL.bat`
2. Aguarde a compilação (pode levar alguns minutos)
3. O executável estará em: `dist\SistemaManutencaoALS.exe`

## 💡 Uso do Sistema

### 🚀 Primeiro Uso
1. Execute o arquivo `SistemaManutencaoALS.exe`
2. O sistema já vem com todos os veículos cadastrados
3. Não é necessário importar ou configurar nada
4. Comece a usar imediatamente!

### 📋 Funcionalidades Detalhadas

#### 1️⃣ **Gestão de Manutenções**

**Novo Registro:**
- Clique em "➕ Novo Registro"
- Preencha os campos (Data, Placa, KM, Veículo, Destino, Serviço)
- Status e Dias são calculados automaticamente
- Data de entrada é obrigatória

**Editar Registro:**
- Selecione um registro na tabela
- Clique em "✏️ Editar"
- Modifique os campos necessários
- Salve as alterações

**Excluir Registro:**
- Selecione um ou mais registros
- Use "🗑️ Excluir Selecionado" para um registro
- Use "🗑️❌ Excluir Múltiplos" para vários registros

#### 2️⃣ **Dias Correndo (Automático)**

**Como funciona:**
- Veículos **sem data de saída** → Conta dias até HOJE
- Veículos **com data de saída** → Período fechado
- Atualização automática a cada abertura do sistema

**Exemplo prático:**
```
Veículo: CAVALO RLK7H02
Entrada: 18/11/2025
Saída: (vazio)

Hoje (09/12): 22 dias ✅
Amanhã (10/12): 23 dias ✅
Quando finalizar: Total de dias do período
```

#### 3️⃣ **Auto-Preenchimento de Data de Saída**

**Funcionalidade inteligente:**
- Ao mudar status para "FINALIZADO"
- Se data de saída estiver vazia
- Sistema preenche automaticamente com a data de hoje
- Impossível esquecer de registrar quando terminou!

#### 4️⃣ **Ordenação Inteligente**

**Visualização otimizada:**
- 🔧 **EM SERVIÇO** sempre aparece PRIMEIRO
- ✅ **FINALIZADO** aparece depois
- Dentro de cada grupo: ordem cronológica (mais recente primeiro)
- Mantém ordenação mesmo com filtros

#### 5️⃣ **Filtros de Busca**

**Campos disponíveis:**
- 🔍 Placa
- 🚛 Veículo
- 📊 Status (EM SERVIÇO / FINALIZADO)
- 📅 Data Entrada
- 📅 Data Saída

**Como usar:**
1. Preencha os campos de filtro desejados
2. Clique em "🔍 Buscar"
3. Use "🧹 Limpar" para remover filtros

#### 6️⃣ **Relatórios**

**Clique em "📊 Relatório" e escolha o formato:**

**📊 Excel (.xlsx):**
- Planilha completa com todas as colunas
- Nome da aba: "Manutenção ALS"
- Estatísticas incluídas
- Pronto para análises

**📄 Texto (.txt):**
- Formato simples e leve
- Estatísticas gerais
- Lista completa de registros
- Fácil compartilhamento

**📕 PDF (.pdf):**
- Visual profissional
- Título: "Sistema ALS - Relatório de Manutenção"
- Tabela formatada
- Estatísticas destacadas

**📘 Word (.docx):**
- Documento editável
- Título: "Sistema ALS - Relatório de Manutenção"
- Tabela profissional
- Estatísticas incluídas

**Todos os relatórios:**
- ✅ Salvos automaticamente na pasta `output/`
- ✅ Nome com data/hora (ex: Relatorio_20251209_143022.pdf)
- ✅ Abrem automaticamente após geração
- ✅ Dias correndo recalculados antes de gerar
- ✅ Tempo médio mostrado como número inteiro

#### 7️⃣ **Gestão de Veículos**

**Cadastrar Veículo:**
- Clique em "🚗 Veículos"
- Botão "Novo Veículo"
- Preencha: Placa, Tipo, Descrição, KM
- Sistema valida formato de placa

**Editar/Excluir:**
- Selecione o veículo na lista
- Use os botões correspondentes
- Exclusões são permanentes (com confirmação)

#### 8️⃣ **Gestão de Destinos**

**Cadastrar Destino:**
- Usado para agilizar cadastros
- Evita digitação repetida
- Mantém padrão de nomenclatura

**Recursos:**
- Adicionar novos destinos
- Editar nomes
- Excluir destinos não usados

#### 9️⃣ **Estatísticas em Tempo Real**

**Barra superior mostra:**
- 📊 Total de Registros
- 🔧 Em Serviço (contagem atual)
- ✅ Finalizados (histórico)
- ⏱️ Tempo Médio (em dias inteiros)
- 🚗 Placas Únicas

**Atualização automática:**
- Após adicionar registro
- Após editar registro
- Após excluir registro
- Após aplicar filtros

#### 🔟 **Backup Automático**

**Sistema de segurança:**
- Backup criado a cada alteração importante
- Salvos na pasta `backup/`
- Formato: `database_backup_YYYYMMDD_HHMMSS.db`
- Mantém histórico completo
- Recuperação fácil em caso de problema

### 🎨 Interface do Usuário

**Cores e Indicadores:**
- 🟨 **Amarelo claro**: Registros EM SERVIÇO
- 🟩 **Verde claro**: Registros FINALIZADOS
- 🔵 **Azul**: Botões de ação principal
- 🔴 **Vermelho**: Botões de exclusão (com confirmação)

**Organização:**
- Filtros no topo para busca rápida
- Botões de ação centralizados
- Tabela principal com scroll
- Estatísticas sempre visíveis
- Abas para Registros e Notas

### ⚠️ Regras Importantes

**Validações do Sistema:**
1. **Data de Entrada** é obrigatória
2. **Placa** deve existir no cadastro de veículos
3. **Status FINALIZADO** requer data de saída (preenchida automaticamente)
4. **Exclusões** pedem confirmação
5. **Múltiplas seleções** com Ctrl+Clique ou Shift+Clique

**Comportamentos Automáticos:**
- Status calculado baseado nas datas (mas pode ser alterado manualmente)
- Dias recalculados em tempo real
- Data de saída preenchida ao finalizar
- Backup criado automaticamente
- Relatórios salvos com timestamp

## 📋 Requisitos

- Windows 7 ou superior
- Python 3.8+ (apenas para desenvolvimento)
- O executável NÃO precisa de Python instalado

## 🔧 Desenvolvimento

### Instalar Dependências
```bash
pip install -r requirements.txt
```

### Executar em Modo Desenvolvimento
```bash
python src/main.py
```

## � Especificações Técnicas

### **Arquitetura:**
- **Linguagem**: Python 3.13
- **Interface**: Tkinter (GUI nativa)
- **Banco de Dados**: SQLite3
- **Relatórios**: ReportLab (PDF), python-docx (Word), openpyxl (Excel)
- **Distribuição**: PyInstaller (executável único)

### **Bibliotecas Principais:**
```
pandas>=2.0.0          # Manipulação de dados
reportlab>=3.6.0       # Geração de PDF
python-docx>=0.8.11    # Geração de Word
openpyxl>=3.1.0        # Geração de Excel
Pillow>=10.0.0         # Manipulação de imagens
ttkbootstrap>=1.10.0   # Temas modernos
```

### **Estrutura do Código:**

```
src/
├── main.py              # Interface principal + formulários
├── database.py          # Gerenciador do banco SQLite
├── veiculos.py          # CRUD de veículos
├── destinos.py          # CRUD de destinos
├── utils.py             # Funções auxiliares + relatórios
├── interface_veiculos.py   # Janela de gestão de veículos
└── interface_destinos.py   # Janela de gestão de destinos
```

### **Recursos Implementados:**

#### **Cálculo de Dias:**
- `calcular_dias_manutencao()`: Conta dias correndo até hoje
- Atualização automática em tempo real
- Tratamento de datas vazias
- Mínimo de 1 dia (mesmo dia entrada/saída)

#### **Gestão de Dados:**
- Database-First Architecture (SQLite como fonte única)
- DataFrame como cache de leitura
- Sincronização automática (SQLite → COMMIT → Reload)
- Transações seguras com rollback

#### **Validações:**
- Formato de placa brasileiro
- Datas no formato DD/MM/YYYY
- Campos obrigatórios destacados
- Confirmação para exclusões

## 📊 Estatísticas do Sistema

### **Capacidade:**
- ✅ Suporta milhares de registros
- ✅ Backup automático ilimitado
- ✅ Histórico completo preservado
- ✅ Performance otimizada

### **Testes Realizados:**
- ✅ 12 funcionalidades testadas
- ✅ 100% de taxa de sucesso
- ✅ Todos os CRUD funcionando
- ✅ Relatórios validados
- ✅ Dias correndo verificados

## 🎯 Casos de Uso

### **Cenário 1: Novo Veículo em Manutenção**
```
1. Clique "➕ Novo Registro"
2. Preencha data entrada: 09/12/2025
3. Selecione placa do veículo
4. Escolha destino e serviço
5. Deixe data saída vazia (ainda em manutenção)
6. Salve

Resultado: Sistema mostra "1 dia" hoje, "2 dias" amanhã, etc.
```

### **Cenário 2: Finalizar Manutenção**
```
1. Selecione o registro
2. Clique "✏️ Editar"
3. Mude status para "FINALIZADO"
4. Sistema preenche data saída automaticamente
5. Salve

Resultado: Total de dias é fixado no período
```

### **Cenário 3: Gerar Relatório Mensal**
```
1. Use filtros para período desejado (ex: 01/12 a 31/12)
2. Clique "📊 Relatório"
3. Escolha "📊 Excel"
4. Arquivo abre automaticamente

Resultado: Planilha com todos os dados filtrados
```

### **Cenário 4: Consultar Veículos em Manutenção**
```
1. Abra o sistema
2. Primeiros registros mostram EM SERVIÇO
3. Veja dias correndo atualizados
4. Identifique rapidamente o que precisa atenção

Resultado: Visão clara do status atual
```

## 📝 Notas Importantes

### ✅ **Pronto para Uso:**
- Banco de dados pré-carregado com 141 veículos
- Cavalos vazios identificados
- Carretas 2 eixos vazias identificadas
- Sistema 100% funcional
- Não requer instalação adicional

### 🔒 **Segurança:**
- Backups automáticos preservam histórico
- Confirmação para exclusões irreversíveis
- Dados salvos localmente (privacidade)
- Sem necessidade de internet

### 🚀 **Performance:**
- Inicialização rápida (< 2 segundos)
- Interface responsiva
- Geração de relatórios instantânea
- Filtros em tempo real

### 💡 **Suporte:**
- Documentação completa incluída
- RELATORIO_VERIFICACAO.md com testes
- FUNCIONALIDADE_DIAS_CORRENDO.md detalhada
- INSTRUCOES_DISTRIBUICAO.md para instalação

## 👨‍💼 Para Distribuição

### **Opção 1: Executável Standalone**
```
1. Copie a pasta "SistemaALS_Atualizado/"
2. Envie para o usuário final
3. Execute "SistemaManutencaoALS.exe"
4. Pronto!
```

### **Opção 2: Apenas Executável**
```
1. Copie "SistemaManutencaoALS.exe"
2. Sistema cria pastas necessárias automaticamente:
   - data/ (banco de dados)
   - backup/ (backups)
   - output/ (relatórios)
   - img/ (se disponível)
```

### **Requisitos do Usuário Final:**
- ✅ Windows 7 ou superior (32 ou 64 bits)
- ✅ Nenhuma instalação adicional necessária
- ✅ Não precisa Python instalado
- ✅ Não precisa permissões especiais
- ✅ Funciona offline

## 🆘 Resolução de Problemas

### **Problema: Relatórios não abrem automaticamente**
**Solução**: Verifique se há um leitor de PDF/Excel instalado. Os arquivos estão salvos em `output/`

### **Problema: Dias não atualizam**
**Solução**: Clique no botão "🔄 Atualizar" ou reabra o sistema

### **Problema: Erro ao excluir veículo/destino**
**Solução**: Certifique-se que não há registros usando esse veículo/destino

### **Problema: Backup ocupando espaço**
**Solução**: Arquivos antigos em `backup/` podem ser deletados manualmente (mantenha os recentes)

---

## 📞 Informações de Desenvolvimento

**Sistema**: Sistema de Gestão de Manutenção ALS  
**Versão**: 2.0 (Dezembro 2025)  
**Desenvolvido para**: ALS Transportes  
**Plataforma**: Windows  
**Licença**: Proprietário  

---

**Desenvolvido com ❤️ para ALS Transportes**
