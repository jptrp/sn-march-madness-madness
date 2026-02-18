from __future__ import annotations

from typing import Any


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _irony_boost(scores: dict[str, float]) -> float:
    """
    Viral paradox: safe bracket + early death = comedy.
    """
    oc = float(scores.get("overconfidence", 0.0))
    chaos = float(scores.get("chaos_addiction", 0.0))
    collapse = float(scores.get("collapse_risk", 0.0))

    safe = _clamp01((oc * 0.7) + ((1.0 - chaos) * 0.6))
    early_death = collapse
    return _clamp01(safe * early_death)


def _headline_bonus(headline: str) -> float:
    h = (headline or "").upper()
    if "DIED IMMEDIATELY" in h:
        return 0.18
    if "SUMMONED" in h:
        return 0.16
    if "THE BRAND WON" in h:
        return 0.14
    if "STORY" in h:
        return 0.12
    if "ANNOYINGLY STABLE" in h:
        return 0.10
    return 0.06


def score_shareability(
    archetype: str,
    scores: dict[str, float],
    headline: str,
    roast_lines: list[str],
) -> dict[str, Any]:
    """
    Returns {score: float, breakdown: {...}} for transparency.
    """
    oc = float(scores.get("overconfidence", 0.0))
    chaos = float(scores.get("chaos_addiction", 0.0))
    brand = float(scores.get("brand_bias", 0.0))
    narrative = float(scores.get("narrative_bias", 0.0))
    collapse = float(scores.get("collapse_risk", 0.0))

    irony = _irony_boost(scores)
    chaos_pop = _clamp01(chaos * 0.9 + (collapse * 0.2))
    brand_pop = _clamp01(brand * 0.7 + oc * 0.2)
    story_pop = _clamp01(narrative * 0.8)

    roast_text = " ".join((roast_lines or [])[:3]).strip()
    roast_len = len(roast_text)
    roast_density = _clamp01(1.0 - abs(roast_len - 110) / 140)

    archetype_bonus = {
        "Spreadsheet Liar": 0.16,
        "Chaos Goblin": 0.16,
        "Brand Worshipper": 0.14,
        "Narrative Romantic": 0.13,
        "Quiet Assassin": 0.10,
        "Social Copycat": 0.11,
    }.get(archetype, 0.10)

    meme_axis = max(irony, chaos_pop, brand_pop, story_pop)
    headline_b = _headline_bonus(headline)

    total = _clamp01(
        0.42 * meme_axis
        + 0.18 * roast_density
        + 0.14 * headline_b
        + 0.18 * archetype_bonus
        + 0.08 * _clamp01(collapse * 0.6 + oc * 0.2)
    )

    return {
        "score": float(total),
        "breakdown": {
            "meme_axis": float(meme_axis),
            "irony": float(irony),
            "chaos_pop": float(chaos_pop),
            "brand_pop": float(brand_pop),
            "story_pop": float(story_pop),
            "roast_density": float(roast_density),
            "headline_bonus": float(headline_b),
            "archetype_bonus": float(archetype_bonus),
        },
    }
