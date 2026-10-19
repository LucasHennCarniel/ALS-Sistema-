"""Regra: os destinos padrão da operação sempre existem no banco"""

DESTINOS_PADRAO = [
    'AGYLE', 'BOM SUCESSO', 'FARROUPILHA', 'FLORIÓPOLIS',
    'G&V', 'GARIBALDI', 'JOINVILLE/SC', 'NOVA TRENTO', 'SALTO VELOSO'
]


def garantir_destinos_padrao(model):
    """Garante que os destinos padrão existam no banco"""
    for destino in DESTINOS_PADRAO:
        # Tenta inserir de forma silenciosa. Se já existir, a exception ou a busca previne.
        if not model.obter_por_nome(destino):
            try:
                model.inserir(destino)
            except Exception:
                pass
