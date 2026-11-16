"""Confere nº de cenários, distribuição perfil x formato e contagem de palavras por formato."""
from collections import Counter
from scenarios import SCENARIOS
RANGES = {"D": (200, 400), "T": (500, 800), "P": (100, 150)}
cells = Counter((s["profile"], s["format"]) for s in SCENARIOS)
print("Total:", len(SCENARIOS))
ok = True
for p in "JNL":
    for f in "DTP":
        flag = "" if cells[(p, f)] == 2 else "  <-- esperado 2"
        ok &= cells[(p, f)] == 2
        print(f"  {p}-{f}: {cells[(p,f)]}{flag}")
for s in SCENARIOS:
    n = len(s["text"].split()); lo, hi = RANGES[s["format"]]
    flag = "OK" if lo <= n <= hi else f"FORA ({lo}-{hi})"
    ok &= lo <= n <= hi
    print(f"{s['id']} [{s['format']}] {n:4d} palavras  {flag}  - {s['title']}")
print("\nTUDO OK" if ok else "\nAJUSTAR os itens marcados")
