"""Anonimização de dados pessoais nos resultados do agente."""

# Colunas que contêm dados pessoais e devem ser mascaradas
COLUNAS_SENSIVEIS = {
    "nome_consumidor",
    "nome_vendedor",
    "nome_cliente",
    "email",
    "telefone",
}

def mascarar_nome(nome: str) -> str:
    """
    Mascara um nome completo preservando apenas a inicial do primeiro
    nome e a inicial do sobrenome.

    Exemplos:
        'João Silva'     -> 'J. S***'
        'Dr. Maria Lima' -> 'Dr. M. L***'
        'Ana'            -> 'A***'

    Args:
        nome: O nome completo a ser mascarado.
    Returns:
        O nome mascarado.
    """
    if not nome or not isinstance(nome, str):
        return nome

    # Preservação dos prefixos de tratamento (Dr., Dra., Sr., Sra.)
    prefixo = ""
    partes = nome.strip().split()
    prefixos_conhecidos = {"dr.", "dra.", "sr.", "sra.", "prof.", "eng."}

    if partes and partes[0].lower() in prefixos_conhecidos:
        prefixo = partes[0] + " "
        partes = partes[1:]

    if not partes:
        return nome

    if len(partes) == 1:
        return f"{prefixo}{partes[0][0]}***"

    inicial_primeiro = partes[0][0].upper()
    inicial_ultimo = partes[-1][0].upper()
    return f"{prefixo}{inicial_primeiro}. {inicial_ultimo}***"


def anonimizar_resultado(colunas: list[str], linhas: list[list]) -> list[list]:
    """
    Aplica mascaramento nas colunas sensíveis de um resultado SQL.

    Args:
        colunas: Nomes das colunas retornadas pela query.
        linhas:  Linhas de dados brutas do banco.

    Returns:
        Linhas com dados pessoais mascarados.
    """
    # Identificação de quais índices de coluna precisam ser mascarados
    indices_sensiveis = [
        i for i, col in enumerate(colunas)
        if col.lower() in COLUNAS_SENSIVEIS
    ]

    if not indices_sensiveis:
        return linhas  # Caso não haja colunas sensíveis, retorna os dados originais

    linhas_anonimizadas = []
    for linha in linhas:
        linha_nova = list(linha)
        for idx in indices_sensiveis:
            if idx < len(linha_nova):
                linha_nova[idx] = mascarar_nome(str(linha_nova[idx]))
        linhas_anonimizadas.append(linha_nova)

    return linhas_anonimizadas
