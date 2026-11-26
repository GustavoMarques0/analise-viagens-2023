"""Analyze Brazilian federal official travel records for 2023."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

COLUNAS = [
    "Cargo",
    "Período - Data de início",
    "Período - Data de fim",
    "Valor diárias",
    "Valor passagens",
    "Valor outros gastos",
]
COMPONENTES_DESPESA = ["Valor diárias", "Valor passagens", "Valor outros gastos"]
LIMITES_DURACAO = [-1, 0, 3, 7, 14, 30, 60, 90, 180, np.inf]
ROTULOS_DURACAO = ["0", "1–3", "4–7", "8–14", "15–30", "31–60", "61–90", "91–180", ">180"]


def carregar_viagens(caminho: Path | str) -> pd.DataFrame:
    """Load only the fields needed for analysis and derive duration and expenses."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="Windows-1252",
        decimal=",",
        usecols=COLUNAS,
    )
    inicio = pd.to_datetime(df["Período - Data de início"], format="%d/%m/%Y", errors="coerce")
    fim = pd.to_datetime(df["Período - Data de fim"], format="%d/%m/%Y", errors="coerce")
    df["Dias de viagem"] = (fim - inicio).dt.days
    df = df.drop(columns=["Período - Data de início", "Período - Data de fim"])

    df[COMPONENTES_DESPESA] = df[COMPONENTES_DESPESA].apply(pd.to_numeric, errors="coerce")
    df["Despesas consideradas"] = df[COMPONENTES_DESPESA].sum(
        axis=1, min_count=len(COMPONENTES_DESPESA)
    )
    return df


def resumir_qualidade(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize missing or protected categories without exposing individual rows."""
    cargo = df["Cargo"].fillna("Não identificado")
    protegido = cargo.str.contains("sigilo", case=False, na=False)
    divulgado = cargo.ne("Não identificado") & ~protegido
    indicadores = [
        ("Viagens no arquivo", len(df)),
        ("Viagens sem cargo informado", int(df["Cargo"].isna().sum())),
        ("Viagens com cargo protegido por sigilo", int(protegido.sum())),
        ("Viagens com cargo divulgado", int(divulgado.sum())),
        ("Viagens sem os três valores de despesa", int(df["Despesas consideradas"].isna().sum())),
        ("Viagens sem duração calculável", int(df["Dias de viagem"].isna().sum())),
    ]
    return pd.DataFrame(indicadores, columns=["Indicador", "Quantidade"])


def resumir_por_cargo(df: pd.DataFrame, minimo_participacao: float = 0.01) -> pd.DataFrame:
    """Return the ten most frequent publicly disclosed cargo categories."""
    cargo = df["Cargo"].fillna("Não identificado")
    protegido = cargo.str.contains("sigilo", case=False, na=False)
    divulgado = cargo.ne("Não identificado") & ~protegido
    total_divulgado = int(divulgado.sum())
    if total_divulgado == 0:
        return pd.DataFrame(
            columns=["Cargo", "viagens", "despesa_mediana", "despesa_total", "duracao_mediana_dias", "participacao_pct"]
        )

    por_cargo = (
        df.assign(Cargo=cargo)
        .groupby("Cargo")
        .agg(
            viagens=("Cargo", "size"),
            despesa_mediana=("Despesas consideradas", "median"),
            despesa_total=("Despesas consideradas", "sum"),
            duracao_mediana_dias=("Dias de viagem", "median"),
        )
        .reset_index()
    )
    por_cargo["participacao_pct"] = por_cargo["viagens"] / total_divulgado * 100
    return (
        por_cargo.loc[
            (por_cargo["participacao_pct"] >= minimo_participacao * 100)
            & ~por_cargo["Cargo"].str.contains("sigilo|não identificado", case=False, na=False)
        ]
        .sort_values("viagens", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )


def resumir_por_duracao(df: pd.DataFrame, minimo_viagens: int = 30) -> pd.DataFrame:
    """Summarize expenses by duration band, omitting sparse bands."""
    faixa = pd.cut(df["Dias de viagem"], bins=LIMITES_DURACAO, labels=ROTULOS_DURACAO)
    por_duracao = (
        df.assign(**{"Faixa de duração (dias)": faixa})
        .groupby("Faixa de duração (dias)", observed=False)
        .agg(
            viagens=("Cargo", "size"),
            despesa_mediana=("Despesas consideradas", "median"),
        )
        .reset_index()
    )
    return por_duracao.loc[
        (por_duracao["viagens"] >= minimo_viagens) & por_duracao["despesa_mediana"].notna()
    ].reset_index(drop=True)


def criar_graficos(
    por_cargo: pd.DataFrame,
    por_duracao: pd.DataFrame,
    percentual_sem_cargo: float,
):
    """Create the aggregated charts used in the README and notebook."""
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold", "axes.titlesize": 12})
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1.25, 1]})
    fig.patch.set_facecolor("#F5F2EA")
    for ax in axes:
        ax.set_facecolor("#F5F2EA")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#C9C3B8")
        ax.tick_params(colors="#263238")
        ax.set_axisbelow(True)

    axes[0].grid(axis="x", color="#D9D4CA", linewidth=0.8, alpha=0.8)
    axes[0].barh(por_cargo["Cargo"], por_cargo["viagens"], color="#176B87", height=0.72)
    axes[0].invert_yaxis()
    axes[0].set_title("Cargos com mais viagens\nTop 10 entre cargos divulgados ≥1%")
    axes[0].set_xlabel("Número de viagens")
    axes[0].set_ylabel("")

    axes[1].barh(
        por_duracao["Faixa de duração (dias)"].astype(str),
        por_duracao["despesa_mediana"],
        color="#D27643",
        height=0.72,
    )
    axes[1].invert_yaxis()
    axes[1].set_title("Mediana das despesas por duração\nFaixas com pelo menos 30 viagens")
    axes[1].set_xlabel("Despesa mediana registrada (R$)")
    axes[1].set_ylabel("Duração (dias)")
    axes[1].xaxis.set_major_formatter(
        FuncFormatter(lambda valor, _: f"R$ {valor / 1000:.0f} mil" if valor >= 1000 else f"R$ {valor:.0f}")
    )
    axes[1].grid(axis="x", color="#D9D4CA", linewidth=0.8, alpha=0.8)

    fig.suptitle(
        "Viagens a serviço do governo federal · 2023",
        x=0.06,
        ha="left",
        fontsize=18,
        color="#17252C",
        weight="bold",
    )
    fig.text(
        0.06,
        0.91,
        "Resumo agregado. Despesas = diárias + passagens + outros gastos; devoluções não descontadas.",
        color="#526168",
        fontsize=9,
    )
    fig.text(
        0.06,
        0.025,
        f"Fonte: Portal da Transparência. Cargo ausente em {percentual_sem_cargo:.1f}%; cargos ausentes/protegidos e grupos pequenos omitidos.",
        color="#526168",
        fontsize=9,
    )
    fig.tight_layout(rect=[0.04, 0.08, 0.98, 0.86], w_pad=2.5)
    return fig, axes


def main() -> None:
    parser = argparse.ArgumentParser(description="Resume viagens a serviço do governo federal em 2023.")
    parser.add_argument("--arquivo", type=Path, default=Path("data/raw/2023_Viagem.csv"))
    parser.add_argument("--imagem", type=Path, default=Path("assets/viagens_2023.png"))
    args = parser.parse_args()

    df = carregar_viagens(args.arquivo)
    qualidade = resumir_qualidade(df)
    total = int(qualidade.loc[qualidade["Indicador"] == "Viagens no arquivo", "Quantidade"].iloc[0])
    sem_cargo = int(qualidade.loc[qualidade["Indicador"] == "Viagens sem cargo informado", "Quantidade"].iloc[0])
    por_cargo = resumir_por_cargo(df)
    por_duracao = resumir_por_duracao(df)
    fig, _ = criar_graficos(por_cargo, por_duracao, sem_cargo / total * 100 if total else 0)

    args.imagem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.imagem, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(qualidade.to_string(index=False))
    print(f"\nGráfico salvo em: {args.imagem}")


if __name__ == "__main__":
    main()
