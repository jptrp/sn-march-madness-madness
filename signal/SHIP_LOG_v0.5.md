# SIGNAL CAPTURE — sn-march-madness-madness v0.5 (Ship Log)

**Date**: 2026-02-17  
**Workspace**: `sn-march-madness-madness`  
**Release**: `v0.5` (tagged + pushed)  
**Intent**: Ship the meme artifact pipeline, then stop.

---

## Context (Why this happened)

A throwback memory: first QA job at Workiva during March Madness.  
One Test Engineer built a "crazy Python program for brackets" and I remember being impressed.

Today wasn't about March Madness.  
It was about recreating that category of project **with modern Signal behavior**:

- deterministic + seed-based outputs
- personality scoring instead of prediction claims
- artifact-first delivery
- shareability as a first-class output
- frictionless entry point (`--seed random`)
- clean repo + release tag

---

## What We Built

### Core Engine
- Bracket simulation + scoring → **Signal Report** + **Share Card**
- Scores: Overconfidence, Chaos Addiction, Narrative Bias, Brand Bias, Collapse Risk
- Roast lines (vibes + math) rendered inside a fixed-width box
- CLI supports `--seed`, `--count`, `--pool`, `--roast`, `--out`, `--force`

### Office Pool Mode
A single command generates a whole office-worth of "people":
- pool distribution
- percentile thresholds (self-calibrating archetypes)
- Top 3 "most shareable"
- Superlatives card
- Duel card (best contrast pair)
- Share Pack folder with everything needed to post

### Output Artifacts
- `output/share_card_<seed>.txt`
- `output/signal_report_<seed>.md`
- `output/pool_card.txt`
- `output/superlatives_card.txt`
- `output/duel_card.txt`
- `output/sharepack/POST.txt` (Slack-ready post)
- `output/leaderboard.json`

---

## The Viral Mechanism (What makes it work)

This is the key insight:

> It's not a bracket predictor.  
> It's a personality test wearing a bracket mask.

The product is not "better picks."  
The product is: **"press button → meme artifact → postable."**

---

## Final Demo Run (Closing the Day)

Activated venv:
```bash
source /Users/dustinbraun/Career/sn-march-madness-madness/.venv/bin/activate

Ran the full demo pipeline:

python run.py --force --seed random --pool 24 --roast normal && cat output/sharepack/POST.txt

Console confirmed frictionless execution:
	•	Random seed generated + printed
	•	Card path printed
	•	Sharepack produced
	•	POST printed (copy/paste ready)

Random seed from this run:
	•	Base seed: 390303303
	•	Pool seeds: 390303303 … 390303326

Pool summary highlights:
	•	Archetype distribution:
	•	Social Copycat: 10 (41.7%)
	•	Chaos Goblin: 6 (25.0%)
	•	Narrative Romantic: 6 (25.0%)
	•	Brand Worshipper: 1 (4.2%)
	•	Quiet Assassin: 1 (4.2%)
	•	Top 3 shareable:
	1.	390303315 — Chaos Goblin — 0.50
	2.	390303319 — Narrative Romantic — 0.50
	3.	390303316 — Brand Worshipper — 0.49

POST headline produced:
	•	"Office update: we're risk-averse AND still collapsing. Love that for us."
	•	"🧾 Safest-but-Dead crown: seed 390303309. Today's top seeds: 390303315, 390303319, 390303316"
	•	CTA: "Paste your card. Signal will do the rest."

⸻

Engineering Hygiene (Why this is real)
	•	Git repo created + pushed: https://github.com/jptrp/sn-march-madness-madness.git
	•	.gitignore added (no __pycache__, output/, .venv/)
	•	README includes quick start + demo command
	•	Release tagged:
	•	v0.5 — "Signal March Madness Madness v0.5"

⸻

Reflection (Close the loop)

I closed the loop on the Workiva memory.

Back then: impressed by someone else's bracket tool.
Now: built a whole artifact pipeline that's funnier, cleaner, and shippable.

And the best part: I'm not chasing the next feature.

The day ends here. v0.5 shipped. Let it rest.

⸻

Next Move (Intentionally deferred)

No more features tonight.

If I feel the urge to tweak tomorrow:
	•	note the urge
	•	re-run the demo command
	•	don't change code unless it breaks

Ship energy is rare. Preserve it.

---

## Close-Out Note (2026-02-18)

I want to see this project come to life as a UI.
I am explicitly not tweaking anything tonight.

Future move:
- Write an agent exploration brief for UI concepts only.
- No code changes until that brief exists.
