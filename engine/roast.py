from __future__ import annotations

from typing import Literal

RoastLevel = Literal["friendly", "normal", "unhinged"]


def select_roast_lines(reasons: list[str], level: RoastLevel) -> list[str]:
    """
    v0.2.1: we keep the existing reasons, then optionally sharpen them.
    No cruelty. No profanity by default. "unhinged" is more aggressive but still not hateful.
    """
    base = (reasons or [])[:3]

    if level == "friendly":
        # Soften phrasing slightly
        softened = []
        for r in base:
            r = r.replace("You ", "You might ")
            r = r.replace("Your ", "Your ")
            softened.append(r)
        return softened

    if level == "unhinged":
        # Add one extra punch line if we have room
        spiced = base[:]
        spiced.append("This is a spreadsheet with a plot twist.")
        return spiced[:3]

    return base
