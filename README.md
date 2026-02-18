# Signal March Madness Madness 🏀🧾

Your bracket is a personality test wearing a bracket mask.

This repo generates:
- **Share cards** (seed-based bracket personalities)
- **Office Pool Mode** (distribution, superlatives, duels)
- **Share Pack** (`output/sharepack/`) including a Slack-ready post

> Not a prediction engine. Just vibes + math.

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you don’t have requirements.txt, you can usually run with standard library only (depends on your current code).

---

## One Card (single seed)

```bash
python run.py --force --seed 42 --count 1 --roast normal
```

Then open:
- output/share_card_42.txt

---

## Office Pool Mode (the fun one)

```bash
python run.py --force --seed 100 --pool 24 --roast normal
```

This generates:
- output/pool_card.txt
- output/superlatives_card.txt
- output/duel_card.txt
- output/sharepack/POST.txt ← copy/paste into Slack
- plus a ranked leaderboard.json

---

## Share Pack

After Office Pool Mode:

```bash
cat output/sharepack/POST.txt
```

Paste your card. Signal will do the rest.

### Commit + push

```bash
git add README.md
git commit -m "docs: add quick start"
git push
```

---

## Optional nice-to-have (viral README energy)

Add 1 screenshot to the README later: paste one share card + pool card as code blocks.

If you want your next move: we can add a --post-only flag so you can regenerate just the Slack post from an existing run without re-simming anything.
