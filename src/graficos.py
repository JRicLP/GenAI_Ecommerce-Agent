"""Geração automática de gráficos a partir das respostas do agente."""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Paleta de cores consistente em todo o projeto
CORES = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
    "#CCB974", "#64B5CD"
]


def gerar_grafico(
    colunas: list[str],
    linhas: list[list],
    tipo: str,
    titulo: str = ""
) -> None:
    """
    Gera e exibe um gráfico a partir dos dados retornados pelo agente.

    Args:
        colunas: Nomes das colunas do resultado SQL.
        linhas:  Linhas de dados do resultado SQL.
        tipo:    Tipo de gráfico: 'barra', 'linha' ou 'pizza'.
        titulo:  Título exibido no gráfico.
    """
    if not linhas or len(colunas) < 2:
        print("Dados insuficientes para gerar gráfico.")
        return

    # Primeira coluna = rótulos, segunda coluna = valores numéricos
    rotulos = [str(row[0]) for row in linhas]
    try:
        valores = [float(row[1]) for row in linhas]
    except (ValueError, TypeError):
        print("A segunda coluna não é numérica — gráfico não gerado.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    if tipo == "barra":
        bars = ax.barh(rotulos[::-1], valores[::-1], color=CORES[:len(rotulos)])
        ax.bar_label(bars, fmt=_formatar_valor, padding=4, fontsize=9)
        ax.set_xlabel(colunas[1], fontsize=10)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(
            lambda x, _: f"R$ {x:,.0f}" if _e_monetario(colunas[1]) else f"{x:,.0f}"
        ))

    elif tipo == "linha":
        ax.plot(rotulos, valores, marker="o", color=CORES[0], linewidth=2)
        ax.fill_between(range(len(rotulos)), valores, alpha=0.1, color=CORES[0])
        ax.set_xticks(range(len(rotulos)))
        ax.set_xticklabels(rotulos, rotation=45, ha="right", fontsize=9)
        ax.set_ylabel(colunas[1], fontsize=10)

    elif tipo == "pizza":
        wedges, texts, autotexts = ax.pie(
            valores,
            labels=rotulos,
            autopct="%1.1f%%",
            colors=CORES[:len(rotulos)],
            startangle=140
        )
        for text in autotexts:
            text.set_fontsize(9)

    else:
        print(f"Tipo de gráfico '{tipo}' não reconhecido.")
        plt.close()
        return

    ax.set_title(titulo or colunas[0], fontsize=13, fontweight="bold", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.show()


def _e_monetario(nome_coluna: str) -> bool:
    """Verifica se o nome da coluna sugere valor monetário."""
    termos = ["brl", "usd", "receita", "valor", "ticket", "preco", "frete"]
    return any(t in nome_coluna.lower() for t in termos)


def _formatar_valor(valor: float, _) -> str:
    """Formata valores grandes de forma legível."""
    if valor >= 1_000_000:
        return f"{valor/1_000_000:.1f}M"
    if valor >= 1_000:
        return f"{valor/1_000:.1f}K"
    return f"{valor:.1f}"
