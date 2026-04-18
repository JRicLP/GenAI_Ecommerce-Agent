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

def validar_query_sql(query: str) -> None:
    """
    Valida que a query é segura para execução.
    Lança ValueError se detectar comandos proibidos.
    """
    query_lower = query.lower().strip()    
    # Deve começar com SELECT
    if not query_lower.startswith("select"):
        raise ValueError(
            f"Apenas queries SELECT são permitidas. "
            f"Query recebida começa com: '{query_lower[:20]}...'"
        )
    # Não pode conter comandos de modificação
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

MENSAGEM_FORA_DE_ESCOPO = (
    "Posso ajudar apenas com análises do sistema de e-commerce, "
    "como vendas, pedidos, produtos, consumidores e avaliações. "
    "Como posso ajudar com algum desses temas?"
)
