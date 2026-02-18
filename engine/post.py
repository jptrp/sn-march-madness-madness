from __future__ import annotations

from typing import Any


def build_post(summary: dict[str, Any], duel_text: str, top3: list[dict[str, Any]]) -> str:
    # Hook: pick the funniest "office truth" + name the cursed award holder
    avg = summary["avg_scores"]
    chaos = float(avg.get("chaos_addiction", 0.0))
    collapse = float(avg.get("collapse_risk", 0.0))

    sup = summary.get("superlatives", {})
    safest = sup.get("safest_but_dead", {})
    cursed_seed = safest.get("seed", None)

    if chaos < 0.15 and collapse > 0.50:
        hook_line_1 = "Office update: we're risk-averse AND still collapsing. Love that for us."
    elif chaos > 0.35:
        hook_line_1 = "Office update: we have a chaos problem. (It's beautiful.)"
    else:
        hook_line_1 = "Office update: your bracket is a personality test and HR agrees."

    seeds = [str(r["seed"]) for r in top3[:3]]
    if cursed_seed is not None:
        hook_line_2 = f"🧾 Safest-but-Dead crown: seed {cursed_seed}.  Today's top seeds: {', '.join(seeds)}"
    else:
        hook_line_2 = f"Today's top seeds: {', '.join(seeds)}"

    cta = (
        "Drop your seed and get profiled.\n\n"
        "`python run.py --force --seed <your_number> --count 1 --roast normal`\n\n"
        "Paste your card. Signal will do the rest."
    )

    post = []
    post.append(hook_line_1)
    post.append(hook_line_2)
    post.append("")
    post.append("```")
    post.append("(POOL)")
    post.append("```")
    post.append("")
    post.append("```")
    post.append("(SUPERLATIVES)")
    post.append("```")
    post.append("")
    post.append("```")
    post.append("(DUEL)")
    post.append("```")
    post.append("")
    post.append(cta)

    # We'll replace placeholders with the actual cards at runtime in run.py
    return "\n".join(post)
