"""Gera o perfil de um dataset (CSV ou Excel) para análise exploratória.

Uso:
    python perfil_dataset.py dados.csv --saida relatorio_eda
    python perfil_dataset.py planilha.xlsx --aba "Plan1" --saida relatorio_eda

O arquivo original nunca é alterado.
"""
import argparse
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def ler_dataset(caminho: Path, aba=None) -> pd.DataFrame:
    sufixo = caminho.suffix.lower()
    if sufixo in (".xlsx", ".xls"):
        return pd.read_excel(caminho, sheet_name=aba or 0)
    if sufixo != ".csv":
        sys.exit(f"Formato não suportado: {sufixo}. Use .csv, .xlsx ou .xls.")
    for codificacao in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(caminho, encoding=codificacao) as f:
                amostra = f.read(20000)
            try:
                sep = csv.Sniffer().sniff(amostra, delimiters=",;\t|").delimiter
            except csv.Error:
                sep = ","
            return pd.read_csv(caminho, sep=sep, encoding=codificacao)
        except UnicodeDecodeError:
            continue
    sys.exit("Não foi possível ler o arquivo: codificação desconhecida.")


def fmt(valor, casas=2):
    if pd.isna(valor):
        return "-"
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def resumo_colunas(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    n = len(df)
    for col in df.columns:
        s = df[col]
        info = {
            "coluna": col,
            "tipo": str(s.dtype),
            "nulos": int(s.isna().sum()),
            "pct_nulos": round(100 * s.isna().mean(), 2) if n else 0,
            "valores_unicos": int(s.nunique(dropna=True)),
            "identificador": parece_identificador(s),
        }
        if info["identificador"]:
            pass  # estatísticas de um identificador não têm significado
        elif pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            info.update({
                "media": s.mean(), "mediana": s.median(), "desvio_padrao": s.std(),
                "minimo": s.min(), "maximo": s.max(), "assimetria": s.skew(),
                "outliers_iqr": int(((s < lim_inf) | (s > lim_sup)).sum()),
                "limite_inferior_iqr": lim_inf, "limite_superior_iqr": lim_sup,
            })
        else:
            topo = s.astype(str).value_counts(dropna=True).head(3)
            info["mais_frequentes"] = "; ".join(f"{k} ({v})" for k, v in topo.items())
            normalizado = s.dropna().astype(str).str.strip().str.lower()
            info["grafias_suspeitas"] = int(s.dropna().astype(str).nunique() - normalizado.nunique())
        linhas.append(info)
    return pd.DataFrame(linhas)


def parece_identificador(s: pd.Series) -> bool:
    """Coluna com (quase) um valor diferente por linha (ex.: id, CPF, código).

    Tolera 5% de repetição, porque linhas duplicadas também repetem o id.
    """
    n = s.notna().sum()
    if n <= 20 or s.nunique(dropna=True) < 0.95 * n:
        return False
    if pd.api.types.is_bool_dtype(s):
        return False
    if pd.api.types.is_float_dtype(s):
        return bool((s.dropna() % 1 == 0).all())
    return True


def colunas_numericas(df: pd.DataFrame):
    return [c for c in df.select_dtypes(include="number").columns
            if not pd.api.types.is_bool_dtype(df[c]) and not parece_identificador(df[c])]


def boxplot_horizontal(ax, dados):
    try:
        ax.boxplot(dados, orientation="horizontal")
    except TypeError:  # matplotlib anterior à 3.10
        ax.boxplot(dados, vert=False)


def gerar_graficos(df: pd.DataFrame, pasta: Path, max_colunas=12):
    pasta.mkdir(parents=True, exist_ok=True)
    gerados = []
    numericas = colunas_numericas(df)[:max_colunas]

    nulos = df.isna().mean().mul(100).sort_values(ascending=False)
    nulos = nulos[nulos > 0]
    if len(nulos):
        fig, ax = plt.subplots(figsize=(8, max(3, 0.35 * len(nulos))))
        nulos.sort_values().plot.barh(ax=ax, color="#3b82f6")
        ax.set_xlabel("% de valores nulos")
        ax.set_title("Nulos por coluna")
        fig.tight_layout(); fig.savefig(pasta / "nulos.png", dpi=110); plt.close(fig)
        gerados.append("nulos.png")

    for col in numericas:
        dados = df[col].dropna()
        if dados.empty:
            continue
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.5))
        a1.hist(dados, bins=30, color="#3b82f6", edgecolor="white")
        a1.set_title(f"Distribuição: {col}")
        boxplot_horizontal(a2, dados)
        a2.set_yticks([])
        a2.set_title(f"Boxplot: {col}")
        fig.tight_layout()
        nome = f"num_{''.join(ch if ch.isalnum() else '_' for ch in str(col))}.png"
        fig.savefig(pasta / nome, dpi=110); plt.close(fig)
        gerados.append(nome)

    if len(numericas) >= 2:
        corr = df[numericas].corr()
        lado = max(5, 1.5 + 0.8 * len(numericas))
        fig, ax = plt.subplots(figsize=(lado + 1, lado))
        im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(numericas)), numericas, rotation=45, ha="right")
        ax.set_yticks(range(len(numericas)), numericas)
        for i in range(len(numericas)):
            for j in range(len(numericas)):
                r = corr.iloc[i, j]
                ax.text(j, i, f"{r:.2f}".replace(".", ","), ha="center", va="center", fontsize=9,
                        color="white" if abs(r) > 0.6 else "black")
        fig.colorbar(im, ax=ax, fraction=0.046)
        ax.set_title("Correlação (Pearson)")
        fig.tight_layout(); fig.savefig(pasta / "correlacao.png", dpi=110); plt.close(fig)
        gerados.append("correlacao.png")
    return gerados


def correlacoes_fortes(df: pd.DataFrame, limiar=0.7):
    num = df[colunas_numericas(df)]
    if num.shape[1] < 2:
        return []
    corr = num.corr()
    pares = []
    cols = list(corr.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr.iloc[i, j]
            if pd.notna(r) and abs(r) >= limiar:
                pares.append((cols[i], cols[j], r))
    return sorted(pares, key=lambda p: -abs(p[2]))


def escrever_relatorio(df, resumo, graficos, pares, origem: Path, saida: Path):
    n_lin, n_col = df.shape
    dup = int(df.duplicated().sum())
    L = [f"# Relatório de EDA: {origem.name}", ""]
    L += ["## Visão geral", "",
          f"- Linhas: {n_lin:,}".replace(",", "."),
          f"- Colunas: {n_col}",
          f"- Linhas duplicadas: {dup} ({fmt(100 * dup / n_lin if n_lin else 0)}%)",
          f"- Células nulas: {int(df.isna().sum().sum()):,}".replace(",", ".") +
          f" ({fmt(100 * df.isna().mean().mean())}%)", ""]

    L += ["## Colunas", "", "| Coluna | Tipo | Nulos (%) | Únicos |", "|---|---|---|---|"]
    for _, r in resumo.iterrows():
        L.append(f"| {r['coluna']} | {r['tipo']} | {fmt(r['pct_nulos'])} | {r['valores_unicos']} |")
    L.append("")

    num = resumo[resumo.get("media").notna()] if "media" in resumo else resumo.iloc[0:0]
    if len(num):
        L += ["## Colunas numéricas", "",
              "| Coluna | Média | Mediana | Mín. | Máx. | Assimetria | Outliers (IQR) |",
              "|---|---|---|---|---|---|---|"]
        for _, r in num.iterrows():
            L.append(f"| {r['coluna']} | {fmt(r['media'])} | {fmt(r['mediana'])} | {fmt(r['minimo'])} | "
                     f"{fmt(r['maximo'])} | {fmt(r['assimetria'])} | {int(r['outliers_iqr'])} |")
        L.append("")

    cat = resumo[resumo.get("mais_frequentes").notna()] if "mais_frequentes" in resumo else resumo.iloc[0:0]
    if len(cat):
        L += ["## Colunas de texto ou categóricas", "",
              "| Coluna | Mais frequentes | Grafias suspeitas* |", "|---|---|---|"]
        for _, r in cat.iterrows():
            L.append(f"| {r['coluna']} | {r['mais_frequentes']} | {int(r['grafias_suspeitas'])} |")
        L += ["", "*Valores que só diferem por maiúsculas/minúsculas ou espaços (ex.: \"Natal\" e \"natal \").", ""]

    L += ["## Alertas automáticos", ""]
    alertas = []
    for _, r in resumo.iterrows():
        if r["pct_nulos"] > 40:
            alertas.append(f"- **{r['coluna']}**: {fmt(r['pct_nulos'])}% nulos. Avalie se a coluna é útil.")
        elif r["pct_nulos"] > 5:
            alertas.append(f"- **{r['coluna']}**: {fmt(r['pct_nulos'])}% nulos. Defina como tratar.")
        if r["valores_unicos"] <= 1:
            alertas.append(f"- **{r['coluna']}**: valor constante. Provavelmente pode ser descartada.")
        if r["identificador"]:
            alertas.append(f"- **{r['coluna']}**: um valor diferente por linha. Parece um identificador "
                           f"e ficou fora das estatísticas e dos gráficos.")
        if pd.notna(r.get("outliers_iqr")) and r.get("outliers_iqr", 0) > 0:
            alertas.append(f"- **{r['coluna']}**: {int(r['outliers_iqr'])} outliers pela regra do IQR "
                           f"(fora de {fmt(r['limite_inferior_iqr'])} a {fmt(r['limite_superior_iqr'])}).")
        if pd.notna(r.get("assimetria")) and abs(r["assimetria"]) > 1:
            alertas.append(f"- **{r['coluna']}**: distribuição bem assimétrica ({fmt(r['assimetria'])}).")
        if pd.notna(r.get("grafias_suspeitas")) and r.get("grafias_suspeitas", 0) > 0:
            g = int(r["grafias_suspeitas"])
            alertas.append(f"- **{r['coluna']}**: {g} {'categoria' if g == 1 else 'categorias'} com grafia "
                           f"diferente para o mesmo valor.")
    if dup:
        alertas.append(f"- **Duplicados**: {dup} linhas repetidas por inteiro.")
    L += alertas or ["- Nenhum alerta automático."]
    L.append("")

    L += ["## Correlações fortes (|r| ≥ 0,7)", ""]
    L += [f"- {a} × {b}: {fmt(r)}" for a, b, r in pares] or ["- Nenhuma."]
    L += ["", "Lembrete: correlação não é causalidade.", ""]

    if graficos:
        L += ["## Gráficos", ""] + [f"![{g}](graficos/{g})" for g in graficos]

    (saida / "relatorio.md").write_text("\n".join(L), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description="Gera o perfil de um dataset para EDA.")
    p.add_argument("arquivo", help="Caminho do CSV ou Excel")
    p.add_argument("--saida", default="relatorio_eda", help="Pasta de saída (padrão: relatorio_eda)")
    p.add_argument("--aba", default=None, help="Nome da aba, para arquivos Excel")
    args = p.parse_args()

    origem = Path(args.arquivo)
    if not origem.exists():
        sys.exit(f"Arquivo não encontrado: {origem}")
    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)

    df = ler_dataset(origem, args.aba)
    resumo = resumo_colunas(df)
    resumo.to_csv(saida / "resumo_colunas.csv", index=False, encoding="utf-8-sig", sep=";", decimal=",")
    graficos = gerar_graficos(df, saida / "graficos")
    pares = correlacoes_fortes(df)
    escrever_relatorio(df, resumo, graficos, pares, origem, saida)
    print(f"Pronto: {df.shape[0]} linhas, {df.shape[1]} colunas. Relatório em {saida / 'relatorio.md'}")


if __name__ == "__main__":
    main()
