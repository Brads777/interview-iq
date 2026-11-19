# Interview-IQ

**Interview-IQ** is a Claude skill for **research by interview**, built by G. Bradley Scheller for MGT4850 Business Strategy (Northeastern University CPS).

It helps you plan and run interviews with a case's executives:

- Claude drafts an interview strategy, a question bank and a coverage map.
- It gives you one question at a time and suggests follow-ups when an answer leaves a gap.
- It saves every exchange in a ledger file.

When your interviews are done, it builds a **memo template** in the course format and **draft exhibits** from your own interview evidence. **It never writes the memo.** The AutoVision Robotaxi case comes pre-loaded.

## Install (Claude.ai, about five minutes)

1. In Claude.ai, open **Settings → Capabilities** and turn on **Code execution and file creation**.
2. Download **`interview-iq.zip`** from the [latest release](https://github.com/Brads777/interview-iq/releases/latest), under **Assets**. **Do not unzip it.**
   - Do **not** use the green *Code → Download ZIP* button. That downloads the source folders, which Claude.ai will not accept.
3. In **Settings → Capabilities → Skills**, choose **Upload skill** and upload `interview-iq.zip`. Check that **interview-iq** is enabled.
4. Create a Project (for example *Interview-IQ — Robotaxi*), open a new chat in it, and type: `Run Interview-IQ`.

The full setup guide is on the course Canvas page.

## What's inside

```
interview-iq/
  SKILL.md                    how Claude runs Interview-IQ
  references/robotaxi.json    the pre-loaded AutoVision Robotaxi case
  references/method.md        interview planning and follow-up rules
  references/exhibits.md      draft-exhibit rules and schema
  scripts/ledger.py           saves the plan and every exchange
  scripts/build_docs.py       memo template and draft exhibits (Word)
interview-iq.zip              the same folder, ready to upload
```

© 2026 G. Bradley Scheller
