# Sistema de Gestão de Manutenção — ALS Transportes

Aplicação desktop para Windows que controla as manutenções da frota da ALS Transportes: entrada e saída de veículos na oficina, tempo parado, cadastros de veículos e destinos, anotações, relatórios e um dashboard analítico.

- **Plataforma:** Windows, com banco SQLite local. O usuário final não precisa instalar Python.
- **Distribuição:** instalador (Inno Setup) gerado pelo GitHub Actions e atualização automática pelas GitHub Releases.
- **Versão:** definida pela tag `vX.Y.Z` no momento do release (veja [CI/CD](#5-cicd-e-release)).

---

## Sumário

1. [Stack](#1-stack)
2. [Arquitetura](#2-arquitetura)
3. [Estrutura de pastas](#3-estrutura-de-pastas)
4. [Executar em desenvolvimento](#4-executar-em-desenvolvimento)
5. [CI/CD e release](#5-cicd-e-release)
6. [Atualização automática](#6-atualização-automática)
7. [Regras de negócio](#7-regras-de-negócio)
8. [Funcionalidades](#8-funcionalidades)
9. [Dashboard analítico](#9-dashboard-analítico)
10. [Dados, logs e backups](#10-dados-logs-e-backups)
11. [Testes](#11-testes)
12. [Solução de problemas](#12-solução-de-problemas)
13. [Pendências conhecidas](#13-pendências-conhecidas)

---

## 1. Stack

| Camada | Tecnologia |
| :--- | :--- |
| Linguagem | Python 3.12 |
| Interface desktop | [PySide6](https://doc.qt.io/qtforpython-6/) (Qt 6) + [PySide6-Fluent-Widgets](https://qfluentwidgets.com/), no visual Windows 11 |
| Dashboard | [Streamlit](https://streamlit.io/) + [Plotly](https://plotly.com/python/), exibido dentro do app por `QWebEngineView` |
| Persistência | SQLite (modo WAL) via **SQLAlchemy 2.0** ORM |
| Dados | pandas |
| Exportação | openpyxl (Excel), ReportLab (PDF), python-docx (Word) |
| Empacotamento | PyInstaller (`--onedir --windowed`) |
| Instalador | Inno Setup 6 ([installer.iss](installer.iss)) |
| CI/CD | GitHub Actions ([build-release.yml](.github/workflows/build-release.yml)) |
| Testes | pytest |

### Design

- **Fluent Design:** tema **cinza suave** (padrão) e **modo escuro**, alternados no menu lateral.
- **Estilos centralizados:** os estilos ficam em [src/views_qt/theme_styles.py](src/views_qt/theme_styles.py). Ali estão o `ContrastCard` (cards de alto contraste com borda de acento) e o QSS das tabelas, nas versões cinza e escura.
- **Cor de acento:** verde ALS `#4CAF50`, usada no app e no tema do Streamlit.
- **Ícones:** vetoriais (Fluent no desktop, Material no Streamlit), sem emojis.
- **Splash screen:** tem animação e verifica atualizações na abertura ([splash_screen.py](src/views_qt/splash_screen.py)).

---

## 2. Arquitetura

O projeto segue **MVC com uma camada de Services** para as regras de negócio:

```
View (PySide6 / Streamlit)
   │  eventos da interface
   ▼
Controller          → apenas encaminha as ações
   │
   ▼
Service             → regras de negócio (uma função por arquivo)
   │
   ▼
Model (SQLAlchemy)  → entidades ORM e consultas
   │
   ▼
SQLite (data/sistema_als.db, WAL)
```

- **Models** ([src/models/](src/models/)): `database.py` gerencia a engine, as sessões e os PRAGMAs do SQLite (`journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout`). `entities.py` mapeia Veículo, Manutenção, Destino e Nota. Há um `*_model.py` por entidade.
- **Controllers** ([src/controllers/](src/controllers/)): não têm regra própria. Delegam para os services.
- **Services** ([src/services/](src/services/)): cada regra fica no próprio arquivo e com nome explícito, como `calcular_dias_manutencao.py` e `normalizar_status.py`. Isso facilita testar e localizar cada regra.
- **Views** ([src/views_qt/](src/views_qt/)): telas PySide6.

### Integração com o Streamlit

O dashboard **não é um site separado**. A aba *Dashboard* inicia o próprio executável como subprocesso:

```
SistemaManutencaoALS.exe --run-streamlit   (ou: python src/main.py --run-streamlit)
```

[main.py](src/main.py) detecta esse argumento e chama o CLI do Streamlit, que sobe sem janela de console em `http://localhost:8505`. A tela exibe esse endereço num `QWebEngineView`.

O Streamlit usa os **mesmos Controllers e Services** do app desktop, então os números são os mesmos nas duas telas. Ele lê o mesmo banco, e o modo WAL permite leitura e escrita simultâneas. O processo é encerrado (`taskkill /T`) quando o app fecha ou antes de uma atualização.

---

## 3. Estrutura de pastas

```text
Planilha-ALS-/
├── .github/workflows/
│   └── build-release.yml        # pipeline de build, testes e release
├── data/
│   ├── sistema_als.db           # banco SQLite
│   ├── config_colunas.txt
│   └── logs/                    # als.log e faulthandler.log (não versionado)
├── img/                         # logo e ícone (.png / .ico)
├── src/
│   ├── main.py                  # ponto de entrada (app Qt ou modo --run-streamlit)
│   ├── app_qt.py                # QApplication, log, instância única, splash
│   ├── config.py                # caminhos, APP_VERSION, repositório de atualização
│   ├── dashboard_streamlit.py   # dashboard analítico
│   ├── importador.py            # importação de planilhas
│   ├── utils.py                 # geração de PDF/Word e utilitários
│   ├── models/                  # M — ORM e acesso a dados
│   ├── controllers/             # C — veículo, manutenção, destino, nota
│   ├── services/                # regras de negócio
│   │   ├── manutencao/          #   status, cálculo de dias, importação, estatísticas
│   │   ├── veiculo/             #   cadastro, KM, formatação de placas
│   │   ├── destino/             #   cadastro e destinos padrão
│   │   ├── nota/                #   anotações
│   │   ├── dashboard/           #   KPIs, aging, ranking de dias parados
│   │   ├── export_service.py    #   exportação Excel/PDF
│   │   └── updater_service.py   #   atualização automática
│   ├── views_qt/                # V — interface atual (PySide6)
│   ├── views/                   # interface antiga (Tkinter) — legado
│   └── main_legacy_tkinter.py   # app antigo — legado, fora do fluxo atual
├── tests/                       # testes pytest
├── installer.iss                # script do Inno Setup
├── SISTEMA_ALS.bat              # menu local: rodar, gerar .exe, gerar instalador
├── requirements.txt
└── pytest.ini
```

O app cria `backup/` e `output/` na primeira execução, e as duas pastas ficam fora do git.

---

## 4. Executar em desenvolvimento

Pré-requisitos: Windows, Python 3.12 e Git.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python src/main.py
```

Também dá para usar o menu [SISTEMA_ALS.bat](SISTEMA_ALS.bat), que instala as dependências que faltarem e oferece estas opções:

| Opção | O que faz |
| :--- | :--- |
| `1` | Inicia o sistema |
| `2` | Gera o executável em `SistemaALS_Atualizado/` (PyInstaller) |
| `3` | Gera o instalador em `dist_installer/` (exige o Inno Setup 6: `winget install JRSoftware.InnoSetup`) |

Para abrir só o dashboard no navegador:

```bash
python src/main.py --run-streamlit
```

---

## 5. CI/CD e release

O workflow [build-release.yml](.github/workflows/build-release.yml) roda em `windows-latest`.

**Gatilhos**
- `push` de tag `v*`: faz o build completo e publica a GitHub Release.
- `workflow_dispatch` (manual): faz build e testes e guarda o instalador como artefato, mas **não** publica Release.

**Etapas**

1. Checkout e Python 3.12, com cache do pip.
2. `pip install -r requirements.txt` e pytest.
3. **Sincroniza a versão:** a tag (`v1.0.4` → `1.0.4`) é gravada em `APP_VERSION` ([config.py](src/config.py)) e em `MyAppVersion` ([installer.iss](installer.iss)).
4. **Testes:** `pytest` com `QT_QPA_PLATFORM=offscreen`. Se algum falhar, o release é interrompido.
5. **PyInstaller** `--onedir --windowed`, com `--collect-all streamlit/plotly` e `--hidden-import` para PySide6, qfluentwidgets, SQLAlchemy e outros.
6. **Monta a pasta** `SistemaALS_Atualizado/` (exe, `_internal/`, `img/`, `data/`).
7. **Instala o Inno Setup** via Chocolatey e compila `Instalador_SistemaALS_Setup.exe`.
8. **Validação:** falha se o instalador tiver menos de 20 MB, sinal de que o payload não foi empacotado.
9. **Upload** do instalador como artefato do workflow.
10. **Publica a GitHub Release** com o instalador e notas geradas automaticamente.

**Como lançar uma versão**

```bash
git tag v1.0.4
git push origin v1.0.4
```

Para tornar a atualização **obrigatória**, coloque `[OBRIGATORIA]` no título ou nas notas da Release.

**O que o instalador faz** ([installer.iss](installer.iss))

- Instala em `C:\Sistema ALS` sem exigir administrador (`PrivilegesRequired=lowest`).
- Usa um `AppId` fixo, então reinstalar substitui a versão anterior.
- **Preserva os dados:** o banco só é copiado se ainda não existir (`onlyifdoesntexist`). As pastas `data`, `backup` e `output` não são tocadas.
- Apaga o `_internal/` antigo antes de copiar o novo, para não sobrar DLL de versão anterior.
- Fecha o app se ele estiver aberto (`CloseApplications=force`) e o reabre ao final no modo silencioso.

---

## 6. Atualização automática

Implementada em [updater_service.py](src/services/updater_service.py), a partir da splash screen:

1. Consulta `GET /repos/LucasHennCarniel/ALS-Sistema-/releases/latest` com timeout de 5 s. Sem internet, segue sem atualizar.
2. Compara a tag com `APP_VERSION` e verifica se a Release tem a marca `[OBRIGATORIA]`.
3. Faz **backup** do banco em `backup/sistema_als_pre_update_<data>.db`.
4. Baixa o instalador, tentando de novo em caso de falha e **retomando o download** (HTTP `Range`) de onde parou.
5. Libera os recursos: fecha a engine do SQLite e encerra o servidor Streamlit.
6. Executa o instalador com `/SILENT /SUPPRESSMSGBOXES /NORESTART /DIR="<pasta atual>" /LOG=...` e encerra o app.
7. Grava um **marcador de instalação** (PID e versão). Uma cópia antiga aberta durante a troca de arquivos espera em vez de abrir.
8. Lê o log do Inno Setup para confirmar se a instalação terminou com sucesso.

> **Atualizar o app não é o mesmo que sincronizar dados.** Cada computador tem o próprio banco SQLite local. A atualização troca apenas o programa.

---

## 7. Regras de negócio

### Status

Definidos em [status.py](src/services/manutencao/status.py), a fonte única para formulários, filtros, cards e dashboard:

| Status | Veículo parado? |
| :--- | :---: |
| `AGENDADO` | Não |
| `EM MANUTENÇÃO` | Sim |
| `FINALIZADO` | Não |
| `SINISTRO` | Sim |

Status antigos (`EM SERVIÇO`, `AGUARDANDO PEÇAS`, `PREVENTIVA`, `CORRETIVA`, etc.) são convertidos na leitura, sem alterar o banco.

Quando o status fica em branco, ele é definido automaticamente ([recalcular_campos.py](src/services/manutencao/recalcular_campos.py)):

- com data de saída → `FINALIZADO`
- só com data de entrada → `EM MANUTENÇÃO`
- sem datas → `AGENDADO`

### Dias em manutenção

- **Fórmula:** dias corridos = `data de saída − data de entrada`, sem contar o dia de entrada e nunca negativo.
- **Sem data de saída:** a conta vai até **hoje**, então o número cresce a cada dia.
- **Valor sempre atualizado:** telas, dashboard e relatórios recalculam o valor na hora ([calcular_dias_dinamicos.py](src/services/manutencao/calcular_dias_dinamicos.py)), sem depender do que foi gravado no banco.
- **Exceções:** registros `AGENDADO`, ou `FINALIZADO` sem data de saída, mantêm o valor gravado.

### Validações

- Datas no formato `DD/MM/AAAA`.
- A placa precisa existir no cadastro de veículos.
- Exclusões pedem confirmação.

---

## 8. Funcionalidades

Navegação lateral do app:

| Aba | Recursos |
| :--- | :--- |
| **Manutenções** | Cadastro, edição e exclusão (também em lote, com `Ctrl`/`Shift` + clique), filtros, cards de indicadores, importação de planilhas (`.xlsx`, `.xls`, `.csv`), exportação para Excel e PDF |
| **Dashboard** | Indicadores de manutenção e panorama da frota em Streamlit (detalhes na [seção 9](#9-dashboard-analítico)) |
| **Veículos** | Cadastro de placa, tipo, descrição e KM |
| **Anotações** | Notas livres |
| **Configurações** | Preferências e alternância de tema (cinza / escuro) |

Os relatórios são salvos no local escolhido pelo usuário. A pasta padrão é `output/`.

---

## 9. Dashboard analítico

O dashboard fica em [src/dashboard_streamlit.py](src/dashboard_streamlit.py), feito com **Streamlit + Plotly**, e aparece na aba *Dashboard* do app. A forma como o processo sobe está em [Integração com o Streamlit](#integração-com-o-streamlit).

### Como funciona

| Item | Detalhe |
| :--- | :--- |
| Servidor | `http://localhost:8505`, sem console, iniciado só quando a aba é aberta |
| Exibição | `QWebEngineView` dentro da janela Qt ([dashboard_view.py](src/views_qt/dashboard_view.py)) |
| Origem dos dados | Os mesmos Controllers do app (`ManutencaoController`, `VeiculoController`, `DestinoController`, `NotaController`) |
| Cálculos | Services em [src/services/dashboard/](src/services/dashboard/), escritos em pandas |
| Cache | `@st.cache_data(ttl=20)`: os dados são relidos do banco no máximo a cada 20 s |
| Atualizar | Botão **Atualizar Dados** (limpa o cache) ou botão de recarregar na aba do app |
| Acesso ao banco | Somente leitura. O modo WAL permite ler enquanto o app grava |

### Abas

O dashboard tem duas abas. Se ainda não houver manutenções cadastradas, **Panorama da Frota** aparece primeiro.

#### Indicadores de Manutenção

**Filtros.** A barra lateral tem busca rápida (placa, veículo, serviço, destino, OF), placa, tipo de veículo, destino programado e período de entrada. Na área principal, uma seleção de **status** com a contagem de cada um.

**KPIs** ([calcular_kpis_manutencao.py](src/services/dashboard/calcular_kpis_manutencao.py))

| KPI | Cálculo | Respeita filtros? |
| :--- | :--- | :---: |
| **Veículos Parados** | Placas distintas com registro `EM MANUTENÇÃO` ou `SINISTRO` | Não (frota inteira) |
| **Disponibilidade** | `1 − parados ÷ veículos ativos`, em % | Não (frota inteira) |
| **Reparo Médio** | Média de dias dos registros `FINALIZADO` | Sim |
| **Mais Antigo** | Registro em aberto há mais dias, com a placa | Sim |
| **Reincidentes** | Placas com 3 ou mais entradas nos últimos 90 dias | Sim |

**Gráficos e tabelas**

| Visual | Service | O que mostra |
| :--- | :--- | :--- |
| Distribuição por status | [contar_por_status.py](src/services/dashboard/contar_por_status.py) | Barra única empilhada com a proporção de cada status |
| Em Aberto por Tempo Parado | [agrupar_por_faixa_aging.py](src/services/dashboard/agrupar_por_faixa_aging.py) | Registros em aberto nas faixas 0–3, 4–7, 8–15 e 16+ dias |
| Top 10 Placas por Dias Parados | [ranking_dias_parados.py](src/services/dashboard/ranking_dias_parados.py) | Soma dos dias de todos os registros da placa no filtro, com o número de ocorrências |
| Manutenções por Tipo de Veículo | — | Os 10 tipos com mais registros |
| Maiores Tempos em Aberto | — | Os 8 registros abertos há mais tempo |
| Registros Filtrados | — | Tabela completa com os dias já atualizados |

Os dias vêm de [calcular_dias_corridos.py](src/services/dashboard/calcular_dias_corridos.py), que reaproveita a mesma regra da tabela do app (`calcular_dias_dinamicos`). Por isso os números das duas telas batem.

#### Panorama da Frota

- **Filtros:** busca por placa ou descrição, tipo/marca e situação (ativo/inativo).
- **KPIs:** total de veículos, ativos, inativos e número de categorias.
- **Gráficos:** veículos por categoria e situação por categoria (ativo × inativo empilhado).
- **Tabela:** relação dos veículos com placa, tipo, descrição, última KM, data de cadastro e status.

### Visual

| Elemento | Definição |
| :--- | :--- |
| Fundo / painéis | `#D5DFE8` / `#EAEFF5`, com borda `#94A3B8` |
| Tema | Passado por argumento ao iniciar o Streamlit (`--theme.primaryColor #4CAF50`, etc.) e completado por CSS próprio no script |
| Cores por status | Agendado `#0284C7` · Em manutenção `#F59E0B` · Finalizado `#4CAF50` · Sinistro `#DC2626` |
| Cores por faixa de tempo | 0–3 verde · 4–7 âmbar · 8–15 laranja · 16+ vermelho |
| Gráficos | Barras horizontais com o valor na ponta. Não há gráfico de pizza |
| Ícones | Material (`:material/...:`) |

### Rodar só o dashboard

```bash
python src/main.py --run-streamlit
```

O Streamlit abre na porta padrão dele (8501). A porta 8505 é a que o app passa ao iniciar o servidor.

---

## 10. Dados, logs e backups

| Caminho | Conteúdo |
| :--- | :--- |
| `data/sistema_als.db` | Banco principal (os arquivos `-wal` e `-shm` são do modo WAL) |
| `data/logs/als.log` | Log da aplicação, que funciona também no `.exe` sem console |
| `data/logs/faulthandler.log` | Pilha das threads em caso de travamento (se a abertura passar de 20 s) |
| `backup/` | Cópias do banco feitas antes de cada atualização |
| `output/` | Relatórios exportados |

Os backups são **locais**. Guarde cópias periódicas do banco fora do computador.

O app permite **só uma instância aberta** por vez (`QLockFile`).

---

## 11. Testes

```bash
pytest
```

Os testes ficam em [tests/](tests/) e cobrem banco, veículos, destinos, notas, status, cálculo de dias, serviços do dashboard, instância única, splash e o updater (comando do instalador e download retomável). O [pytest.ini](pytest.ini) define `pythonpath = .`, então basta rodar `pytest` na raiz. Os testes de interface usam `QT_QPA_PLATFORM=offscreen` no CI.

---

## 12. Solução de problemas

| Situação | O que verificar |
| :--- | :--- |
| App não abre ou fecha sozinho | `data/logs/als.log` e `data/logs/faulthandler.log` |
| "Já existe uma instância aberta" | Feche a outra janela ou finalize o processo `SistemaManutencaoALS.exe` |
| Dashboard fica em "Iniciando servidor" | A porta `8505` pode estar ocupada por outro processo |
| Máquina não recebeu a versão nova | A Release foi publicada (não é rascunho)? O workflow passou? A máquina tem acesso ao GitHub? |
| Atualização falhou no meio | O banco anterior está em `backup/sistema_als_pre_update_*.db`. Rode o instalador da Release manualmente |
| Dados diferentes entre computadores | Esperado: cada instalação tem o próprio banco local |

---

## 13. Pendências conhecidas

- **Banco versionado:** o `data/sistema_als.db` ainda está versionado, apesar de constar no `.gitignore`, e o workflow o empacota no instalador. Antes de publicar Releases, use um banco sem dados reais ou crie o banco vazio na primeira execução, e tire o arquivo do git com `git rm --cached data/sistema_als.db`.
- **Testes só no release:** o CI roda os testes apenas em tags. Um workflow em `push`/`pull_request` na `main` anteciparia os erros.
- **Sem assinatura de código:** o instalador não é assinado, então o Windows SmartScreen pode exibir o aviso de "editor desconhecido".
- **Download sem checksum:** o updater não confere um checksum (SHA-256) do instalador baixado.
- **Versão no repositório desatualizada:** `APP_VERSION` e `MyAppVersion` só são atualizados dentro do CI. No repositório ficam com a última versão definida à mão.
- **Código legado:** `src/views/` e `src/main_legacy_tkinter.py` são do app Tkinter antigo e podem ser removidos quando não forem mais necessários.

---

**Licença:** proprietária — ALS Transportes.
