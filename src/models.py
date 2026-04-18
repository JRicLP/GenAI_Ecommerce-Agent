from pydantic import BaseModel, Field
from typing import Optional

class SQLQuery(BaseModel):
    """Query SQL gerada pelo modelo para responder à pergunta do usuário."""
    query: str = Field(description="Query SELECT válida em SQLite")
    explicacao: str = Field(description="Explicação em português do que a query faz")

class QueryResult(BaseModel):
    """Resultado bruto da execução da query no banco."""
    colunas: list[str] = Field(description="Nomes das colunas retornadas")
    linhas: list[list] = Field(description="Linhas de dados retornadas")
    total_linhas: int = Field(description="Total de linhas no resultado")

class AgentResponse(BaseModel):
    """Resposta final do agente para o usuário."""
    resposta: str = Field(description="Resposta em português natural explicando os dados")
    sql_gerado: str = Field(description="SQL que foi executado")
    tem_dados: bool = Field(description="Se a consulta retornou algum dado")
    sugestao_grafico: Optional[str] = Field(
        default=None,
        description="Tipo de gráfico sugerido: 'barra', 'linha', 'pizza' ou None"
    )
