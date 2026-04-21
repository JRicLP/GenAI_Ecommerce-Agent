# GenAI E-Commerce Agent

Agente conversacional **Text-to-SQL** para análise de dados de um sistema de gerenciamento de e-commerce brasileiro. O agente permite que usuários não técnicos realizem consultas em linguagem natural diretamente sobre o banco de dados, obtendo respostas explicadas em português e visualizações automáticas dos resultados.

Desenvolvido como atividade prática do programa **Rocket Lab 2026 — Visagio**.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JRicLP/GenAI_Ecommerce-Agent/blob/main/notebook.ipynb)

---

## Índice

- [Visão Geral](#visão-geral)
- [Stack Utilizada](#stack-utilizada)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Banco de Dados](#banco-de-dados)
- [Pré-requisitos](#pré-requisitos)
- [Como Executar](#como-executar)
- [Funcionalidades](#funcionalidades)
- [Exemplos de Perguntas](#exemplos-de-perguntas)
- [Guardrails e Segurança](#guardrails-e-segurança)

---

## Visão Geral

O agente recebe uma pergunta em português, gera automaticamente a query SQL correspondente, executa no banco de dados SQLite e retorna a resposta em linguagem natural — com gráfico automático quando relevante e anonimização de dados pessoais antes da exibição.

```
Usuário → Pergunta em português
       → Agente (Pydantic AI + Gemini 2.5 Flash)
       → Query SQL gerada e validada
       → Execução no banco SQLite
       → Resposta em português + gráfico automático
```

---

## Stack Utilizada

| Componente | Tecnologia |
|-----------|-----------|
| Framework de Agentes | [Pydantic AI](https://ai.pydantic.dev/) |
| Modelo de Linguagem | Gemini 2.5 Flash (Google AI Studio) |
| Linguagem | Python 3.13 |
| Banco de Dados | SQLite3 (embutido no Python) |
| Ambiente de Execução | Google Colab |
| Visualizações | Matplotlib |

---

## Estrutura do Projeto

```
GenAI_Ecommerce-Agent/
├── notebook.ipynb          # Notebook principal (Colab) — entregável
├── requirements.txt        # Dependências do projeto
├── .gitignore
├── README.md
└── src/
    ├── agent.py            # Agente Pydantic AI com retry automático
    ├── config.py           # Carregamento seguro da API Key
    ├── models.py           # Modelos Pydantic (SQLQuery, QueryResult, AgentResponse)
    ├── tools.py            # Tool execute_sql — interface com o banco
    ├── guardrails.py       # Validações de segurança e escopo
    ├── graficos.py         # Geração automática de gráficos
    ├── anonimizacao.py     # Mascaramento de dados pessoais
    └── schema_prompt.py    # System prompt com schema completo do banco
```

---

## Banco de Dados

O banco `banco.db` é um arquivo SQLite3 com 7 tabelas cobrindo o período de **setembro de 2016 a outubro de 2018**:

| Tabela | Tipo | Linhas | Descrição |
|--------|------|--------|-----------|
| `dim_consumidores` | Dimensão | 99.441 | Estado, cidade e CEP do comprador |
| `dim_produtos` | Dimensão | 32.951 | Nome, categoria e dimensões físicas |
| `dim_vendedores` | Dimensão | 3.095 | Nome e localização do vendedor |
| `fat_pedidos` | Fato | 99.441 | Status, timestamps e métricas de entrega |
| `fat_pedido_total` | Fato | 99.441 | Valor pago (BRL e USD) por pedido |
| `fat_itens_pedidos` | Fato | 112.650 | Itens, preços e frete por pedido |
| `fat_avaliacoes_pedidos` | Fato | 95.307 | Nota (1–5), título e comentário |

**O arquivo `banco.db` não está incluído no repositório.** Ele deve ser obtido junto à atividade e salvo no Google Drive conforme instruções abaixo.

---

## Pré-requisitos

- Conta Google (para uso do Google Colab e Google Drive)
- API Key do Google AI Studio — obtenha gratuitamente em [aistudio.google.com](https://aistudio.google.com)
- Arquivo `banco.db` (fornecido pela atividade)

---

## Como Executar

### 1. Salvar o banco de dados no Google Drive

Faça upload do arquivo `banco.db` para o seu Google Drive no seguinte caminho:

```
Meu Drive/
└── GenAI Database/
    └── banco.db
```

> Se preferir um caminho diferente, atualize a variável `BANCO_ORIGEM` na Célula 6 do notebook.

### 2. Configurar a API Key no Colab

No Google Colab, clique no ícone de cadeado na barra lateral esquerda (**Secrets**) e adicione:

```
Nome:  GEMINI_API_KEY
Valor: sua-chave-aqui
```

> Nunca insira a chave diretamente no código — use sempre o painel de Secrets.

### 3. Abrir o notebook no Colab

Clique no badge abaixo ou acesse o link diretamente:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JRicLP/GenAI_Ecommerce-Agent/blob/main/notebook.ipynb)

### 4. Executar todas as células

No menu do Colab: **Runtime → Run all** (`Ctrl+F9`)

As células de setup (Parte 1) irão automaticamente:
- Aplicar `nest_asyncio` para compatibilidade com o Colab
- Montar o Google Drive
- Instalar as dependências via `requirements.txt`
- Clonar o repositório do GitHub
- Copiar o `banco.db` para o projeto

### 5. Executar localmente (opcional)

```bash
# 1. Clonar o repositório
git clone https://github.com/JRicLP/GenAI_Ecommerce-Agent.git
cd GenAI_Ecommerce-Agent

# 2. Criar e ativar o ambiente virtual
py -3.13 -m venv venv          # Windows
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar o arquivo .env na raiz do projeto
echo GEMINI_API_KEY=sua-chave-aqui > .env

# 5. Colocar o banco.db na raiz do projeto e executar
```

---

## Funcionalidades

### Text-to-SQL com Gemini 2.5 Flash
O agente converte perguntas em linguagem natural para queries SQL, executa no banco e retorna a resposta explicada em português.

### Gráficos Automáticos
Quando o resultado é tabular e adequado para visualização, o agente sugere e gera automaticamente o gráfico mais apropriado (`barra`, `linha` ou `pizza`) usando Matplotlib.

### Anonimização de Dados Pessoais
Campos como `nome_consumidor` e `nome_vendedor` são automaticamente mascarados antes da exibição. Exemplo: `"Dr. João Silva"` → `"Dr. J. S***"`.

### Retry Automático
O agente trata dois tipos de falha automaticamente:
- **Erros de API (503/429):** aguarda 15 segundos e tenta novamente (até 3 tentativas)
- **SQL inválido:** devolve o erro ao modelo e solicita reescrita (até 2 tentativas)

### Guardrails de Segurança
Quatro camadas de proteção antes de qualquer chamada ao modelo ou ao banco:
1. **Tamanho da pergunta:** máximo de 500 caracteres
2. **Prompt injection:** detecta tentativas de manipulação do agente
3. **Escopo:** bloqueia perguntas fora do contexto de e-commerce
4. **SQL seguro:** apenas queries `SELECT` são permitidas — nenhuma modificação de dados

---

## Exemplos de Perguntas

### Análise de Vendas e Receita
```
Quais são os 10 produtos mais vendidos?
Qual a receita total por categoria de produto?
Qual a quantidade de pedidos por status?
```

### Análise de Entrega e Logística
```
Qual o percentual de pedidos entregues no prazo por estado?
Quais os estados com maior atraso médio nas entregas?
Qual o tempo médio de entrega em dias por estado do consumidor?
```

### Análise de Satisfação e Avaliações
```
Qual a média de avaliação geral dos pedidos?
Quais os 10 vendedores com melhor avaliação média?
Quais categorias de produto têm maior taxa de avaliação negativa?
```

### Análise de Consumidores
```
Quais estados têm maior volume de pedidos e qual o ticket médio?
Quais estados têm maior atraso médio nas entregas para os consumidores?
```

### Análise de Vendedores e Produtos
```
Quais os 3 produtos mais vendidos em SP, RJ, MG, RS e PR?
Quais os 10 vendedores com maior receita total gerada?
```

---

## Guardrails e Segurança

O agente opera em **modo somente leitura**. As seguintes proteções estão implementadas:

| Camada | Tipo | Comportamento |
|--------|------|--------------|
| Tamanho | Pergunta > 500 caracteres | Recusa com mensagem de limite |
| Prompt Injection | Padrões como "ignore as instruções" | Recusa com aviso de segurança |
| Escopo | Perguntas fora do e-commerce | Redireciona para temas válidos |
| SQL | Comandos `INSERT`, `UPDATE`, `DELETE`, `DROP`, etc. | Lança `ValueError` antes da execução |

---

## Categorias de Análise Cobertas

- Análise de Vendas e Receita
- Análise de Entrega e Logística
- Análise de Satisfação e Avaliações
- Análise de Consumidores
- Análise de Vendedores e Produtos