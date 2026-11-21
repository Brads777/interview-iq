# Interview method

## Plan (outside-in)

- **Order.** Interview neutral or expert sources first to set benchmarks. Then interview competitors and partners. Interview the decision's sponsor, or the person with the most at stake, **last**, so their claims can be tested against the evidence.
- **Objectives.** Give each person 3–6 objectives. Each objective is a specific thing to learn, tied to an assignment question (for example, "cost per mile broken into its drivers (Q1, Q3)").
- **Required themes.** List 5–8 topics the interviews as a whole must cover (for Robotaxi they are pre-loaded: unit economics; safety and technology; regulation, liability and insurance; operating capabilities; channel and partners; competitive response; capital allocation). Cover each with at least one person, and the riskiest with two.
- **Questions.** Write 5–7 open questions per person.
  - **One question, one question mark.** Interviewees push back on bundled questions ("that's three questions, which first?"). Move second and third parts into the probes.
  - Open with a framework question and close with a recommendation question.
  - Cite facts and numbers from the case, so the answer has to be specific.
  - Tag each question to the assignment questions and the themes it serves.
  - Add 1–3 probes per question that dig for numbers, evidence, or bias.
  - Never ask the interviewee to summarize (that synthesis is the student's job) and never ask for a raw data dump (year-by-year financials, a full model). Ask for the one figure that matters, or use the course materials. `ledger.py lint` flags these.
- **Coverage and balance.** Every assignment question needs at least two interviewees. Flag any question that only one interviewee covers, especially when that person has an interest in the outcome. Keep the plans even: no key interviewee should have far fewer planned questions than another.

## Run (one question at a time)

After every reply, decide whether to ask **one** follow-up. Ask one only if the answer:

- gave a vague number, or no number where one was needed,
- made a claim with no support,
- contradicted something said earlier in this or another interview, or
- made a self-serving statement worth testing.

Don't follow up on something a later planned question covers, and don't repeat what was already answered. Stop when the objectives for this question are met.

**Limits** (`ledger.py` enforces them):

- **2 follow-ups per planned question** (the instructor version allows 3). The first follow-up usually brings out the key number or admission; after that, interviewees repeat themselves or decline.
- **About 1.5 follow-ups per planned question across each interview.** This keeps time balanced between interviewees.
- **Clarifying replies don't count.** When the interviewee asks something back ("which part first?", "what's your view?"), the student's answer is logged with `--clar`.
- **Two refusals, then move on.** If the interviewee declines the same item twice ("competitively sensitive"), log the reply with `--declined "<item>"`. The second refusal records it as a gap for the memo. A refusal is evidence too.

Prefer adapting a planned probe when it fits. Otherwise, quote what the interviewee just said. Keep each follow-up to one or two sentences, addressed to the interviewee by name.

## Present each question like this

```
**[Dr. Wei Zhang] · Question 2 of 6 · planned** — tags: Q1
Purpose: Threat of entry, straight from an operator who walked away.

    You explicitly chose not to enter the U.S. What barriers would a new U.S. entrant face that you weren't willing to take on?

Paste the reply here. Or type: skip · probe 1/2/3 · my question: … · status · log
```

Put the question in an indented code block, on its own, so the student can copy it with one click.
