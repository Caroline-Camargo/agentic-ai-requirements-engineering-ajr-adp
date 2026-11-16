"""Gera as especificações (abordagens A/B[/C]). Retomável: pula o que já está salvo.
Uso:
  python run_generation.py --pilot                 # 3 cenários x 1 rep x A,B (arquivo separado)
  python run_generation.py                         # 18 x A,B x 3 reps = 108 gerações
  python run_generation.py --approaches A B C      # inclui o controle C (162 gerações)
  python run_generation.py --workers 5             # executa com 5 chamadas simultâneas
"""
import argparse, json, os, random, uuid, datetime, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import config, prompts, llm
from scenarios import SCENARIOS

def load(path):
    if not os.path.exists(path): return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--approaches", nargs="+", default=["A", "B"])
    ap.add_argument("--reps", type=int, default=config.REPS)
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--model", default=config.GEN_MODEL)
    ap.add_argument("--workers", type=int, default=int(os.getenv("WORKERS", "4")))
    a = ap.parse_args()
    tag = a.tag or ("pilot" if a.pilot else "main")
    scs = [s for s in SCENARIOS if s["id"] in ("J1", "N1", "L1")] if a.pilot else SCENARIOS
    reps = 1 if a.pilot else a.reps
    os.makedirs(config.DATA_DIR, exist_ok=True)
    path = config.path("generations", tag)
    done = {(r["scenario_id"], r["approach"], r["rep"]) for r in load(path)}
    jobs = [(s, ap_, r) for r in range(1, reps + 1) for s in scs for ap_ in a.approaches]
    random.Random(config.SEED).shuffle(jobs)   # ordem embaralhada: evita confundir abordagem com deriva da API
    jobs = [j for j in jobs if (j[0]["id"], j[1], j[2]) not in done]
    total = len(jobs)
    print(f"{total} gerações pendentes ({len(done)} já feitas) -> {path} (workers: {a.workers})")

    if not jobs:
        return

    write_lock = threading.Lock()
    stop_event = threading.Event()
    completed_count = 0

    def worker(job_data):
        nonlocal completed_count
        if stop_event.is_set():
            return
        s, ap_, r = job_data
        prompt = prompts.build_generation_prompt(ap_, s["text"])
        try:
            out = llm.call(a.model, prompt, config.GEN_TEMPERATURE)
        except llm.DailyQuotaExceeded as e:
            print("\n[!] Saldo ou cota esgotada na API. O progresso foi salvo.\n", str(e)[:200])
            stop_event.set()
            return
        except Exception as e:
            print(f"\n[!] Erro na chamada do modelo para {s['id']} {ap_} rep{r}: {e}")
            return

        rec = dict(gen_id=uuid.uuid4().hex[:10], scenario_id=s["id"], profile=s["profile"], format=s["format"],
                   approach=ap_, rep=r, model=a.model, temperature=config.GEN_TEMPERATURE, prompt=prompt,
                   output=out["text"], tokens_in=out["tokens_in"], tokens_out=out["tokens_out"],
                   tokens_thinking=out["tokens_thinking"], finish_reason=out["finish_reason"],
                   timestamp=datetime.datetime.now().isoformat(timespec="seconds"))

        with write_lock:
            completed_count += 1
            curr = completed_count
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        warn = "  [!] TRUNCADA?" if "MAX_TOKENS" in str(out["finish_reason"]) else ""
        print(f"[{curr}/{total}] {s['id']} {ap_} rep{r}: {out['tokens_out']} tokens{warn}")

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
