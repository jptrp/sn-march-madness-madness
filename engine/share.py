from __future__ import annotations


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _bar(x: float, width: int = 10) -> str:
    x = _clamp01(x)
    n = int(round(x * width))
    return "█" * n + "░" * (width - n)


def _headline(scores: dict[str, float], archetype: str) -> str:
    oc = float(scores.get("overconfidence", 0.0))
    chaos = float(scores.get("chaos_addiction", 0.0))
    collapse = float(scores.get("collapse_risk", 0.0))
    brand = float(scores.get("brand_bias", 0.0))
    narrative = float(scores.get("narrative_bias", 0.0))

    if chaos < 0.20 and collapse > 0.85 and oc > 0.70:
        return "PLAYED IT SAFE. DIED IMMEDIATELY."
    if chaos > 0.75 and collapse > 0.70:
        return "YOU DIDN’T PICK UPSETS — YOU SUMMONED THEM."
    if brand > 0.80 and oc > 0.60:
        return "THE BRAND WON. YOU JUST WORK HERE."
    if narrative > 0.75 and chaos < 0.55:
        return "YOU BUILT A STORY, NOT A BRACKET."
    if collapse < 0.45:
        return "ANNOYINGLY STABLE. LEGALLY INSPECTABLE."
    return f"{archetype.upper()} ENERGY DETECTED."


def _wrap(text: str, width: int) -> list[str]:
    """
    Word-wrap to width. If a single word exceeds width, hard-split that word.
    """
    text = (text or "").strip()
    if not text:
        return [""]

    words = text.split()
    lines: list[str] = []
    cur = ""

    def push(line: str) -> None:
        if line is not None:
            lines.append(line)

    for w in words:
        if not cur:
            if len(w) <= width:
                cur = w
            else:
                push(w[:width])
                remainder = w[width:]
                while len(remainder) > width:
                    push(remainder[:width])
                    remainder = remainder[width:]
                cur = remainder
        else:
            cand = cur + " " + w
            if len(cand) <= width:
                cur = cand
            else:
                push(cur)
                if len(w) <= width:
                    cur = w
                else:
                    push(w[:width])
                    remainder = w[width:]
                    while len(remainder) > width:
                        push(remainder[:width])
                        remainder = remainder[width:]
                    cur = remainder

    if cur:
        push(cur)

    return lines


def render_share_card(archetype: str, scores: dict[str, float], roast_lines: list[str]) -> str:
    # Box geometry
    inner_width = 46
    content_width = inner_width - 2

    def line(content: str) -> str:
        content = (content or "")[:inner_width]
        return f"║{content:<{inner_width}}║"

    def header(kind: str) -> str:
        if kind == "top":
            return "╔" + ("═" * inner_width) + "╗"
        if kind == "mid":
            return "╠" + ("═" * inner_width) + "╣"
        return "╚" + ("═" * inner_width) + "╝"

    def fmt_metric(label: str, key: str) -> str:
        v = float(scores.get(key, 0.0))
        bar = _bar(v, 10)
        return f"  {label:<14} {bar} {v:>4.2f}"

    head = _headline(scores, archetype)

    roast_display: list[str] = []
    for r in (roast_lines or [])[:3]:
        r = r.strip()
        if not r:
            continue

        bullet = f"• {r}"
        wrapped = _wrap(bullet, content_width)

        for idx, w in enumerate(wrapped):
            if idx == 0:
                roast_display.append("  " + w)
            else:
                roast_display.append("    " + w)

    if len(roast_display) > 3:
        roast_display = roast_display[:3]
        last = roast_display[-1]
        if len(last) >= 3:
            roast_display[-1] = last[:-3] + "..."

    while len(roast_display) < 3:
        roast_display.append("  •")

    lines: list[str] = []
    lines.append(header("top"))
    lines.append(line("            SIGNAL MADNESS REPORT             "))
    lines.append(header("mid"))
    lines.append(line(f"  {head}"))
    lines.append(header("mid"))
    lines.append(line(f"  ARCHETYPE: {archetype}"))
    lines.append(header("mid"))
    lines.append(line(fmt_metric("Overconfidence", "overconfidence")))
    lines.append(line(fmt_metric("Chaos Addiction", "chaos_addiction")))
    lines.append(line(fmt_metric("Narrative Bias", "narrative_bias")))
    lines.append(line(fmt_metric("Brand Bias", "brand_bias")))
    lines.append(line(fmt_metric("Collapse Risk", "collapse_risk")))
    lines.append(header("mid"))
    lines.append(line("  ROAST"))
    for rb in roast_display:
        lines.append(line(rb))
    lines.append(header("mid"))
    lines.append(line("  Your bracket is a personality test."))
    lines.append(line("  Not predictions. Just vibes + math."))
    lines.append(header("bot"))
    return "\n".join(lines)


def get_headline(archetype: str, scores: dict[str, float]) -> str:
    return _headline(scores, archetype)
