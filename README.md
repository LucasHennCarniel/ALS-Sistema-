Sistema de Gestão de Manutenção — ALS Transportes
Documentação funcional e técnica | Versão 2.0 — dezembro de 2025

O Sistema de Gestão de Manutenção ALS é uma aplicação desktop desenvolvida para organizar e acompanhar as manutenções da frota da ALS Transportes. A solução centraliza os registros de entrada e saída dos veículos, os serviços realizados, os períodos de permanência em manutenção e os dados necessários para consultas e relatórios.

A versão descrita neste documento opera localmente no Windows, utiliza banco de dados SQLite e pode ser distribuída como executável, sem exigir a instalação do Python no computador do usuário final.
Escopo desta documentação: as funcionalidades e especificações abaixo correspondem à versão 2.0 descrita no material original. Acesso simultâneo por vários computadores, sincronização em rede e acesso remoto não fazem parte do escopo documentado desta versão.

1. Visão geral
O objetivo do sistema é substituir controles manuais ou dispersos por um processo padronizado de registro e consulta das manutenções da frota. Entre seus principais recursos estão:
- Cadastro e manutenção dos registros de serviço, com inclusão, edição e exclusão.
- Controle do status de cada manutenção: Em serviço ou Finalizado.
- Cálculo automático do tempo de permanência do veículo em manutenção.
- Cadastro de veículos e destinos utilizados nos registros.
- Filtros para localização de informações por placa, veículo, status e datas.
- Indicadores operacionais para acompanhamento da frota.
- Exportação de relatórios em Excel, PDF, Word e texto.
- Geração automática de cópias de segurança após alterações relevantes.
1.1. Organização da interface
A tela principal reúne filtros de consulta, uma tabela com os registros e indicadores resumidos. A organização foi pensada para priorizar as manutenções em andamento e facilitar o acesso às ações mais frequentes.

Na identificação visual dos registros, são utilizadas as seguintes cores:
Elemento	Identificação
Manutenções em andamento	Fundo amarelo-claro
Manutenções finalizadas	Fundo verde-claro
Ações principais	Botões azuis
Exclusões	Botões vermelhos, com confirmação


A aplicação também possui abas para Registros e Notas. O funcionamento detalhado da aba de notas não está especificado no material desta versão.
2. Gestão dos registros de manutenção
Cada registro representa a passagem de um veículo pelo processo de manutenção. Os dados informados permitem identificar o equipamento, o serviço e o intervalo de tempo em que ele permaneceu em atendimento.
2.1. Cadastrar uma manutenção
1. Na tela principal, selecione Novo Registro.
2. Informe a data de entrada, que é obrigatória.
3. Selecione a placa e preencha os dados disponíveis do veículo, incluindo quilometragem, destino e descrição do serviço.
4. Se o veículo ainda estiver em manutenção, mantenha a data de saída em branco.
5. Salve o registro.
O sistema calcula o status e os dias de manutenção com base nas informações cadastradas. A placa informada deve corresponder a um veículo existente no cadastro.
2.2. Editar uma manutenção
1. Localize o registro na tabela, utilizando os filtros quando necessário.
2. Selecione o item e clique em Editar.
3. Atualize os dados desejados.
4. Salve para registrar as alterações.
Esse procedimento pode ser utilizado tanto para corrigir informações quanto para finalizar uma manutenção.
2.3. Excluir registros
A aplicação permite excluir um registro individualmente ou selecionar vários para exclusão em lote. Para selecionar diversos itens, utilize Ctrl + clique ou Shift + clique na tabela.

Antes de concluir a operação, o sistema solicita confirmação. Exclusões devem ser tratadas como definitivas, sendo importante verificar se os registros selecionados estão corretos.
3. Regras de negócio e comportamentos automáticos
3.1. Cálculo dos dias em manutenção
O campo de dias representa o tempo de permanência do veículo no processo de manutenção:
- Sem data de saída: o cálculo considera o intervalo entre a data de entrada e a data atual.
- Com data de saída: o cálculo considera o intervalo entre a entrada e a saída, sem continuar aumentando nos dias seguintes.
- Entrada e saída no mesmo dia: a contagem mínima aplicada pelo sistema é de um dia.
A regra documentada considera o dia inicial na contagem. Por exemplo, um veículo que entrou em 18/11/2025 e continuava em serviço em 09/12/2025 apresenta 22 dias. Se permanecesse em serviço em 10/12/2025, apresentaria 23 dias.

O valor é atualizado durante o uso ou na reabertura/atualização do sistema e é recalculado antes da geração dos relatórios.
3.2. Finalização da manutenção
Ao alterar o status de um registro para Finalizado, se a data de saída estiver vazia, o sistema a preenche automaticamente com a data atual. A partir desse momento, o total de dias é calculado sobre o período encerrado.

O material original também informa que o status pode ser alterado manualmente. Por isso, a data de saída e o status devem ser conferidos durante a edição para manter a consistência do histórico.
3.3. Ordenação dos registros
Na tabela principal, os registros são organizados da seguinte maneira:
1. Manutenções com status Em serviço aparecem primeiro.
2. Manutenções com status Finalizado aparecem em seguida.
3. Dentro de cada grupo, os itens são exibidos do mais recente para o mais antigo.
Essa ordem é preservada ao aplicar filtros, facilitando a identificação das atividades ainda pendentes.
3.4. Validações importantes
Regra	Comportamento esperado
Data de entrada	Campo obrigatório no cadastro da manutenção
Placa	Deve estar cadastrada na relação de veículos
Formato de placa	Validado conforme os formatos brasileiros aceitos pelo sistema
Datas	Informadas no formato DD/MM/AAAA
Status Finalizado	Requer data de saída; caso esteja vazia, é preenchida automaticamente
Exclusão	Exige confirmação do usuário


4. Consultas, filtros e indicadores
4.1. Pesquisa de manutenções
Os registros podem ser consultados por placa, veículo, status, data de entrada e data de saída. Os filtros podem ser combinados para restringir os resultados.

Para pesquisar, informe os critérios desejados e selecione Buscar. Para retornar à listagem sem filtros, utilize Limpar.
4.2. Indicadores operacionais
A faixa de indicadores da tela principal apresenta:
Indicador	Informação apresentada
Total de registros	Quantidade de registros considerados na visualização
Em serviço	Manutenções que permanecem abertas
Finalizados	Manutenções registradas como concluídas
Tempo médio	Média de duração das manutenções, exibida em dias inteiros
Placas únicas	Quantidade de placas distintas consideradas


Os indicadores são atualizados após a inclusão, edição ou exclusão de registros e também após a aplicação de filtros.
5. Cadastros auxiliares
5.1. Veículos
O cadastro de veículos organiza a identificação dos equipamentos utilizados nos lançamentos de manutenção.

Para incluir um veículo:
1. Acesse Veículos e selecione Novo Veículo.
2. Preencha placa, tipo, descrição e quilometragem.
3. Confirme os dados e salve.
Veículos existentes podem ser editados ou excluídos pelos comandos da mesma tela. O sistema valida o formato da placa e pode impedir a exclusão de veículos associados a registros de manutenção.
5.2. Destinos
O cadastro de destinos permite reutilizar informações recorrentes, reduzindo digitação e padronizando a nomenclatura nos lançamentos.

São disponibilizadas operações para adicionar, editar e excluir destinos. Quando um destino estiver associado a registros existentes, sua exclusão poderá ser bloqueada para preservar a integridade dos dados.
6. Emissão de relatórios
O sistema exporta dados de manutenção em diferentes formatos, para atender às necessidades de acompanhamento operacional, análise e compartilhamento.
Formato	Extensão	Aplicação principal
Excel	.xlsx	Análise de dados em planilhas, com colunas e estatísticas
PDF	.pdf	Consulta e compartilhamento de relatório com apresentação padronizada
Word	.docx	Edição posterior de um documento com tabela e indicadores
Texto	.txt	Consulta ou compartilhamento em formato simples e leve


6.1. Gerar um relatório
1. Se necessário, aplique os filtros para selecionar o conjunto de registros desejado.
2. Clique em Relatório na tela principal.
3. Escolha o formato de exportação.
4. Aguarde a geração e consulte o documento.
Os arquivos são armazenados na pasta output/, com data e hora no nome. Exemplo: Relatorio_20251209_143022.pdf.

O sistema tenta abrir o relatório automaticamente após sua geração, desde que exista no computador um aplicativo associado ao formato selecionado. Os dias de manutenção são recalculados antes da exportação, e a média é exibida como número inteiro.
7. Banco de dados e informações iniciais
A versão documentada utiliza SQLite, com persistência dos dados em arquivo local. O banco fornecido originalmente contém 141 veículos cadastrados.
Categoria informada	Quantidade
Cavalos	39
Carretas de 1 eixo	46
Carretas de 2 eixos	19
Bugs	21
LS	6
Outras categorias, conforme diferença para o total informado	10
Total	141


Na base original, há referência a um cadastro vazio entre os cavalos e cinco entre as carretas de dois eixos. Recomenda-se revisar essas ocorrências antes de uma nova distribuição, caso os dados sejam usados em produção.

O arquivo principal do banco está identificado como data/sistema_als.db.
8. Backups e proteção dos dados
O sistema cria cópias de segurança após alterações relevantes no banco de dados. Os arquivos ficam armazenados na pasta backup/, com nomes que incluem a data e a hora da geração, por exemplo:
database_backup_20251209_143022.db
Essa estratégia mantém versões anteriores do banco que podem auxiliar em recuperações. Entretanto, o backup é local: ele não substitui uma cópia externa em outro dispositivo ou ambiente. Em caso de falha do computador ou da unidade de armazenamento, o banco principal e seus backups locais podem ser afetados simultaneamente.

Como o material original não descreve uma política automática de retenção, é recomendável verificar periodicamente o espaço ocupado pela pasta e preservar cópias recentes e confiáveis antes de apagar arquivos antigos.
9. Instalação e execução
9.1. Uso do executável
Na distribuição do sistema, execute SistemaManutencaoALS.exe. O executável foi pensado para funcionar sem uma instalação separada do Python.

Na versão que acompanha a base previamente cadastrada, o arquivo de dados precisa estar disponível conforme a estrutura esperada pela aplicação. Copiar somente o executável não garante, por si só, que os 141 veículos estejam presentes, a menos que o empacotamento tenha incluído ou provisionado o banco inicial.
9.2. Distribuição da pasta completa
Para preservar a estrutura e os dados da versão disponibilizada:
1. Copie a pasta de distribuição do sistema.
2. Verifique se o banco em data/ acompanha a cópia.
3. Confirme as permissões de leitura e gravação nas pastas de dados, backups e relatórios.
4. Execute SistemaManutencaoALS.exe.
5. Valide a listagem dos veículos e a gravação de um registro de teste no ambiente de destino.
9.3. Compatibilidade
O sistema é destinado a computadores com Windows. O material anterior mencionava Windows 7 ou superior, mas a compatibilidade real depende da versão do Python utilizada no empacotamento e das dependências do executável. Portanto, a versão do Windows de destino deve ser testada antes da distribuição.

O uso documentado é local e offline. Este documento não prevê acesso multiusuário, autenticação de usuários nem sincronização de dados entre instalações.
10. Estrutura do projeto
A organização informada para a aplicação é a seguinte:
Sistema Manutenção ALS/
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
Arquivos auxiliares, como scripts de empacotamento e requirements.txt, são utilizados no ambiente de desenvolvimento.
11. Especificações técnicas
Componente	Tecnologia ou abordagem
Linguagem da versão documentada	Python 3.13
Interface gráfica	Tkinter, com ttkbootstrap para temas
Persistência	SQLite 3
Manipulação de dados	pandas
Relatórios PDF	ReportLab
Relatórios Word	python-docx
Relatórios Excel	openpyxl
Manipulação de imagens	Pillow
Empacotamento	PyInstaller


11.1. Persistência e atualização de dados
O banco SQLite é a fonte principal das informações. Conforme a arquitetura descrita, a aplicação utiliza DataFrame como estrutura auxiliar de leitura, mas as gravações são persistidas no banco.

Após operações de inclusão, alteração ou exclusão, a aplicação executa a transação correspondente, confirma a gravação e atualiza os dados apresentados. A camada de acesso utiliza tratamento de falhas com possibilidade de rollback, para evitar manter transações incompletas.
11.2. Principais dependências
O material original indica as seguintes versões mínimas de bibliotecas:
pandas>=2.0.0
reportlab>=3.6.0
python-docx>=0.8.11
openpyxl>=3.1.0
Pillow>=10.0.0
ttkbootstrap>=1.10.0
A compatibilidade de cada versão deve ser conferida com o interpretador Python adotado no ambiente de desenvolvimento.
11.3. Executar em modo de desenvolvimento
Com o Python e as dependências corretamente instalados:
pip install -r requirements.txt
python src/main.py
O material anterior mencionava Python 3.8 ou superior como requisito geral, enquanto as especificações técnicas registram Python 3.13. Para reproduzir a versão documentada com mais fidelidade, utilize o ambiente de desenvolvimento efetivamente validado para o projeto.
11.4. Gerar o executável
Execute o script de empacotamento:
GERAR_EXECUTAVEL.bat
Ao final do processo, o arquivo gerado é esperado no caminho:
dist\SistemaManutencaoALS.exe
Antes de entregar o executável, valide a inicialização, o acesso ao banco, a gravação dos registros e a emissão dos relatórios em um computador de destino.
12. Exemplos de operação
Exemplo A — Registrar uma nova manutenção
Um veículo dá entrada na oficina e ainda não possui previsão confirmada de saída. O operador cadastra a data de entrada, seleciona a placa, informa o serviço e salva sem preencher a data de saída.

Resultado esperado: a manutenção permanece em serviço e sua duração passa a ser contabilizada automaticamente.
Exemplo B — Encerrar uma manutenção
Após a conclusão do serviço, o operador localiza a manutenção, abre a edição e modifica o status para Finalizado. Se o campo de saída estiver vazio, o sistema registra a data atual.

Resultado esperado: a manutenção passa a compor o histórico de serviços concluídos, com duração final calculada.
Exemplo C — Emitir um relatório por período
O operador filtra os registros do intervalo desejado, por exemplo, 01/12/2025 a 31/12/2025, e gera a exportação em Excel.

Resultado esperado: é criado um arquivo na pasta output/ com os registros do conjunto filtrado, pronto para consulta e análise.
13. Solução de problemas
Situação	Verificação ou procedimento sugerido
O relatório é gerado, mas não abre	Verifique se existe um aplicativo padrão para o formato. O arquivo permanece disponível em output/.
A contagem de dias parece desatualizada	Utilize Atualizar ou feche e abra novamente o sistema. Confira as datas do registro.
Não é possível excluir um veículo ou destino	Verifique se o item está associado a registros existentes.
A pasta de backups ocupa muito espaço	Revise os arquivos antigos, mantenha cópias válidas e, preferencialmente, salve uma cópia fora do computador.
O executável abre sem os dados esperados	Confira se o arquivo SQLite foi distribuído no local correto e se a aplicação possui acesso à pasta data/.


14. Verificação e documentação complementar
A documentação anterior registra testes sobre 12 funcionalidades, com resultado informado de 100% de sucesso na verificação realizada à época. Esse registro se refere à versão e ao ambiente testados e não dispensa uma nova validação após mudanças no código, nas dependências ou na forma de distribuição.

Arquivos complementares mencionados no projeto:
- RELATORIO_VERIFICACAO.md — registro de verificações e testes.
- FUNCIONALIDADE_DIAS_CORRENDO.md — detalhamento da regra de cálculo dos dias.
- INSTRUCOES_DISTRIBUICAO.md — instruções para preparar a entrega do sistema.
15. Identificação do projeto
Informação	Descrição
Nome	Sistema de Gestão de Manutenção ALS
Organização atendida	ALS Transportes
Versão documentada	2.0
Referência da versão	Dezembro de 2025
Plataforma	Windows (aplicação desktop)
Modalidade de operação	Local, sem necessidade de conexão com a internet
Tipo de licença informado	Proprietária
