# Draft exhibits: what to build and the rules

Write `exhibits.json`, then run `scripts/build_docs.py`. The drafts give the student an evidence-backed starting point. **They are not the analysis.**

## Rules that apply to every exhibit

1. **Use only the student's evidence.** Draw only on the ledger's interview turns, the case background in the ledger, and files the student added. Never use outside knowledge, and never invent a number.
2. **Cite every claim.** Name the source in brackets: `(Zhang)`, `(Okonkwo, follow-up to Q3)`, `(Case: Company tab)`.
3. **Mark missing evidence.** Put a red-flag cell as `[gap: what is missing and who could answer]` rather than guessing.
4. **No conclusions.** Leave out Impact Summaries, the recommendation, ranked alternatives, final ratings, the weighted decision matrix, and memo prose. Where a rating is customary (a force's strength, a VRIN yes/no), give the **evidence for and against** plus a *suggested* rating labeled `suggested: Medium — student to decide`.
5. **Keep it short.** Use table cells of one or two sentences, with at most 8 rows per table.

## exhibits.json schema

```json
{
  "exhibits": [
    {"letter": "E", "title": "Porter's Five Forces", "purpose": "One line on what this exhibit is for.",
     "table": {"columns": ["Force", "Evidence (source)", "Evidence against (source)", "Suggested strength"],
               "rows": [["Threat of new entrants", "…(Zhang)", "…(Drake)", "suggested: Medium — student to decide"]]},
     "bullets": ["optional short points"], "note": "optional caveat"}
  ],
  "gaps": ["Evidence still missing, and who could supply it"]
}
```

## Robotaxi exhibit set (course letters)

| Letter | Title | Memo question | What to draft |
|---|---|---|---|
| C | Industry Overview | Q1 | Rows for definition and scope, market players, operating economics (cost per mile, utilization), regulation, and technology approaches. Use only figures the case and the interviews gave. |
| E | Porter's Five Forces | Q1 | One row per force, plus a row for complementors and partners (RideLink). Show evidence for and against, and a suggested strength. |
| I | VRIN Analysis | Q2 | The assignment's resources: fleet, technology (camera-only), vertical integration, manufacturing scale, brand, and founder/CEO. Columns: Resource, Valuable?, Rare?, Inimitable?, Non-substitutable?, each with evidence, then *Suggested implication (student to decide)*. |
| J-1 | Unit Economics and Financial Ratios | Q3 | Cost per mile, revenue per vehicle, vehicle cost, utilization and burn rate, compared across AutoVision, DragonPath, Apex and LogiPod. Add a ratio block for AutoVision 2020–2025 (revenue growth, margins, cash, capex coverage of $18B). Mark `[gap]` wherever the statements were not obtained. |
| K | SWOT | Q2 | Two to four items per quadrant, each with a source. |
| N | Pros and Cons by Alternative | Q5 | For each of the three alternatives in the case, list evidence-based pros and cons with sources. No ranking and no recommendation. |
| P-1 | Five-Year Scenario Inputs | Q4 | Drivers (vehicles, cities, rides, price per mile, cost per mile, revenue) with the **low and high figures executives stated or implied**, and their sources. Leave the "Your projection" column blank. |
| P-2 | Competitor Responses | Q4 | Apex, RideLink and LogiPod: their likely response in their own words, the evidence behind it, and how credible it is (interest or bias noted). |

Exhibits A, B, L and M are **not** drafted. They are in the memo template for the student to complete.

## Other cases

Use the course letters where they fit: C Industry Overview, D PESTEL, E Five Forces, F Strategic Map, G KSFs, H Resources & Capabilities, I VRIO/VRIN, J Value Chain, J-1 Unit Economics, K SWOT, N Pros and Cons. Draft only the exhibits that the case's assignment asks for, or that the interviews actually support.
