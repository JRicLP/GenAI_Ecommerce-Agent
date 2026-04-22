"""Agente principal que orquestra a interação entre
o modelo Gemini, as ferramentas e os guardrails."""

import asyncio
from time import sleep
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from src.config import GEMINI_API_KEY
from src.models import AgentResponse
from src.tools import execute_sql
from src.schema_prompt import SYSTEM_PROMPT
from src.guardrails import (
    validar_escopo_pergunta,
    detectar_prompt_injection,
    validar_tamanho_pergunta,
    MENSAGEM_FORA_DE_ESCOPO,
    MENSAGEM_INJECTION,
    MENSAGEM_MUITO_LONGA,
)

# Inicialização do modelo Gemini 2.5 Flash
model = GoogleModel(
    "gemini-2.5-flash",
    provider=GoogleProvider(api_key=GEMINI_API_KEY),
)

# Criação do agente com tipo de resposta estruturada e ferramentas
agent = Agent(
    model=model,
    output_type=AgentResponse,
    system_prompt=SYSTEM_PROMPT,
    tools=[execute_sql]
)

def consultar(pergunta: str) -> AgentResponse:
    """
    Ponto de entrada principal do agente com retry automático.

    Trata dois tipos de falha:
    - Erros de disponibilidade da API (503) e cota (429): aguarda e tenta novamente.
    - Erros de SQL inválido: devolve o erro ao modelo e pede reescrita.

    Args:
        pergunta: Pergunta do usuário sobre os dados de e-commerce.

    Returns:
        AgentResponse: A resposta do agente, incluindo a resposta textual,
        a query SQL gerada, se há dados para mostrar e sugestão de gráfico.
    """

    # Guardrail 1: Tamanho da pergunta
    if not validar_tamanho_pergunta(pergunta):
        return AgentResponse(
            resposta=MENSAGEM_MUITO_LONGA,
            sql_gerado="",
            tem_dados=False,
            sugestao_grafico=None
        )

        # Guardrail 2: Prompt injection
    if detectar_prompt_injection(pergunta):
        return AgentResponse(
            resposta=MENSAGEM_INJECTION,
            sql_gerado="",
            tem_dados=False,
            sugestao_grafico=None
        )
    
        # Guardrail 3: Escopo da pergunta
    if not validar_escopo_pergunta(pergunta):
        return AgentResponse(
            resposta=MENSAGEM_FORA_DE_ESCOPO,
            sql_gerado="",
            tem_dados=False,
            sugestao_grafico=None
        )

    async def _run():
        resultado = await agent.run(pergunta)
        return resultado.output

    # Nível 1: Retry para erros de API (503/429)

    MAX_TENTATIVAS_API = 3
    ESPERA_SEGUNDOS = 15

    for tentativa in range(1, MAX_TENTATIVAS_API + 1):
        try:
            return asyncio.get_event_loop().run_until_complete(_run())

        except Exception as e:
            erro_str = str(e)
            e_api = "503" in erro_str or "429" in erro_str

            if e_api and tentativa < MAX_TENTATIVAS_API:
                codigo = "503" if "503" in erro_str else "429"
                print(
                    f"Erro {codigo} da API. "
                    f"Tentativa {tentativa}/{MAX_TENTATIVAS_API} — "
                    f"aguardando {ESPERA_SEGUNDOS}s..."
                )
                sleep(ESPERA_SEGUNDOS)
                continue

            # Nível 2: Retry para SQL inválido
            if "Erro ao executar SQL" in erro_str or "RuntimeError" in erro_str:
                return _retry_sql(pergunta, erro_str)

            # Qualquer outro erro: relança para o caller tratar
            raise

    # Esgotamento das tentativas de API
    raise RuntimeError(
        "O modelo está indisponível no momento. "
        "Tente novamente em alguns minutos."
    )


def _retry_sql(pergunta: str, erro_original: str) -> AgentResponse:
    """
    Tenta corrigir um SQL inválido devolvendo o erro ao modelo
    e pedindo uma nova query. Até 2 tentativas adicionais.

    Args:
        pergunta: A pergunta original do usuário.
        erro_original: O erro retornado ao tentar executar a query SQL.
    Returns:
        AgentResponse: A resposta do agente após tentar corrigir a query SQL.
    """
    MAX_TENTATIVAS_SQL = 2

    pergunta_corrigida = (
        f"{pergunta}\n\n"
        f"[SISTEMA] A query SQL gerada anteriormente retornou o seguinte erro:\n"
        f"{erro_original}\n"
        f"Por favor, corrija a query e tente novamente."
    )

    async def _run_corrigido():
        resultado = await agent.run(pergunta_corrigida)
        return resultado.output

    for tentativa in range(1, MAX_TENTATIVAS_SQL + 1):
        try:
            print(f"Corrigindo SQL — tentativa {tentativa}/{MAX_TENTATIVAS_SQL}...")
            return asyncio.get_event_loop().run_until_complete(_run_corrigido())
        except Exception as e:
            if tentativa == MAX_TENTATIVAS_SQL:
                return AgentResponse(
                    resposta=(
                        "Não foi possível gerar uma query válida para esta pergunta. "
                        f"Erro: {str(e)}"
                    ),
                    sql_gerado="",
                    tem_dados=False,
                    sugestao_grafico=None
                )

    return AgentResponse(
    resposta="Não foi possível concluir a correção da query SQL.",
    sql_gerado="",
    tem_dados=False,
    sugestao_grafico=None
    )
