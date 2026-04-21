"""Guardrails para validação de queries SQL e escopo de perguntas."""

import re

# Palavras que jamais podem aparecer em uma query
COMANDOS_PROIBIDOS = [
    "insert", "update", "delete", "drop", "alter",
    "create", "truncate", "replace", "merge", "grant"
]

# Termos que indicam que a pergunta está fora do escopo
FORA_DE_ESCOPO = [
    "previsão do tempo", "esportes", "política", "receita culinária",
    "filme", "música", "notícia", "futebol", "financeiro pessoal"
]

# Padrões comuns de prompt injections para contornar as regras
PADROES_INJECTION = [
    r"ignore\s+(as\s+)?instru[çc][oõ]es",
    r"esquece?\s+(as\s+)?instru[çc][oõ]es",
    r"novo\s+papel",
    r"nova\s+personalidade",
    r"act\s+as",
    r"ignore\s+previous",
    r"forget\s+(your\s+)?instructions",
    r"you\s+are\s+now",
    r"fingir?\s+que\s+(voc[eê]\s+[eé]|[eé]s?)",
    r"ignore\s+all",
    r"jailbreak",
    r"dan\s+mode",
]

TAMANHO_MAXIMO_PERGUNTA = 500  # Limite de caracteres para a query SQL

MENSAGEM_INJECTION = (
    "Sua pergunta contém termos que parecem ser uma tentativa de manipular o sistema." 
    "Por questões de segurança, não posso processar esse tipo de pergunta. "
)

MENSAGEM_FORA_DE_ESCOPO = (
    "Posso ajudar apenas com análises do sistema de e-commerce, "
    "como vendas, pedidos, produtos, consumidores e avaliações. "
    "Como posso ajudar com algum desses temas?"
)

MENSAGEM_MUITO_LONGA = (
    f"A query é muito longa. O limite é de {TAMANHO_MAXIMO_PERGUNTA} caracteres."
)

def validar_tamanho_pergunta(pergunta: str, limite: int = TAMANHO_MAXIMO_PERGUNTA) -> bool:
    """ Valida se a pergunta do usuário não excede um limite de caracteres."""
    return len((pergunta or "").strip()) <= limite

def detectar_prompt_injection(pergunta: str) -> bool:
    """
    Detecta tentativas de prompt injection na pergunta.
    Retorna True se detectar um padrão suspeito.

    Args:
        pergunta (str): A pergunta do usuário a ser analisada.

    Returns:
        bool: True se detectar prompt injection, False caso contrário.
    """
    pergunta_lower = pergunta.lower()
    for padrao in PADROES_INJECTION:
        if re.search(padrao, pergunta_lower):
            return True
    return False

def validar_tamanho_query(query: str) -> None:
    """
    Valida que a query não excede o tamanho máximo permitido.
    Lança ValueError se a query for muito longa.

    Args:
        query (str): A query SQL a ser validada.
    """
    if len(query) > TAMANHO_MAXIMO_PERGUNTA:
        raise ValueError(MENSAGEM_MUITO_LONGA)

def validar_query_sql(query: str) -> None:
    """
    Valida que a query é segura para execução.
    Lança ValueError se detectar comandos proibidos.
    """
    query_lower = query.lower().strip()    
    # Deve começar com SELECT e aceitar CTEs com WITH, mas não pode conter comandos de modificação
    if not query_lower.startswith("select") and not query_lower.startswith("with"):
        raise ValueError(
            f"Apenas queries SELECT são permitidas. "
            f"Query recebida começa com: '{query_lower[:20]}...'"
        )
    # Não pode conter comandos de modificação em nenhuma parte da query
    for comando in COMANDOS_PROIBIDOS:
        # Usa regex para evitar falsos positivos (ex: 'selected' não é 'select')
        if re.search(rf'\b{comando}\b', query_lower):
            raise ValueError(
                f"Comando '{comando.upper()}' não é permitido. "
                f"O agente opera em modo somente leitura."
            )

def validar_escopo_pergunta(pergunta: str) -> bool:
    """
    Verifica se a pergunta está dentro do escopo do e-commerce.
    Retorna False se a pergunta for claramente fora do contexto.
    """
    pergunta_lower = pergunta.lower()
    for termo in FORA_DE_ESCOPO:
        if termo in pergunta_lower:
            return False
    return True
