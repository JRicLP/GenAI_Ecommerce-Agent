"""Agente principal que orquestra a interação entre
o modelo Gemini, as ferramentas e os guardrails."""

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
    # Guardrail de escopo antes de chamar o modelo
    if not validar_escopo_pergunta(pergunta):
        return AgentResponse(
            resposta=MENSAGEM_FORA_DE_ESCOPO,
            sql_gerado="",
            tem_dados=False,
            sugestao_grafico=None
        )
    # Chama o agente — o Pydantic AI orquestra o loop modelo -> tool -> modelo
    resultado = agent.run_sync(pergunta)
    return resultado.data
