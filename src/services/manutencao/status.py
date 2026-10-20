"""Status válidos de um registro de manutenção (fonte única para formulário, filtros, cards e dashboard)"""

STATUS_AGENDADO = 'AGENDADO'
STATUS_EM_MANUTENCAO = 'EM MANUTENÇÃO'
STATUS_FINALIZADO = 'FINALIZADO'
STATUS_SINISTRO = 'SINISTRO'

# Ordem do fluxo operacional (usada em listas, filtros e no dashboard)
STATUS_VALIDOS = [STATUS_AGENDADO, STATUS_EM_MANUTENCAO, STATUS_FINALIZADO, STATUS_SINISTRO]

# Status que não deixam o veículo parado: ainda vai entrar (agendado) ou já saiu (finalizado)
STATUS_SEM_PARADA = [STATUS_AGENDADO, STATUS_FINALIZADO]

# Status antigos que deixaram de existir -> equivalente atual (aplicado na leitura, sem alterar o banco)
STATUS_LEGADOS = {
    'EM SERVIÇO': STATUS_EM_MANUTENCAO,
    'AGUARDANDO PEÇAS': STATUS_EM_MANUTENCAO,
    'EM TRÂNSITO': STATUS_EM_MANUTENCAO,
    'PREVENTIVA': STATUS_EM_MANUTENCAO,
    'CORRETIVA': STATUS_EM_MANUTENCAO,
    'SOCORRO': STATUS_EM_MANUTENCAO,
    'AGUARDANDO': STATUS_AGENDADO,
}
