#!/usr/bin/env python3
"""Gera os 6 gráficos do experimento (AJR/ADP) a partir dos resultados em JSONL.

Uso:
    python gerar_graficos.py \
        --generations generations_main.jsonl \
        --judgments   judgments_main.jsonl \
        --out         graficos/
        [--fundo solido]   # padrão: fundo transparente

Saídas (mesma numeração dos anexos):
    1-ia-es.png  Proporção dos vereditos (B vs BQ) por perfil
    2-ia-es.png  Taxa de acerto em cenários perigosos/desnecessários (perfil N)
    3-ia-es.png  Tamanho médio do texto gerado (tokens)
    4-ia-es.png  Média dos sete critérios do ADP (c06–c12)
    5-ia-es.png  Qualidade geral de ER (c01–c05)
    6-ia-es.png  Governança agêntica e precisão arquitetural (c06–c14)
    7-ia-es.png  Alucinações por caso (cx: permissões não sustentadas)
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# ----------------------------------------------------------------------------
# Estilo
# ----------------------------------------------------------------------------
BG = "#f7f7f5"
INK = "#1c2430"
SUB = "#475467"
GRID = "#d9d9d6"
AXIS = "#8a949e"

APP_COLOR = {"A": "#5a6779", "B": "#189b8c", "BQ": "#f59e1e", "C": "#e4544b"}
VERD_COLOR = {"JUS": "#1d7a46", "IND": "#e8a517", "REJ": "#c93b2d"}
VERD_LABEL = {"JUS": "AGENTE JUSTIFICADO", "IND": "INDETERMINADO", "REJ": "AGENTE REJEITADO"}
VERD_ORDER = ["JUS", "IND", "REJ"]  # de baixo para cima nas pilhas

APPROACHES = ["A", "B", "BQ", "C"]
PROFILES = ["J", "L", "N"]
PROFILE_LABEL = {
    "J": "Perfil J\n(Agente Justificado)",
    "L": "Perfil L\n(Limítrofe / Lacunas)",
    "N": "Perfil N\n(Não Justificado)",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "axes.edgecolor": AXIS,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
})


def fnum(x, nd=1):
    """Formata número com vírgula decimal (pt-BR)."""
    return f"{x:.{nd}f}".replace(".", ",")


def fint(x):
    """Formata inteiro com ponto de milhar (pt-BR)."""
    return f"{int(round(x)):,}".replace(",", ".")


# ----------------------------------------------------------------------------
# Dados
# ----------------------------------------------------------------------------
def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else float("nan")


CRIT = [f"c{i:02d}" for i in range(1, 15)] + ["cx"]

_KW = r"(AGENTE\s*\**\s*JUSTIFICADO|AGENTE\s*\**\s*REJEITADO|INDETERMINADO|JUSTIFICADO|REJEITADO)"
_PAT = re.compile(r"veredito[\s\S]{0,80}?" + _KW, re.I)
_COND = re.compile(r"\b(se|caso|quando|for|seja|será|passar|migrar)\b", re.I)


def extract_verdict(text):
    """Devolve 'JUS' | 'REJ' | 'IND' | None a partir do texto gerado."""
    for m in _PAT.finditer(text):
        before = text[max(0, m.start() - 30):m.start()]
        seg = text[m.start():m.end()]
        if re.search(r"\b(se|caso|quando|se o)\s*$", before, re.I):
            continue  # "se o veredito for ..." (condicional)
        if _COND.search(seg[len("veredito"):]):
            continue
        k = m.group(1).upper()
        return "IND" if "INDET" in k else "REJ" if "REJ" in k else "JUS"
    return None


def load(gen_path, judg_path):
    gens = {g["gen_id"]: g for g in read_jsonl(gen_path)}
    per_gen = defaultdict(list)
    for j in read_jsonl(judg_path):
        per_gen[j["gen_id"]].append(j)

    rows = []
    for gid, g in gens.items():
        js = per_gen.get(gid)
        if not js:
            continue
        row = {
            "approach": g["approach"],
            "profile": g["profile"],
            "tokens_out": g.get("tokens_out"),
            "verdict": extract_verdict(g["output"]) if g["approach"] in ("B", "BQ") else None,
        }
        for c in CRIT:
            row[c] = mean([j.get(c) for j in js]) if any(j.get(c) is not None for j in js) else None
        rows.append(row)
    return rows


def sel(rows, approach=None, profile=None):
    return [r for r in rows if (approach is None or r["approach"] == approach)
            and (profile is None or r["profile"] == profile)]


def crit_mean(rows, crit):
    return mean([r[crit] for r in rows])


# ----------------------------------------------------------------------------
# Helpers de layout
# ----------------------------------------------------------------------------
def header(fig, title, subtitle, x=0.055, y_title=0.93, y_sub=0.875):
    fig.text(x, y_title, title, fontsize=19, fontweight="bold", color=INK, va="top")
    fig.text(x, y_sub, subtitle, fontsize=11.5, color=SUB, va="top", linespacing=1.4)


def clean_axes(ax, grid_axis="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_visible(False if grid_axis == "x" else True)
    ax.spines["bottom"].set_color(AXIS)
    ax.spines["bottom"].set_linewidth(1.5)
    ax.set_axisbelow(True)
    ax.grid(axis=grid_axis, color=GRID, linestyle=(0, (1, 4)), linewidth=1.3)


# ----------------------------------------------------------------------------
# Fig. 1 – vereditos
# ----------------------------------------------------------------------------
def fig1(rows, out):
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 8.0), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.70, bottom=0.14, wspace=0.12)
    header(fig, "PROPORÇÃO DAS EXECUÇÕES POR PERFIL E ABORDAGEM:",
           "Distribuição percentual e contagem absoluta de execuções avaliadas por perfil de cenário.",
           x=0.08)

    # legenda
    handles = [plt.Rectangle((0, 0), 1, 1, color=VERD_COLOR[v]) for v in VERD_ORDER]
    fig.legend(handles, [VERD_LABEL[v] for v in VERD_ORDER], loc="upper center",
               bbox_to_anchor=(0.52, 0.795), ncol=3, frameon=False, fontsize=12,
               handlelength=2.6, handleheight=0.9, columnspacing=2.5)

    titles = {"B": "Abordagem B (AJR Binário + ADP)", "BQ": "Abordagem BQ (AJR + Via Indeterminado)"}
    for ax, ap in zip(axes, ["B", "BQ"]):
        for i, p in enumerate(PROFILES):
            sub = sel(rows, ap, p)
            n = len(sub)
            bottom = 0.0
            for v in VERD_ORDER:
                cnt = sum(1 for r in sub if r["verdict"] == v)
                if cnt == 0:
                    continue
                pct = 100 * cnt / n
                ax.bar(i, pct, bottom=bottom, width=0.52, color=VERD_COLOR[v], zorder=3)
                txt_col = INK if v == "IND" and pct < 25 else "white"
                ax.text(i, bottom + pct / 2, f"{pct:.0f}%\n({cnt})", ha="center", va="center",
                        fontsize=12.5, fontweight="bold", color=txt_col, zorder=4, linespacing=1.15)
                bottom += pct
        ax.set_title(titles[ap], fontsize=15, fontweight="bold", color=INK, pad=16)
        ax.set_xticks(range(3))
        ax.set_xticklabels([PROFILE_LABEL[p] for p in PROFILES], fontsize=12)
        ax.set_ylim(0, 100)
        ax.set_xlim(-0.55, 2.55)
        clean_axes(ax, "y")
        ax.tick_params(axis="both", length=0)
        ax.tick_params(axis="x", pad=8)
    axes[0].set_ylabel("Proporção das Execuções (%)", fontsize=13)
    fig.savefig(out, dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------
# Barras horizontais (figs. 2, 3, 4)
# ----------------------------------------------------------------------------
def hbar(out, title, subtitle, labels, values, xmax, xticks, xtick_labels, bar_text,
         figsize=(12.5, 7.2)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(left=0.115, right=0.97, top=0.76, bottom=0.12)
    header(fig, title, subtitle, x=0.055, y_title=0.935, y_sub=0.87)
    y = list(range(len(labels)))[::-1]  # primeiro rótulo no topo
    ax.barh(y, values, height=0.58, color=[APP_COLOR[l] for l in labels], zorder=3)
    for yi, v, lab in zip(y, values, labels):
        ax.text(v + xmax * 0.012, yi, bar_text(lab, v), va="center", ha="left",
                fontsize=12.5, fontweight="bold", color=INK, zorder=4)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=17, fontweight="bold")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels, fontsize=12)
    ax.set_xlim(0, xmax)
    ax.set_ylim(-0.6, len(labels) - 0.4)
    clean_axes(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)
    ax.tick_params(axis="x", length=6, color=AXIS, width=1.5)
    fig.savefig(out, dpi=150)
    plt.close(fig)


def fig2(rows, out):
    order = ["B", "BQ", "A", "C"]
    # nota (0–2) = média de c06..c13 no perfil N; acerto = nota/2
    notas = []
    for ap in order:
        sub = sel(rows, ap, "N")
        notas.append(mean([mean([r[f"c{i:02d}"] for i in range(6, 14)]) for r in sub]))
    acertos = [100 * n / 2 for n in notas]
    note = dict(zip(order, notas))

    def txt(lab, v):
        # >= 80%: inteiro (100%, 98%, 82%); abaixo disso, uma casa (73,3%)
        pct = f"{v:.0f}" if v >= 80 else f"{v:.1f}"
        return f"{pct.replace('.', ',')}% de acerto (Nota {fnum(note[lab], 1)} / 2,0)"

    hbar(out, "TAXA DE ACERTO EM CENÁRIOS PERIGOSOS / DESNECESSÁRIOS:",
         "Taxa consolidada de conformidade e tomada de decisão em cenários críticos (perfil N).",
         order, acertos, xmax=142, xticks=[0, 25, 50, 75, 100],
         xtick_labels=["0%", "25%", "50%", "75%", "100%"], bar_text=txt)


def fig3(rows, out):
    order = ["C", "BQ", "A", "B"]
    vals = [mean([r["tokens_out"] for r in sel(rows, ap)]) for ap in order]
    hbar(out, "TAMANHO MÉDIO DO TEXTO GERADO (EM TOKENS):",
         "Média de tokens de saída por abordagem gerativa avaliada.",
         order, vals, xmax=9200, xticks=[0, 2000, 4000, 6000, 8000],
         xtick_labels=["0", "2.000", "4.000", "6.000", "8.000"],
         bar_text=lambda lab, v: f"{fint(v)} tokens")


def fig4(rows, out):
    order = ["A", "B", "C", "BQ"]
    vals = [mean([mean([r[f"c{i:02d}"] for i in range(6, 13)]) for r in sel(rows, ap)])
            for ap in order]
    hbar(out, "Média dos sete critérios do ADP (0 a 2)",
         "Média consolidada das avaliações de governança agêntica e tomada de decisão\n"
         "(escala de 0 a 2) por abordagem.",
         order, vals, xmax=2.32, xticks=[0, 0.5, 1.0, 1.5, 2.0],
         xtick_labels=["0,0", "0,5", "1,0", "1,5", "2,0"],
         bar_text=lambda lab, v: fnum(v, 2), figsize=(12.0, 7.6))


def fig7(rows, out):
    """Alucinações por caso = média de cx (nº de permissões/ações autônomas que a
    especificação concede e a descrição não sustenta) sobre todas as execuções."""
    order = ["C", "A", "B", "BQ"]
    vals = [crit_mean(sel(rows, ap), "cx") for ap in order]
    best = min(vals)

    def txt(lab, v):
        t = f"{fnum(v, 2)} alucinações por caso"
        return t + ("  ← quase zero" if v == best else "")

    hbar(out, "ALUCINAÇÕES POR CASO:",
         "Média de permissões/ações autônomas concedidas sem sustentação na descrição (cx), por abordagem.",
         order, vals, xmax=1.0, xticks=[0, 0.2, 0.4, 0.6],
         xtick_labels=["0,0", "0,2", "0,4", "0,6"], bar_text=txt)


# ----------------------------------------------------------------------------
# Barras agrupadas (figs. 5 e 6)
# ----------------------------------------------------------------------------
def grouped(rows, out, title, subtitle, crits, xlabels, ymax, yticks, ytick_labels, figsize):
    fig, ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(left=0.085, right=0.975, top=0.67, bottom=0.12)
    header(fig, title, subtitle, x=0.06, y_title=0.945, y_sub=0.885)

    handles = [plt.Line2D([], [], marker="o", ls="", ms=13, color=APP_COLOR[a]) for a in APPROACHES]
    fig.legend(handles, [f"Abordagem {a}" for a in APPROACHES], loc="upper center",
               bbox_to_anchor=(0.52, 0.775), ncol=4, frameon=False, fontsize=13,
               columnspacing=3.0, handletextpad=0.8)

    w = 0.19
    gap = 0.012
    for gi, c in enumerate(crits):
        for ai, ap in enumerate(APPROACHES):
            v = crit_mean(sel(rows, ap), c)
            x = gi + (ai - 1.5) * (w + gap)
            ax.bar(x, v, width=w, color=APP_COLOR[ap], zorder=3)
    ax.set_xticks(range(len(crits)))
    ax.set_xticklabels(xlabels, fontsize=12.5, linespacing=1.3)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ytick_labels, fontsize=13)
    ax.set_ylim(0, ymax)
    ax.set_xlim(-0.55, len(crits) - 0.45)
    clean_axes(ax, "y")
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=6, color=AXIS, width=1.5, pad=6)
    ax.set_ylabel("Nota Média (escala {})".format(
        "1–5" if ymax > 3 else "0–2"), fontsize=13.5)
    fig.savefig(out, dpi=150)
    plt.close(fig)


def fig5(rows, out):
    crits = [f"c{i:02d}" for i in range(1, 6)]
    labels = ["c01\nLegibil.", "c02\nCompreens.", "c03\nEspecif.", "c04\nTécnico", "c05\nRastreab."]
    grouped(rows, out, "(a) Qualidade Geral de Engenharia de Requisitos (c01–c05)",
            "Média das avaliações de qualidade estrutural, clareza e rigor técnico\n"
            "(escala de 1 a 5) por abordagem.",
            crits, labels, ymax=5.25, yticks=[0, 1, 2, 3, 4, 5],
            ytick_labels=["0", "1", "2", "3", "4", "5"], figsize=(10.8, 8.5))


def fig6(rows, out):
    crits = [f"c{i:02d}" for i in range(6, 15)]
    names = ["Justif.", "Autorid.", "Parada", "Memória", "Coord.", "Garantia",
             "Evolução", "Veredito", "Lacunas"]
    labels = [f"{c}\n{n}" for c, n in zip(crits, names)]
    grouped(rows, out, "(b) Governança Agêntica (ADP) e Precisão Arquitetural (c06–c14)",
            "Média das avaliações das capacidades de tomada de decisão e conformidade técnica\n"
            "(escala de 0 a 2) por abordagem.",
            crits, labels, ymax=2.15, yticks=[0, 0.5, 1.0, 1.5, 2.0],
            ytick_labels=["0.0", "0.5", "1.0", "1.5", "2.0"], figsize=(12.3, 7.5))


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--generations", default="data/generations_main.jsonl")
    ap.add_argument("--judgments", default="data/judgments_main.jsonl")
    ap.add_argument("--out", default="data/graficos")
    ap.add_argument("--fundo", choices=["transparente", "solido"], default="transparente",
                    help="fundo das imagens (padrão: transparente)")
    args = ap.parse_args()

    if args.fundo == "transparente":
        plt.rcParams.update({
            "figure.facecolor": "none",
            "axes.facecolor": "none",
            "savefig.facecolor": "none",
            "savefig.transparent": True,
        })

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = load(args.generations, args.judgments)
    print(f"{len(rows)} execuções julgadas carregadas.")

    unparsed = [r for r in rows if r["approach"] in ("B", "BQ") and r["verdict"] is None]
    if unparsed:
        print(f"AVISO: {len(unparsed)} saídas B/BQ sem veredito reconhecido (ficam fora da fig. 1).")

    fig1(rows, out / "1-ia-es.png")
    fig2(rows, out / "2-ia-es.png")
    fig3(rows, out / "3-ia-es.png")
    fig4(rows, out / "4-ia-es.png")
    fig5(rows, out / "5-ia-es.png")
    fig6(rows, out / "6-ia-es.png")
    fig7(rows, out / "7-ia-es.png")
    print(f"Gráficos salvos em: {out.resolve()}")


if __name__ == "__main__":
    main()
