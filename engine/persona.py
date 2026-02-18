from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class PickerProfile:
    risk_tolerance: float
    narrative_chasing: float
    brand_loyalty: float
    contrarian: float


def profile_from_seed(seed: int) -> PickerProfile:
    rng = random.Random(seed * 9173 + 11)

    risk = min(1.0, max(0.0, rng.betavariate(2.0, 2.6)))
    narrative = min(1.0, max(0.0, rng.betavariate(2.2, 2.2)))
    brand = min(1.0, max(0.0, rng.betavariate(2.6, 2.0)))
    contrarian = min(1.0, max(0.0, rng.betavariate(1.8, 3.0)))

    return PickerProfile(
        risk_tolerance=round(risk, 3),
        narrative_chasing=round(narrative, 3),
        brand_loyalty=round(brand, 3),
        contrarian=round(contrarian, 3),
    )
