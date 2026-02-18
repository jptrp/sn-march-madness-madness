from __future__ import annotations

from collections import Counter
from typing import Any


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * p
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    if f == c:
        return xs[f]
    return xs[f] + (xs[c] - xs[f]) * (k - f)


def pool_thresholds(results: list[dict[str, Any]]) -> dict[str, float]:
    keys = ["overconfidence", "chaos_addiction", "narrative_bias", "brand_bias", "collapse_risk"]
    vals = {k: [float(r["scores"].get(k, 0.0)) for r in results] for k in keys}

    return {
        "oc_p75": _percentile(vals["overconfidence"], 0.75),
        "chaos_p75": _percentile(vals["chaos_addiction"], 0.75),
        "narr_p75": _percentile(vals["narrative_bias"], 0.75),
        "brand_p75": _percentile(vals["brand_bias"], 0.75),
        "collapse_p25": _percentile(vals["collapse_risk"], 0.25),
        "collapse_p75": _percentile(vals["collapse_risk"], 0.75),
        "chaos_p25": _percentile(vals["chaos_addiction"], 0.25),
    }


def superlatives(results: list[dict[str, Any]]) -> dict[str, Any]:
    def best(key: str):
        return max(results, key=lambda r: float(r["scores"].get(key, 0.0)))

    def worst(key: str):
        return min(results, key=lambda r: float(r["scores"].get(key, 0.0)))

    most_chaos = best("chaos_addiction")
    most_narr = best("narrative_bias")
    most_brand = best("brand_bias")
    most_oc = best("overconfidence")
    quietest = worst("collapse_risk")

    def safe_but_dead_score(r):
        s = r["scores"]
        return (
            float(s.get("overconfidence", 0.0)) * 0.6
            + (1.0 - float(s.get("chaos_addiction", 0.0))) * 0.4
            + float(s.get("collapse_risk", 0.0)) * 0.6
        )

    safest_but_dead = max(results, key=safe_but_dead_score)

    return {
        "most_chaos": {
            "seed": most_chaos["seed"],
            "archetype": most_chaos["archetype"],
            "value": most_chaos["scores"]["chaos_addiction"],
        },
        "most_narrative": {
            "seed": most_narr["seed"],
            "archetype": most_narr["archetype"],
            "value": most_narr["scores"]["narrative_bias"],
        },
        "most_brand": {
            "seed": most_brand["seed"],
            "archetype": most_brand["archetype"],
            "value": most_brand["scores"]["brand_bias"],
        },
        "most_overconfident": {
            "seed": most_oc["seed"],
            "archetype": most_oc["archetype"],
            "value": most_oc["scores"]["overconfidence"],
        },
        "quiet_assassin": {
            "seed": quietest["seed"],
            "archetype": quietest["archetype"],
            "value": quietest["scores"]["collapse_risk"],
        },
        "safest_but_dead": {
            "seed": safest_but_dead["seed"],
            "archetype": safest_but_dead["archetype"],
            "value": safe_but_dead_score(safest_but_dead),
        },
    }


def summarize_pool(results: list[dict[str, Any]]) -> dict[str, Any]:
    """
    results items: {seed, archetype, headline, shareability_score, scores, ...}
    """
    n = max(1, len(results))
    archetypes = [r["archetype"] for r in results]
    counts = Counter(archetypes)

    dist = [
        {"archetype": k, "count": v, "pct": round((v / n) * 100, 1)}
        for k, v in counts.most_common()
    ]

    avg = {}
    keys = ["overconfidence", "chaos_addiction", "narrative_bias", "brand_bias", "collapse_risk"]
    for k in keys:
        avg[k] = round(sum(float(r["scores"].get(k, 0.0)) for r in results) / n, 3)

    top3 = sorted(results, key=lambda r: r["shareability_score"], reverse=True)[:3]

    thresholds = pool_thresholds(results)
    supers = superlatives(results)

    return {
        "n": n,
        "distribution": dist,
        "avg_scores": avg,
        "top3": top3,
        "thresholds": thresholds,
        "superlatives": supers,
    }


def render_office_summary_card(summary: dict[str, Any]) -> str:
    inner = 46

    def top() -> str:
        return "╔" + ("═" * inner) + "╗"

    def mid() -> str:
        return "╠" + ("═" * inner) + "╣"

    def bot() -> str:
        return "╚" + ("═" * inner) + "╝"

    def line(s: str) -> str:
        s = (s or "")[:inner]
        return f"║{s:<{inner}}║"

    n = summary["n"]
    dist = summary["distribution"]
    avg = summary["avg_scores"]
    top3 = summary["top3"]
    t = summary.get("thresholds", {})

    lines = []
    lines.append(top())
    lines.append(line("            SIGNAL MADNESS - OFFICE POOL       "))
    lines.append(mid())
    lines.append(line(f"  Participants: {n}"))
    lines.append(
        line(
            f"  Avg Collapse Risk: {avg['collapse_risk']:.2f}   Avg Chaos: {avg['chaos_addiction']:.2f}"
        )
    )
    if t:
        lines.append(
            line(
                "  P75 Chaos:{:.2f} Narr:{:.2f} Brand:{:.2f}".format(
                    t.get("chaos_p75", 0.0),
                    t.get("narr_p75", 0.0),
                    t.get("brand_p75", 0.0),
                )
            )
        )
    lines.append(mid())
    lines.append(line("  ARCHETYPE DISTRIBUTION"))
    for item in dist[:5]:
        lines.append(
            line(f"  - {item['archetype']:<18} {item['count']:>2}  ({item['pct']:>4}%)")
        )
    while len(lines) < 13:
        lines.append(line(""))
    lines.append(mid())
    lines.append(line("  TOP 3 MOST SHAREABLE"))
    for i, r in enumerate(top3, start=1):
        lines.append(
            line(f"  {i}) seed {r['seed']:<4} {r['archetype']:<18} {r['shareability_score']:.2f}")
        )
    lines.append(bot())
    return "\n".join(lines)


def render_superlatives_card(summary: dict[str, Any]) -> str:
    inner = 46

    def top() -> str:
        return "╔" + ("═" * inner) + "╗"

    def mid() -> str:
        return "╠" + ("═" * inner) + "╣"

    def bot() -> str:
        return "╚" + ("═" * inner) + "╝"

    def line(s: str) -> str:
        s = (s or "")[:inner]
        return f"║{s:<{inner}}║"

    s = summary["superlatives"]

    lines = []
    lines.append(top())
    lines.append(line("          SIGNAL MADNESS - SUPERLATIVES        "))
    lines.append(mid())
    lines.append(line(f"  🌀 Most Chaotic: seed {s['most_chaos']['seed']} ({s['most_chaos']['value']:.2f})"))
    lines.append(
        line(f"  📣 Most Narrative: seed {s['most_narrative']['seed']} ({s['most_narrative']['value']:.2f})")
    )
    lines.append(line(f"  🏛️ Brand Worshipper: seed {s['most_brand']['seed']} ({s['most_brand']['value']:.2f})"))
    lines.append(
        line(
            f"  😤 Most Overconfident: seed {s['most_overconfident']['seed']} ({s['most_overconfident']['value']:.2f})"
        )
    )
    lines.append(
        line(
            f"  🥷 Quiet Assassin: seed {s['quiet_assassin']['seed']} (collapse {s['quiet_assassin']['value']:.2f})"
        )
    )
    lines.append(mid())
    lines.append(
        line(
            f"  🧾 Safest-but-Dead: seed {s['safest_but_dead']['seed']} (index {s['safest_but_dead']['value']:.2f})"
        )
    )
    lines.append(line(""))
    lines.append(bot())
    return "\n".join(lines)
