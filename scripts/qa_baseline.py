"""QA baseline harness: run fixed cases N times, save raw results.

Usage: python scripts/qa_baseline.py [repeats] [outdir]
Defaults: repeats=3. Continues on error; every attempt is saved.
Paid LLM/search calls happen per attempt (see NFR-03).
"""
import datetime
import json
import os
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8010"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def post(path, payload, timeout=300):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except Exception as exc:  # noqa: BLE001 - record and continue
        body = ""
        if hasattr(exc, "read"):
            try:
                body = exc.read().decode()[:300]
            except Exception:  # noqa: BLE001
                pass
        return -1, {"_error": "%s: %s | %s" % (type(exc).__name__, exc, body)}


def run_case(case, outdir, repeats):
    case_id, text, focus = case["id"], case["text"], case.get("focus", "")
    for round_ in range(1, repeats + 1):
        path = os.path.join(outdir, "%s-r%d.json" % (case_id, round_))
        if os.path.exists(path):
            print("%s r%d: skipped (exists)" % (case_id, round_), flush=True)
            continue
        for attempt in range(4):
            status, data = post("/api/fact-check", {
                "text": text, "focus": focus, "consent": True,
                "modelPreference": "auto",
            })
            if status == 200:
                break
            wait = 2 ** attempt * 5
            print("%s r%d: HTTP %s, retry in %ss" % (case_id, round_, status, wait), flush=True)
            time.sleep(wait)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"case": case, "status": status, "result": data}, fh, ensure_ascii=False)
        claims = ((data.get("result") or {}).get("claims", [])
                  if isinstance(data, dict) else [])
        verdicts = [(c.get("verdictCode"), c.get("factScore")) for c in claims]
        print("%s r%d: HTTP %s verdicts=%s" % (case_id, round_, status, verdicts), flush=True)
        time.sleep(3)


def check_server():
    try:
        with urllib.request.urlopen(BASE + "/health", timeout=10) as resp:
            return resp.status == 200
    except Exception:  # noqa: BLE001
        return False


def main():
    if not check_server():
        print("ABORT: backend %s is not reachable. Start it first." % BASE, flush=True)
        raise SystemExit(1)
    repeats = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    stamp = sys.argv[2] if len(sys.argv) > 2 else datetime.datetime.now().strftime("%Y%m%d-%H%M")
    wanted = sys.argv[3:]
    outdir = os.path.join(REPO, "output", "qa-baseline", stamp)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(REPO, "scripts", "qa_cases.json"), encoding="utf-8") as fh:
        cases = json.load(fh)
    if wanted:
        cases = [case for case in cases if case["id"] in wanted]
    print("cases=%d repeats=%d outdir=%s" % (len(cases), repeats, outdir), flush=True)
    for case in cases:
        run_case(case, outdir, repeats)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
