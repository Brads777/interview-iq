#!/usr/bin/env python3
"""Interview-IQ ledger: one JSON file that holds the case, the interview plan and every exchange.

Usage (paths are examples):
  python ledger.py init --case robotaxi --student "Jane Doe" --out /mnt/user-data/outputs
  python ledger.py init --case-file my_case.json --student "Jane Doe" --out /mnt/user-data/outputs
  python ledger.py plan   --ledger L.json --plan plan.json
  python ledger.py add    --ledger L.json --person zhang --kind root --root 0 --q "..." --a "..."
  python ledger.py add    --ledger L.json --person zhang --kind fu   --root 0 --q "..." --a "..." --src claude
  python ledger.py add    ... --kind fu --clar        (your answer to the interviewee's "which part first?" or "your view?": not counted)
  python ledger.py add    ... --declined "cost split" (the reply refused this; after 2 refusals on a question it is logged as a gap)
  python ledger.py lint   --q "question text"
  python ledger.py skip   --ledger L.json --person zhang --root 2
  python ledger.py status --ledger L.json
  python ledger.py log    --ledger L.json [--md out.md]

plan.json: {"summary": "...", "people": [{"id": "zhang", "order": 1, "why": "...",
            "objectives": ["..."], "questions": [{"t": "...", "tags": ["Q1"], "th": ["theme"], "why": "...", "probes": ["..."]}]}],
            "themes": ["optional: replaces the case's required themes"]}
"""
import argparse, json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "references")
MAX_FU = 2          # real follow-ups per planned question (clarifying replies don't count)
FU_PER_ROOT = 1.5   # follow-up budget per interviewee = planned questions x this
MAX_DECLINES = 2    # after this many refusals on one question, log a gap and move on
import re


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
    d = {"tool": "Interview-IQ", "version": 2, "student": a.student, "case": {k: v for k, v in case.items() if k != "people"},
         "people": case["people"], "strategy": "", "themes": case.get("themes", []), "turns": [], "skipped": [], "gaps": [],
         "createdAt": datetime.datetime.now().isoformat(timespec="seconds")}
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, f"interview-iq-ledger-{case['id']}.json")
    save(path, d)


def cmd_plan(a):
    d = load(a.ledger); plan = load(a.plan)
    d["strategy"] = plan.get("summary", d.get("strategy", ""))
    if plan.get("themes"):
        d["themes"] = plan["themes"]
    ids = [q["id"] for q in d["case"]["assignment"]["questions"]]
    for pp in plan["people"]:
        p = person(d, pp["id"])
        for k in ("order", "why", "objectives", "questions"):
            if k in pp:
                p[k] = pp[k]
        for q in p["questions"]:
            q["tags"] = [t for t in q.get("tags", []) if t in ids]
            q["th"] = [t for t in q.get("th", []) if t in d.get("themes", [])]
    save(a.ledger, d)
    coverage(d)
    for p in d["people"]:
        for i, q in enumerate(p["questions"]):
            for w in lint(q["t"]):
                print(f"⚠ {p['name']} Q{i + 1}: {w}")


def lint(text):
    out = []
    if text.count("?") > 1:
        out.append("Asks more than one question. Keep one and move the rest to probes.")
    if re.search(r"\b(summari[sz]e|recap|sum up|key points|key takeaways)\b", text, re.I):
        out.append("Asks the interviewee to summarize. Low value: that synthesis is your job.")
    if re.search(r"\b(year[- ]by[- ]year|line[- ]item|full (model|financials|statements)|all (your|the) (data|numbers|financials))\b", text, re.I):
        out.append("Asks for a raw data dump. Ask for the one figure you need, or use the course materials.")
    return out


def cmd_lint(a):
    w = lint(a.q)
    print("\n".join("⚠ " + x for x in w) if w else "OK: one clear question.")


def real_fu(d, pid, root=None):
    return sum(1 for t in d["turns"] if t["person"] == pid and t["kind"] == "fu" and not t.get("clar")
               and (root is None or t["root"] == root))


def cmd_add(a):
    d = load(a.ledger); p = person(d, a.person)
    if a.kind == "fu" and not a.clar:
        if sum(1 for t in d["turns"] if t["person"] == a.person and t["root"] == a.root and t.get("declined")) >= MAX_DECLINES:
            sys.exit(f"{p['name']} has declined twice on Q{a.root + 1}. It is logged as a gap; move to the next question.")
        if real_fu(d, a.person, a.root) >= MAX_FU:
            sys.exit(f"Limit reached: {MAX_FU} follow-ups already asked on Q{a.root + 1} for {p['name']}. Move to the next question.")
        if real_fu(d, a.person) >= budget(p):
            sys.exit(f"Follow-up budget reached for {p['name']} ({budget(p)}). Use the rest of the time on planned questions.")
    t = {"person": a.person, "kind": a.kind, "root": a.root, "q": a.q, "a": a.a, "src": a.src,
         "at": datetime.datetime.now().isoformat(timespec="seconds")}
    if a.clar:
        t["clar"] = True
    if a.declined:
        t["declined"] = a.declined
    d["turns"].append(t)
    if a.declined:
        n = sum(1 for x in d["turns"] if x["person"] == a.person and x["root"] == a.root and x.get("declined"))
        if n >= MAX_DECLINES:
            g = {"person": a.person, "root": a.root, "item": a.declined}
            d.setdefault("gaps", []).append(g)
            print(f"⚠ Declined twice: '{a.declined}' is logged as a gap for the memo. Move to the next question.")
    save(a.ledger, d)
    progress(d, a.person)


def budget(p):
    import math
    return math.ceil(len(p["questions"]) * FU_PER_ROOT)


def cmd_skip(a):
    d = load(a.ledger); person(d, a.person)
    d["skipped"].append({"person": a.person, "root": a.root}); save(a.ledger, d); progress(d, a.person)


def progress(d, pid):
    p = person(d, pid)
    asked = {t["root"] for t in d["turns"] if t["person"] == pid and t["kind"] == "root"}
    sk = {s["root"] for s in d["skipped"] if s["person"] == pid}
    nxt = [i for i in range(len(p["questions"])) if i not in asked and i not in sk]
    fu = real_fu(d, pid)
    print(f"{p['name']}: {len(asked)}/{len(p['questions'])} planned questions answered, {fu} of {budget(p)} follow-ups used. "
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
    th = d.get("themes", [])
    if th:
        print("\nRequired themes (planned questions covering each)")
        for t in th:
            n = sum(1 for p in ppl for x in p["questions"] if t in x.get("th", []))
            who = sorted({p["name"] for p in ppl for x in p["questions"] if t in x.get("th", [])})
            print(f"- {t}: {n}" + (f" ({', '.join(who)})" if who else " ⚠ nobody covers it"))
    qn = [len(p["questions"]) for p in ppl if p["questions"]]
    if qn and max(qn) - min(qn) > 2:
        print("\n⚠ Uneven plan: " + ", ".join(f"{p['name']} {len(p['questions'])}" for p in ppl if p["questions"]) + " planned questions.")


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
            tag = f"Q{t['root'] + 1}" + (f" [{', '.join(q.get('tags', []))}]" if q.get("tags") else "") if t["kind"] == "root" else ("Clarifying reply" if t.get("clar") else "Follow-up") + f" to Q{t['root'] + 1}"
            out += [f"**{tag}:** {t['q']}", "", f"**Reply{' (declined)' if t.get('declined') else ''}:** {t['a']}", ""]
    g = d.get("gaps", [])
    if g:
        names = {p["id"]: p["name"] for p in d["people"]}
        out += ["## Declined twice (gaps for the memo)", ""] + [f"- {names.get(x['person'], x['person'])}, Q{x['root'] + 1}: {x['item']}" for x in g]
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
    s.add_argument("--clar", action="store_true"); s.add_argument("--declined", default="")
    s = sp.add_parser("lint"); s.add_argument("--q", required=True)
    s = sp.add_parser("skip"); s.add_argument("--ledger", required=True); s.add_argument("--person", required=True); s.add_argument("--root", type=int, required=True)
    s = sp.add_parser("status"); s.add_argument("--ledger", required=True)
    s = sp.add_parser("log"); s.add_argument("--ledger", required=True); s.add_argument("--md")
    a = ap.parse_args()
    {"init": cmd_init, "plan": cmd_plan, "add": cmd_add, "skip": cmd_skip, "status": cmd_status, "log": cmd_log, "lint": cmd_lint}[a.cmd](a)
