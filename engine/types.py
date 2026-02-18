from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Team:
	id: str
	name: str
	seed: int  # 1..16
	momentum: float  # 0..1
	hype: float  # 0..1
	pressure: float  # 0..1 (higher = more likely to choke)
	chaos: float  # 0..1 (higher = more variance)
	brand_code: float  # 0..1 synthetic "legacy aura"


@dataclass
class Game:
	slot: str  # e.g. "R1-G01"
	round: int  # 1..6
	team_a: Team
	team_b: Team
	winner: Optional[Team] = None
	reason_tags: Optional[list[str]] = None


@dataclass
class Bracket:
	games: list[Game]


@dataclass
class SignalReport:
	scores: dict[str, float]
	archetype: str
	reasons: list[str]
