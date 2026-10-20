# Sistema de Gestão de Manutenção — ALS Transportes
**Documentação funcional e técnica | Base funcional: versão 2.0 (dezembro de 2025) | Atualização da documentação: outubro de 2026**

O **Sistema de Gestão de Manutenção ALS** é uma aplicação desktop desenvolvida para organizar e acompanhar as manutenções da frota da ALS Transportes. A solução centraliza os registros de entrada e saída dos veículos, os serviços realizados, os períodos de permanência em manutenção e os dados necessários para consultas e relatórios.

A aplicação é executada em computadores Windows e utiliza banco de dados SQLite local. A distribuição passou a contar com um instalador, um fluxo de CI/CD configurado no GitHub Actions e um processo de atualização das instalações existentes. Assim, as correções e melhorias podem chegar às máquinas de destino sem o envio manual de um novo executável ou instalador a cada alteração. O usuário final não precisa instalar o Python separadamente.

> **Escopo desta documentação:** as funcionalidades operacionais abaixo foram preservadas da documentação da versão 2.0. A instalação e a distribuição foram atualizadas conforme as melhorias relatadas em outubro de 2026. A atualização automática da aplicação não deve ser confundida com sincronização do banco de dados: compartilhamento de registros entre computadores, acesso remoto e trabalho multiusuário não estão comprovados pelo material disponível.

---

## 1. Visão geral

O objetivo do sistema é substituir controles manuais ou dispersos por um processo padronizado de registro e consulta das manutenções da frota. Entre seus principais recursos estão:

- Cadastro e manutenção dos registros de serviço, com inclusão, edição e exclusão.
- Controle do status de cada manutenção: **Em serviço** ou **Finalizado**.
- Cálculo automático do tempo de permanência do veículo em manutenção.
- Cadastro de veículos e destinos utilizados nos registros.
- Filtros para localização de informações por placa, veículo, status e datas.
- Indicadores operacionais para acompanhamento da frota.
- Exportação de relatórios em Excel, PDF, Word e texto.
- Geração automática de cópias de segurança após alterações relevantes.
- Instalação inicial simplificada por instalador.
- Processo automatizado de integração e entrega com GitHub Actions, reduzindo a necessidade de distribuição manual de novas versões.

### 1.1. Organização da interface

A tela principal reúne filtros de consulta, uma tabela com os registros e indicadores resumidos. A organização foi pensada para priorizar as manutenções em andamento e facilitar o acesso às ações mais frequentes.

Na identificação visual dos registros, são utilizadas as seguintes cores:

| Elemento | Identificação |
| :--- | :--- |
| **Manutenções em andamento** | Fundo amarelo-claro |
| **Manutenções finalizadas** | Fundo verde-claro |
| **Ações principais** | Botões azuis |
| **Exclusões** | Botões vermelhos, com confirmação |

A aplicação também possui abas para **Registros** e **Notas**. O funcionamento detalhado da aba de notas não está especificado no material desta versão.

---

## 2. Gestão dos registros de manutenção

Cada registro representa a passagem de um veículo pelo processo de manutenção. Os dados informados permitem identificar o equipamento, o serviço e o intervalo de tempo em que ele permaneceu em atendimento.

### 2.1. Cadastrar uma manutenção

1. Na tela principal, selecione **Novo Registro**.
2. Informe a **data de entrada**, que é obrigatória.
3. Selecione a **placa** e preencha os dados disponíveis do veículo, incluindo quilometragem, destino e descrição do serviço.
4. Se o veículo ainda estiver em manutenção, mantenha a **data de saída** em branco.
5. Salve o registro.

O sistema calcula o status e os dias de manutenção com base nas informações cadastradas. A placa informada deve corresponder a um veículo existente no cadastro.

### 2.2. Editar uma manutenção

1. Localize o registro na tabela, utilizando os filtros quando necessário.
2. Selecione o item e clique em **Editar**.
3. Atualize os dados desejados.
4. Salve para registrar as alterações.

Esse procedimento pode ser utilizado tanto para corrigir informações quanto para finalizar uma manutenção.

### 2.3. Excluir registros

A aplicação permite excluir um registro individualmente ou selecionar vários para exclusão em lote. Para selecionar diversos itens, utilize `Ctrl + clique` ou `Shift + clique` na tabela.

Antes de concluir a operação, o sistema solicita confirmação. Exclusões devem ser tratadas como definitivas, sendo importante verificar se os registros selecionados estão corretos.

---

## 3. Regras de negócio e comportamentos automáticos

### 3.1. Cálculo dos dias em manutenção

O campo de dias representa o tempo de permanência do veículo no processo de manutenção:

- **Sem data de saída:** o cálculo considera o intervalo entre a data de entrada e a data atual.
- **Com data de saída:** o cálculo considera o intervalo entre a entrada e a saída, sem continuar aumentando nos dias seguintes.
- **Entrada e saída no mesmo dia:** a contagem mínima aplicada pelo sistema é de um dia.

A regra documentada considera o dia inicial na contagem. Por exemplo, um veículo que entrou em `18/11/2025` e continuava em serviço em `09/12/2025` apresenta **22 dias**. Se permanecesse em serviço em `10/12/2025`, apresentaria **23 dias**.

O valor é atualizado durante o uso ou na reabertura/atualização do sistema e é recalculado antes da geração dos relatórios.

### 3.2. Finalização da manutenção

Ao alterar o status de um registro para **Finalizado**, se a data de saída estiver vazia, o sistema a preenche automaticamente com a data atual. A partir desse momento, o total de dias é calculado sobre o período encerrado.

O material original também informa que o status pode ser alterado manualmente. Por isso, a data de saída e o status devem ser conferidos durante a edição para manter a consistência do histórico.

### 3.3. Ordenação dos registros

Na tabela principal, os registros são organizados da seguinte maneira:

1. Manutenções com status **Em serviço** aparecem primeiro.
2. Manutenções com status **Finalizado** aparecem em seguida.
3. Dentro de cada grupo, os itens são exibidos do mais recente para o mais antigo.

Essa ordem é preservada ao aplicar filtros, facilitando a identificação das atividades ainda pendentes.

### 3.4. Validações importantes

| Regra | Comportamento esperado |
| :--- | :--- |
| **Data de entrada** | Campo obrigatório no cadastro da manutenção |
| **Placa** | Deve estar cadastrada na relação de veículos |
| **Formato de placa** | Validado conforme os formatos brasileiros aceitos pelo sistema |
| **Datas** | Informadas no formato `DD/MM/AAAA` |
| **Status Finalizado** | Requer data de saída; caso esteja vazia, é preenchida automaticamente |
| **Exclusão** | Exige confirmação do usuário |

---

## 4. Consultas, filtros e indicadores

### 4.1. Pesquisa de manutenções

Os registros podem ser consultados por placa, veículo, status, data de entrada e data de saída. Os filtros podem ser combinados para restringir os resultados.

Para pesquisar, informe os critérios desejados e selecione **Buscar**. Para retornar à listagem sem filtros, utilize **Limpar**.

### 4.2. Indicadores operacionais

A faixa de indicadores da tela principal apresenta:

| Indicador | Informação apresentada |
| :--- | :--- |
| **Total de registros** | Quantidade de registros considerados na visualização |
| **Em serviço** | Manutenções que permanecem abertas |
| **Finalizados** | Manutenções registradas como concluídas |
| **Tempo médio** | Média de duração das manutenções, exibida em dias inteiros |
| **Placas únicas** | Quantidade de placas distintas consideradas |

Os indicadores são atualizados após a inclusão, edição ou exclusão de registros e também após a aplicação de filtros.

---

## 5. Cadastros auxiliares

### 5.1. Veículos

O cadastro de veículos organiza a identificação dos equipamentos utilizados nos lançamentos de manutenção.

Para incluir um veículo:

1. Acesse **Veículos** e selecione **Novo Veículo**.
2. Preencha placa, tipo, descrição e quilometragem.
3. Confirme os dados e salve.

Veículos existentes podem ser editados ou excluídos pelos comandos da mesma tela. O sistema valida o formato da placa e pode impedir a exclusão de veículos associados a registros de manutenção.

### 5.2. Destinos

O cadastro de destinos permite reutilizar informações recorrentes, reduzindo digitação e padronizando a nomenclatura nos lançamentos.

São disponibilizadas operações para adicionar, editar e excluir destinos. Quando um destino estiver associado a registros existentes, sua exclusão poderá ser bloqueada para preservar a integridade dos dados.

---

## 6. Emissão de relatórios

O sistema exporta dados de manutenção em diferentes formatos, para atender às necessidades de acompanhamento operacional, análise e compartilhamento.

| Formato | Extensão | Aplicação principal |
| :--- | :--- | :--- |
| **Excel** | `.xlsx` | Análise de dados em planilhas, com colunas e estatísticas |
| **PDF** | `.pdf` | Consulta e compartilhamento de relatório com apresentação padronizada |
| **Word** | `.docx` | Edição posterior de um documento com tabela e indicadores |
| **Texto** | `.txt` | Consulta ou compartilhamento em formato simples e leve |

### 6.1. Gerar um relatório

1. Se necessário, aplique os filtros para selecionar o conjunto de registros desejado.
2. Clique em **Relatório** na tela principal.
3. Escolha o formato de exportação.
4. Aguarde a geração e consulte o documento.

Os arquivos são armazenados na pasta `output/`, com data e hora no nome. Exemplo: `Relatorio_20251209_143022.pdf`.

O sistema tenta abrir o relatório automaticamente após sua geração, desde que exista no computador um aplicativo associado ao formato selecionado. Os dias de manutenção são recalculados antes da exportação, e a média é exibida como número inteiro.

---

## 7. Banco de dados e informações iniciais

A versão documentada utiliza **SQLite**, com persistência dos dados em arquivo local. O banco fornecido originalmente contém **141 veículos** cadastrados.

| Categoria informada | Quantidade |
| :--- | :---: |
| **Cavalos** | 39 |
| **Carretas de 1 eixo** | 46 |
| **Carretas de 2 eixos** | 19 |
| **Bugs** | 21 |
| **LS** | 6 |
| **Outras categorias** *(conforme diferença para o total informado)* | 10 |
| **Total** | **141** |

Na base original, há referência a um cadastro vazio entre os cavalos e cinco entre as carretas de dois eixos. Recomenda-se revisar essas ocorrências antes de uma nova distribuição, caso os dados sejam usados em produção.

O arquivo principal do banco está identificado como `data/sistema_als.db`.

---

## 8. Backups e proteção dos dados

O sistema cria cópias de segurança após alterações relevantes no banco de dados. Os arquivos ficam armazenados na pasta `backup/`, com nomes que incluem a data e a hora da geração, por exemplo:

```text
database_backup_20251209_143022.db
```

Essa estratégia mantém versões anteriores do banco que podem auxiliar em recuperações. Entretanto, o backup é local: ele não substitui uma cópia externa em outro dispositivo ou ambiente. Em caso de falha do computador ou da unidade de armazenamento, o banco principal e seus backups locais podem ser afetados simultaneamente.

Como o material original não descreve uma política automática de retenção, é recomendável verificar periodicamente o espaço ocupado pela pasta e preservar cópias recentes e confiáveis antes de apagar arquivos antigos.

---

## 9. Instalação, distribuição e atualização do sistema

O processo de distribuição foi modernizado em outubro de 2026. Inicialmente, a aplicação era entregue mediante cópia de um arquivo executável ou de uma pasta completa. Agora, existe um instalador para a primeira implantação e um processo automatizado para a entrega de alterações às instalações já existentes.

### 9.1. Instalação inicial

Para disponibilizar o sistema em um novo computador:

1. Obtenha o instalador correspondente à versão disponibilizada para a ALS Transportes.
2. Execute o instalador e siga as instruções apresentadas.
3. Inicie o **Sistema de Gestão de Manutenção ALS** após a conclusão da instalação.
4. Verifique se os cadastros e as funcionalidades esperadas estão disponíveis na estação.

A instalação inicial é diferente da atualização de uma estação que já possui o sistema. O instalador precisa ser disponibilizado para o primeiro uso, enquanto as correções posteriores não exigem que o desenvolvedor reenvie manualmente um novo `.exe` ou instalador a cada máquina.

### 9.2. Entrega contínua de versões

O projeto passou a utilizar **GitHub Actions** para automatizar etapas do processo de integração e entrega (CI/CD). De acordo com o funcionamento relatado, uma alteração publicada pelo desenvolvedor pode ser processada e distribuída pelo fluxo configurado, sem a repetição do procedimento manual de copiar executáveis para os demais computadores.

O fluxo operacional é descrito em alto nível a seguir:

1. **Desenvolvimento:** uma correção ou melhoria é implementada no código-fonte.
2. **Versionamento:** a alteração é enviada ao repositório Git que concentra o projeto.
3. **Automação:** o workflow do GitHub Actions executa as etapas de preparação, empacotamento e/ou publicação definidas na configuração do projeto.
4. **Disponibilização:** a nova versão é disponibilizada pelo canal adotado na implantação.
5. **Atualização das estações:** o mecanismo de atualização utilizado no sistema permite que as instalações existentes recebam a nova versão sem envio manual de arquivos pelo desenvolvedor.

> **Importante:** o GitHub Actions executa os workflows de automação, mas não atualiza sozinho os programas instalados nos computadores. Para que o processo funcione de ponta a ponta, também é necessário um meio de disponibilizar as versões e um mecanismo que as aplique no destino. Como os arquivos do workflow e do atualizador não foram fornecidos, os nomes das ações, gatilhos, verificações de versão e procedimentos internos de instalação não são especificados aqui.

### 9.3. Componentes da distribuição

| Componente | Responsabilidade |
| :--- | :--- |
| **Instalador** | Preparar o computador para o primeiro uso da aplicação. |
| **Executável da aplicação** | Executar a interface e as funcionalidades do sistema na estação. |
| **GitHub Actions** | Automatizar as rotinas configuradas de integração, empacotamento e entrega de novas versões. |
| **Mecanismo de atualização** | Permitir que uma instalação existente receba correções sem a transferência manual de um novo executável pelo desenvolvedor. |
| **Banco de dados SQLite** | Armazenar os dados operacionais mantidos pela instalação, conforme a arquitetura local documentada. |

### 9.4. Atualização da aplicação não é sincronização de dados

Com a nova distribuição, o software pode ser atualizado em diferentes computadores. Isso não significa, por si só, que os registros de manutenção estejam compartilhados entre eles.

Na arquitetura SQLite local descrita nesta documentação, cada instalação pode ter sua própria base de dados. Caso seja necessário que vários usuários consultem e alterem os mesmos registros simultaneamente, será preciso documentar e validar uma solução específica de compartilhamento ou centralização dos dados.

Por segurança, o processo de atualização deve preservar o banco de dados e as informações operacionais existentes. Essa é uma verificação recomendada, não uma garantia técnica aferida nos arquivos do instalador e do workflow.

### 9.5. Requisitos e compatibilidade

A aplicação é destinada a Windows e não exige a instalação manual do interpretador Python quando distribuída em formato empacotado. A versão mínima do Windows deve ser validada com o instalador e as dependências efetivamente utilizados.

As funcionalidades baseadas em SQLite local podem operar sem conexão com a internet. A obtenção de novas versões, contudo, depende de acesso ao canal de atualização configurado, quando esse canal for remoto.

---

## 10. Estrutura do projeto

A organização de referência da aplicação e de seu código-fonte é a seguinte. A localização exata dos arquivos do instalador e do atualizador depende da implementação atual:

```text
Sistema Manutenção ALS/
├── .github/
│   └── workflows/              # Fluxos do GitHub Actions (CI/CD)
├── data/
│   └── sistema_als.db         # Banco de dados SQLite
├── img/                       # Imagens e identidade visual
├── backup/                    # Cópias de segurança
├── output/                    # Relatórios exportados
└── src/                       # Código-fonte da aplicação
    ├── main.py                # Tela principal e formulários
    ├── database.py            # Acesso e operações de banco de dados
    ├── veiculos.py            # Regras e operações de veículos
    ├── destinos.py            # Regras e operações de destinos
    ├── utils.py               # Utilitários, cálculos e relatórios
    ├── interface_veiculos.py  # Interface de cadastro de veículos
    └── interface_destinos.py  # Interface de cadastro de destinos
```

Arquivos auxiliares, como scripts de empacotamento, `requirements.txt` e configurações do instalador/atualizador, integram o processo de desenvolvimento e distribuição. A árvore acima representa os componentes documentados e a convenção de configuração do GitHub Actions; os caminhos específicos devem ser conferidos no repositório.

---

## 11. Especificações técnicas

| Componente | Tecnologia ou abordagem |
| :--- | :--- |
| **Linguagem da versão documentada** | Python 3.13 |
| **Interface gráfica** | Tkinter, com ttkbootstrap para temas |
| **Persistência** | SQLite 3 |
| **Manipulação de dados** | pandas |
| **Relatórios PDF** | ReportLab |
| **Relatórios Word** | python-docx |
| **Relatórios Excel** | openpyxl |
| **Manipulação de imagens** | Pillow |
| **Empacotamento** | PyInstaller (conforme a base técnica documentada) |
| **Instalação** | Instalador para implantação inicial (ferramenta não informada) |
| **CI/CD** | GitHub Actions |
| **Atualização das estações** | Processo automatizado relatado; implementação específica não fornecida |

### 11.1. Persistência e atualização de dados

O banco SQLite é a fonte principal das informações. Conforme a arquitetura descrita, a aplicação utiliza `DataFrame` como estrutura auxiliar de leitura, mas as gravações são persistidas no banco.

Após operações de inclusão, alteração ou exclusão, a aplicação executa a transação correspondente, confirma a gravação e atualiza os dados apresentados. A camada de acesso utiliza tratamento de falhas com possibilidade de *rollback*, para evitar manter transações incompletas.

### 11.2. Principais dependências

O material original indica as seguintes versões mínimas de bibliotecas:

```txt
pandas>=2.0.0
reportlab>=3.6.0
python-docx>=0.8.11
openpyxl>=3.1.0
Pillow>=10.0.0
ttkbootstrap>=1.10.0
```

A compatibilidade de cada versão deve ser conferida com o interpretador Python adotado no ambiente de desenvolvimento.

### 11.3. Executar em modo de desenvolvimento

Com o Python e as dependências corretamente instalados:

```bash
pip install -r requirements.txt
python src/main.py
```

O material anterior mencionava Python 3.8 ou superior como requisito geral, enquanto as especificações técnicas registram Python 3.13. Para reproduzir a versão documentada com mais fidelidade, utilize o ambiente de desenvolvimento efetivamente validado para o projeto.

### 11.4. Empacotamento e distribuição

A documentação anterior descrevia a geração local do executável pelo script:

```bat
GERAR_EXECUTAVEL.bat
```

Na configuração anterior, o arquivo gerado era esperado no caminho:

```text
dist\SistemaManutencaoALS.exe
```

Com a implantação de CI/CD, o fluxo automatizado do GitHub Actions passou a fazer parte da estratégia principal de distribuição. O script manual permanece aqui como referência histórica ou alternativa de desenvolvimento, caso ainda exista na estrutura atual. Antes de publicar atualizações, valide a inicialização, a preservação do banco, a gravação de registros, a emissão de relatórios e o funcionamento da atualização em uma estação de teste.

---

## 12. Exemplos de operação

### Exemplo A — Registrar uma nova manutenção
Um veículo dá entrada na oficina e ainda não possui previsão confirmada de saída. O operador cadastra a data de entrada, seleciona a placa, informa o serviço e salva sem preencher a data de saída.
- **Resultado esperado:** a manutenção permanece em serviço e sua duração passa a ser contabilizada automaticamente.

### Exemplo B — Encerrar uma manutenção
Após a conclusão do serviço, o operador localiza a manutenção, abre a edição e modifica o status para **Finalizado**. Se o campo de saída estiver vazio, o sistema registra a data atual.
- **Resultado esperado:** a manutenção passa a compor o histórico de serviços concluídos, com duração final calculada.

### Exemplo C — Emitir um relatório por período
O operador filtra os registros do intervalo desejado, por exemplo, `01/12/2025` a `31/12/2025`, e gera a exportação em Excel.
- **Resultado esperado:** é criado um arquivo na pasta `output/` com os registros do conjunto filtrado, pronto para consulta e análise.

---

## 13. Solução de problemas

| Situação | Verificação ou procedimento sugerido |
| :--- | :--- |
| **O relatório é gerado, mas não abre** | Verifique se existe um aplicativo padrão para o formato. O arquivo permanece disponível em `output/`. |
| **A contagem de dias parece desatualizada** | Utilize **Atualizar** ou feche e abra novamente o sistema. Confira as datas do registro. |
| **Não é possível excluir um veículo ou destino** | Verifique se o item está associado a registros existentes. |
| **A pasta de backups ocupa muito espaço** | Revise os arquivos antigos, mantenha cópias válidas e, preferencialmente, salve uma cópia fora do computador. |
| **O executável abre sem os dados esperados** | Confira a localização do arquivo SQLite e as permissões de leitura e gravação na pasta `data/`. |
| **Uma estação não recebeu uma nova versão** | Verifique a execução do workflow no GitHub Actions, a disponibilização da versão e o comportamento do mecanismo de atualização da estação. |
| **Dados de manutenção parecem diferentes entre dois computadores** | Confirme onde está armazenado o banco utilizado por cada instalação. Atualização automática do aplicativo não equivale à sincronização dos dados. |

---

## 14. Verificação e documentação complementar

A documentação anterior registra testes sobre 12 funcionalidades, com resultado informado de 100% de sucesso na verificação realizada à época. Esse registro se refere à versão e ao ambiente testados e não comprova o funcionamento do instalador ou do novo CI/CD. Após as mudanças de distribuição, recomenda-se validar o processo completo: instalação inicial, publicação de uma alteração, aplicação da atualização em outra estação, preservação dos dados locais e possibilidade de recuperação diante de falhas.

Arquivos complementares mencionados no projeto:

- `RELATORIO_VERIFICACAO.md` — registro de verificações e testes.
- `FUNCIONALIDADE_DIAS_CORRENDO.md` — detalhamento da regra de cálculo dos dias.
- `INSTRUCOES_DISTRIBUICAO.md` — instruções para preparar a entrega do sistema.

---

## 15. Identificação do projeto

| Informação | Descrição |
| :--- | :--- |
| **Nome** | Sistema de Gestão de Manutenção ALS |
| **Organização atendida** | ALS Transportes |
| **Versão documentada** | 2.0 |
| **Referência da versão** | Dezembro de 2025 |
| **Plataforma** | Windows (aplicação desktop) |
| **Modalidade de operação** | Dados locais; acesso ao canal de distribuição necessário para obter atualizações remotas |
| **Distribuição** | Instalador para primeiro uso e atualizações posteriores sem reenvio manual de executáveis |
| **Integração e entrega** | GitHub Actions (CI/CD) |
| **Tipo de licença informado** | Proprietária |

---

## 16. Evolução recente da distribuição

Em outubro de 2026, foram incorporadas as seguintes melhorias à entrega do sistema:

- **Instalador dedicado:** simplificação do procedimento de implantação em novos computadores.
- **Pipeline CI/CD com GitHub Actions:** automatização do processo configurado para preparar e disponibilizar alterações do aplicativo.
- **Atualização sem envio manual:** eliminação da rotina anterior de encaminhar um novo arquivo `.exe` ou instalador para cada estação sempre que uma correção fosse implementada.

Esses avanços melhoram a manutenção e a distribuição do software. Eles não alteram, isoladamente, o modelo de persistência SQLite local nem demonstram acesso simultâneo aos mesmos registros por múltiplas estações.

> **Detalhes pendentes para documentação técnica completa:** gatilhos do workflow, nomes dos arquivos de instalação, ferramenta empregada para criar o instalador, publicação dos artefatos, política de versões, funcionamento do atualizador e estratégia de reversão de uma atualização com falha.
