#!/usr/bin/env python3
"""Interview-IQ ledger: one JSON file that holds the case, the interview plan and every exchange.

Usage (paths are examples):
  python ledger.py init --case robotaxi --student "Jane Doe" --out /mnt/user-data/outputs
  python ledger.py init --case-file my_case.json --student "Jane Doe" --out /mnt/user-data/outputs
  python ledger.py plan   --ledger L.json --plan plan.json
  python ledger.py add    --ledger L.json --person zhang --kind root --root 0 --q "..." --a "..."
  python ledger.py add    --ledger L.json --person zhang --kind fu   --root 0 --q "..." --a "..." --src claude
  python ledger.py skip   --ledger L.json --person zhang --root 2
  python ledger.py status --ledger L.json
  python ledger.py log    --ledger L.json [--md out.md]

plan.json: {"summary": "...", "people": [{"id": "zhang", "order": 1, "why": "...",
            "objectives": ["..."], "questions": [{"t": "...", "tags": ["Q1"], "why": "...", "probes": ["..."]}]}]}
"""
import argparse, json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "references")
MAX_FU = 8


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(p, d):
    d["updatedAt"] = datetime.datetime.now().isoformat(timespec="seconds")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    print(f"Saved ledger: {p}")


def person(d, pid):
    for p in d["people"]:
        if p["id"] == pid:
            return p
    sys.exit(f"No interviewee with id '{pid}'. Ids: {', '.join(p['id'] for p in d['people'])}")


def cmd_init(a):
    case = load(a.case_file) if a.case_file else load(os.path.join(REF, f"{a.case}.json"))
    for p in case["people"]:
        p.setdefault("order", 0); p.setdefault("why", ""); p.setdefault("objectives", []); p.setdefault("questions", [])
    d = {"tool": "Interview-IQ", "version": 1, "student": a.student, "case": {k: v for k, v in case.items() if k != "people"},
         "people": case["people"], "strategy": "", "turns": [], "skipped": [],
         "createdAt": datetime.datetime.now().isoformat(timespec="seconds")}
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, f"interview-iq-ledger-{case['id']}.json")
    save(path, d)


def cmd_plan(a):
    d = load(a.ledger); plan = load(a.plan)
    d["strategy"] = plan.get("summary", d.get("strategy", ""))
    ids = [q["id"] for q in d["case"]["assignment"]["questions"]]
    for pp in plan["people"]:
        p = person(d, pp["id"])
        for k in ("order", "why", "objectives", "questions"):
            if k in pp:
                p[k] = pp[k]
        for q in p["questions"]:
            q["tags"] = [t for t in q.get("tags", []) if t in ids]
    save(a.ledger, d)
    coverage(d)


def cmd_add(a):
    d = load(a.ledger); p = person(d, a.person)
    if a.kind == "fu":
        n = sum(1 for t in d["turns"] if t["person"] == a.person and t["root"] == a.root and t["kind"] == "fu")
        if n >= MAX_FU:
            sys.exit(f"Limit reached: {MAX_FU} follow-ups already asked on Q{a.root + 1} for {p['name']}. Move to the next question.")
    d["turns"].append({"person": a.person, "kind": a.kind, "root": a.root, "q": a.q, "a": a.a, "src": a.src,
                       "at": datetime.datetime.now().isoformat(timespec="seconds")})
    save(a.ledger, d)
    progress(d, a.person)


def cmd_skip(a):
    d = load(a.ledger); person(d, a.person)
    d["skipped"].append({"person": a.person, "root": a.root}); save(a.ledger, d); progress(d, a.person)


def progress(d, pid):
    p = person(d, pid)
    asked = {t["root"] for t in d["turns"] if t["person"] == pid and t["kind"] == "root"}
    sk = {s["root"] for s in d["skipped"] if s["person"] == pid}
    nxt = [i for i in range(len(p["questions"])) if i not in asked and i not in sk]
    fu = sum(1 for t in d["turns"] if t["person"] == pid and t["kind"] == "fu")
    print(f"{p['name']}: {len(asked)}/{len(p['questions'])} planned questions answered, {fu} follow-ups. "
          + (f"Next planned: Q{nxt[0] + 1}" if nxt else "All planned questions done."))


def coverage(d):
    qs = [q["id"] for q in d["case"]["assignment"]["questions"]]
    ppl = sorted(d["people"], key=lambda p: p.get("order") or 99)
    print("\nCoverage map (planned questions per memo question)")
    print("| Interviewee | " + " | ".join(qs) + " |")
    print("|---|" + "---|" * len(qs))
    tot = {q: 0 for q in qs}
    for p in ppl:
        row = []
        for q in qs:
            n = sum(1 for x in p["questions"] if q in x.get("tags", []))
            tot[q] += n; row.append(str(n) if n else "–")
        print(f"| {p['name']} | " + " | ".join(row) + " |")
    print("| **Total** | " + " | ".join(f"**{tot[q]}**" + (" ⚠" if not tot[q] else "") for q in qs) + " |")
    gaps = [q for q in qs if not tot[q]]
    if gaps:
        print("\n⚠ No planned question covers: " + ", ".join(gaps))


def cmd_status(a):
    d = load(a.ledger)
    print(f"Case: {d['case']['title']} · Student: {d['student']} · {len(d['turns'])} exchanges logged\n")
    for p in sorted(d["people"], key=lambda p: p.get("order") or 99):
        if p["questions"]:
            progress(d, p["id"])
        else:
            print(f"{p['name']}: no questions planned yet")
    coverage(d)


def build_log(d):
    out = [f"# {d['case']['title']} — Interview Evidence Log", f"Student: {d['student']}", ""]
    for p in sorted(d["people"], key=lambda p: p.get("order") or 99):
        turns = [t for t in d["turns"] if t["person"] == p["id"]]
        if not turns:
            continue
        out += [f"## {p['name']} ({p['role']})", ""]
        for t in turns:
            q = p["questions"][t["root"]] if t["root"] < len(p["questions"]) else {}
            tag = f"Q{t['root'] + 1}" + (f" [{', '.join(q.get('tags', []))}]" if q.get("tags") else "") if t["kind"] == "root" else f"Follow-up to Q{t['root'] + 1}"
            out += [f"**{tag}:** {t['q']}", "", f"**Reply:** {t['a']}", ""]
    return "\n".join(out)


def cmd_log(a):
    d = load(a.ledger); text = build_log(d)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Wrote {a.md}")
    else:
        print(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("init"); s.add_argument("--case", default="robotaxi"); s.add_argument("--case-file"); s.add_argument("--student", default="Student"); s.add_argument("--out", default="/mnt/user-data/outputs")
    s = sp.add_parser("plan"); s.add_argument("--ledger", required=True); s.add_argument("--plan", required=True)
    s = sp.add_parser("add"); s.add_argument("--ledger", required=True); s.add_argument("--person", required=True); s.add_argument("--kind", choices=["root", "fu"], required=True)
    s.add_argument("--root", type=int, required=True); s.add_argument("--q", required=True); s.add_argument("--a", required=True); s.add_argument("--src", default="plan")
    s = sp.add_parser("skip"); s.add_argument("--ledger", required=True); s.add_argument("--person", required=True); s.add_argument("--root", type=int, required=True)
    s = sp.add_parser("status"); s.add_argument("--ledger", required=True)
    s = sp.add_parser("log"); s.add_argument("--ledger", required=True); s.add_argument("--md")
    a = ap.parse_args()
    {"init": cmd_init, "plan": cmd_plan, "add": cmd_add, "skip": cmd_skip, "status": cmd_status, "log": cmd_log}[a.cmd](a)
