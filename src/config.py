"""Configurações para o GenAI Agent, incluindo a chave de API do Gemini."""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("A chave de API do Gemini não foi encontrada." \
    "Por favor, defina a variável de ambiente GEMINI_API_KEY.")
