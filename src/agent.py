"""Agente principal que orquestra a interação entre
o modelo Gemini, as ferramentas e os guardrails."""

import asyncio
from time import time
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from src.config import GEMINI_API_KEY
from src.models import AgentResponse
from src.tools import execute_sql
from src.guardrails import validar_escopo_pergunta, MENSAGEM_FORA_DE_ESCOPO
from src.schema_prompt import SYSTEM_PROMPT

# Inicializa o modelo Gemini 2.5 Flash
model = GoogleModel(
    "gemini-2.5-flash",
    provider=GoogleProvider(api_key=GEMINI_API_KEY),
)

# Cria o agente com tipo de resposta estruturada
agent = Agent(
    model=model,
    output_type=AgentResponse,
    system_prompt=SYSTEM_PROMPT,
    tools=[execute_sql]
)

def consultar(pergunta: str) -> AgentResponse:
    """
    Ponto de entrada principal do agente.
    Recebe uma pergunta em português e retorna uma resposta estruturada.

    Args:
        pergunta: Pergunta do usuário sobre os dados de e-commerce.

    Returns:
        AgentResponse com a resposta, SQL gerado e metadados.
    """
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
    
    """ Lógica de retry com até 3 tentativas e um delay de 10 segundos entre elas para
     lidar com possíveis erros de disponibilidade do modelo. """

    for tentativa in range(1, 4):
        try:
            return asyncio.get_event_loop().run_until_complete(_run())
        except Exception as e:
            if "503" in str(e) and tentativa < 3:
                print(f"Modelo indisponível. Tentativa {tentativa}/3 — aguardando 10s...")
                time.sleep(10)
            else:
                raise

    return asyncio.get_event_loop().run_until_complete(_run())
