"""Ferramentas para interação com o banco de dados SQLite."""

import os
import sqlite3
from src.models import QueryResult
from src.guardrails import validar_query_sql

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "banco.db")

def get_connection():
    """Retorna uma conexão com o banco SQLite."""
    return sqlite3.connect(DB_PATH)

def execute_sql(query: str) -> QueryResult:
    """
    Executa uma query SELECT no banco de dados e retorna o resultado.
    
    Args:
        query: Query SQL do tipo SELECT a ser executada.
        
    Returns:
        QueryResult com colunas, linhas e total de resultados.
        
    Raises:
        ValueError: Se a query não for do tipo SELECT.
        RuntimeError: Se houver erro de execução no banco.
    """
    validar_query_sql(query) 

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        
        colunas = [desc[0] for desc in cursor.description]
        linhas = [list(row) for row in cursor.fetchall()]
        
        return QueryResult(
            colunas=colunas,
            linhas=linhas,
            total_linhas=len(linhas)
        )
    except sqlite3.Error as e:
        raise RuntimeError(f"Erro ao executar SQL: {str(e)}\nQuery: {query}") from e
    finally:
        conn.close()
