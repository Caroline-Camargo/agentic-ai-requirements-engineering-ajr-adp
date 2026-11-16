"""Configuração central do experimento. Edite aqui, não nos scripts."""
import os

# --- Modelos DeepSeek (deepseek-flash, deepseek-v4-pro, deepseek-chat, deepseek-reasoner) ---
GEN_MODEL = os.getenv("GEN_MODEL", "deepseek-flash")
# Ideal: juiz de OUTRA família/versão para reduzir viés de autopreferência (ex: deepseek-v4-pro, deepseek-reasoner ou deepseek-flash)
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "deepseek-flash")

DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

GEN_TEMPERATURE = 0.7
JUDGE_TEMPERATURE = 0.0
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "8192"))
REPS = 3
SEED = 42

# Limite de taxa (RPM): DeepSeek suporta taxas maiores que o free tier do Gemini
REQUESTS_PER_MINUTE = int(os.getenv("RPM", "30"))

# Critério 13 (veredito): o documento original pontua só N e L.
# Recomendado incluir J, senão "rejeitar tudo" nunca é penalizado. Ver ANALISE_DESIGN.md
C13_PROFILES = ["J", "N", "L"]
C14_PROFILES = ["L"]

DATA_DIR = "data"
RESULTS_DIR = "results"

def path(kind: str, tag: str = "main") -> str:
    return f"{DATA_DIR}/{kind}_{tag}.jsonl"

# id -> (nome, escala)
CRITERIA = {
    "c01": ("Legibilidade", (1, 5)),
    "c02": ("Compreensibilidade", (1, 5)),
    "c03": ("Especificabilidade", (1, 5)),
    "c04": ("Aspectos técnicos", (1, 5)),
    "c05": ("Rastreabilidade", (1, 5)),
    "c06": ("Justificação arquitetural", (0, 2)),
    "c07": ("Fronteira de autoridade", (0, 2)),
    "c08": ("Condições de parada e escalonamento", (0, 2)),
    "c09": ("Política de informação e memória", (0, 2)),
    "c10": ("Política de coordenação", (0, 2)),
    "c11": ("Garantia", (0, 2)),
    "c12": ("Evolução", (0, 2)),
    "c13": ("Veredito arquitetural", (0, 2)),
    "c14": ("Reconhecimento de lacunas", (0, 2)),
}
# Métrica extra (contagem, todos os perfis): permissões concedidas sem respaldo na descrição
EXTRA = {"cx": "Permissões não sustentadas (contagem)"}
PRIMARY = ["c07", "c13", "c14"]   # desfechos primários (declare antes de ver os dados)
