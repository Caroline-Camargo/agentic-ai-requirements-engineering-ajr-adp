"""Juiz LLM cego: cada saída é avaliada isoladamente, em ordem embaralhada, sem saber a abordagem.
Uso: python run_judge.py [--tag main] [--passes 2] [--workers 4]
"""
import argparse, json, os, random, re, datetime, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import config, prompts, llm
from scenarios import BY_ID
from run_generation import load

KEYS = list(config.CRITERIA) + ["cx"]

def parse(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        return json.loads(m.group(0)) if m else None

def clean(raw, profile):
    """Valida faixas e aplica a regra de aplicabilidade de c13/c14."""
    row, just = {}, {}
    for k in KEYS:
        n = (raw.get(k) or {}).get("n")
        just[k] = (raw.get(k) or {}).get("j")
        if k in config.CRITERIA:
            lo, hi = config.CRITERIA[k][1]
            n = n if isinstance(n, (int, float)) and lo <= n <= hi else None
        else:
            n = n if isinstance(n, (int, float)) and n >= 0 else None
        row[k] = n
    if profile not in config.C13_PROFILES: row["c13"] = None
    if profile not in config.C14_PROFILES: row["c14"] = None
    return row, just

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="main")
    ap.add_argument("--passes", type=int, default=1)
    ap.add_argument("--model", default=config.JUDGE_MODEL)
    ap.add_argument("--workers", type=int, default=int(os.getenv("WORKERS", "4")))
    a = ap.parse_args()
    gens = load(config.path("generations", a.tag))
    path = config.path("judgments", a.tag)
    done = {(r["gen_id"], r["pass_n"]) for r in load(path)}
    jobs = []
    for p in range(1, a.passes + 1):
        js = [g for g in gens if (g["gen_id"], p) not in done]
        random.Random(config.SEED + p).shuffle(js)       # ordem embaralhada por passada
        jobs += [(g, p) for g in js]
    total = len(jobs)
    print(f"{total} julgamentos pendentes -> {path} (workers: {a.workers})")

    if not jobs:
        return

    write_lock = threading.Lock()
    stop_event = threading.Event()
    completed_count = 0

    def worker(job_data):
        nonlocal completed_count
        if stop_event.is_set():
            return
        g, p = job_data
        sc = BY_ID[g["scenario_id"]]
        prompt = prompts.build_judge_prompt(sc, g["output"])   # NÃO inclui abordagem
        try:
            out = llm.call(a.model, prompt, config.JUDGE_TEMPERATURE, system=prompts.JUDGE_SYSTEM, json_mode=True)
        except llm.DailyQuotaExceeded as e:
            print("\n[!] Saldo ou cota esgotada na API. O progresso foi salvo.\n", str(e)[:200])
            stop_event.set()
            return
        except Exception as e:
            print(f"\n[!] Erro no julgamento de {g['gen_id']}: {e}")
            return

        raw = None
        try: raw = parse(out["text"])
        except Exception: pass
        if raw is None:
            print(f"[!] {g['gen_id']}: JSON inválido retornado pelo juiz, ignorado (será refeito na próxima execução)")
            return

        row, just = clean(raw, g["profile"])
        rec = dict(gen_id=g["gen_id"], pass_n=p, judge_model=a.model, **row, just=just,
                   timestamp=datetime.datetime.now().isoformat(timespec="seconds"))

        with write_lock:
            completed_count += 1
            curr = completed_count
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[{curr}/{total}] {g['gen_id']} pass{p} ok")

    if a.workers <= 1:
        for j in jobs:
            if stop_event.is_set():
                break
            worker(j)
    else:
        with ThreadPoolExecutor(max_workers=a.workers) as executor:
            futures = [executor.submit(worker, j) for j in jobs]
            for f in as_completed(futures):
                if stop_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                try:
                    f.result()
                except Exception as ex:
                    print(f"Erro na thread: {ex}")

if __name__ == "__main__":
    main()
