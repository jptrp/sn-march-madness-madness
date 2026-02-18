from __future__ import annotations


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _bar(x: float, width: int = 10) -> str:
    x = _clamp01(x)
    n = int(round(x * width))
    return "█" * n + "░" * (width - n)


def _winner(a: float, b: float) -> str:
    if abs(a - b) < 1e-9:
        return "TIE"
    return "LEFT" if a > b else "RIGHT"


def render_duel_card(left: dict, right: dict) -> str:
    """
    left/right:
      {
        "seed": int,
        "archetype": str,
        "headline": str,
        "scores": {...}
      }
    """
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

    L = left
    R = right
    Ls = L["scores"]
    Rs = R["scores"]

    # Core metrics
    chaos_L = float(Ls.get("chaos_addiction", 0.0))
    chaos_R = float(Rs.get("chaos_addiction", 0.0))

    brand_L = float(Ls.get("brand_bias", 0.0))
    brand_R = float(Rs.get("brand_bias", 0.0))

    survive_L = 1.0 - float(Ls.get("collapse_risk", 0.0))
    survive_R = 1.0 - float(Rs.get("collapse_risk", 0.0))

    danger_L = float(Ls.get("overconfidence", 0.0)) * (1.0 + chaos_L)
    danger_R = float(Rs.get("overconfidence", 0.0)) * (1.0 + chaos_R)

    # Winners
    w_chaos = _winner(chaos_L, chaos_R)
    w_brand = _winner(brand_L, brand_R)
    w_surv = _winner(survive_L, survive_R)
    w_danger = _winner(danger_L, danger_R)

    def crown(side: str, w: str) -> str:
        return "👑" if w == side else "  " if w != "TIE" else "🤝"

    headline = "DUEL: SAFE-AND-SURE vs SAFE-AND-DEAD"

    lines = []
    lines.append(top())
    lines.append(line("              SIGNAL MADNESS — DUEL           "))
    lines.append(mid())
    lines.append(line(f"  {headline}"))
    lines.append(mid())
    lines.append(line(f"  LEFT:  seed {L['seed']}  {L['archetype'][:20]}"))
    lines.append(line(f"  RIGHT: seed {R['seed']}  {R['archetype'][:20]}"))
    lines.append(mid())

    def duel_row(label: str, lv: float, rv: float, w: str) -> None:
        # 46 inner width. We'll format to a fixed template:
        # "  LABEL      LBAR VAL C | C VAL RBAR"
        lbar = _bar(lv, 8)
        rbar = _bar(rv, 8)
        lc = crown("LEFT", w)
        rc = crown("RIGHT", w)

        left_part = f"{lbar} {lv:>4.2f} {lc}"
        right_part = f"{rc} {rv:>4.2f} {rbar}"

        s = f"  {label:<9} {left_part:<15} | {right_part:<18}"
        lines.append(line(s))

    duel_row("CHAOS", chaos_L, chaos_R, w_chaos)
    duel_row("BRAND", brand_L, brand_R, w_brand)
    duel_row("SURVIVE", survive_L, survive_R, w_surv)
    duel_row("DANGER", danger_L, danger_R, w_danger)

    lines.append(mid())

    left_wins = sum(1 for w in [w_chaos, w_brand, w_surv, w_danger] if w == "LEFT")
    right_wins = sum(1 for w in [w_chaos, w_brand, w_surv, w_danger] if w == "RIGHT")

    if left_wins > right_wins:
        verdict = f"  VERDICT: seed {L['seed']} wins ({left_wins}-{right_wins})."
    elif right_wins > left_wins:
        verdict = f"  VERDICT: seed {R['seed']} wins ({right_wins}-{left_wins})."
    else:
        verdict = "  VERDICT: tie. both are a workplace hazard."

    lines.append(line(verdict))
    lines.append(line("  (Personality test wearing a bracket.)"))
    lines.append(bot())
    return "\n".join(lines)
