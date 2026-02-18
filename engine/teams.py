from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .types import Team


def load_teams(path: str | Path) -> list[Team]:
	p = Path(path)
	raw = json.loads(p.read_text(encoding="utf-8"))
	teams: list[Team] = []
	for item in raw:
		teams.append(
			Team(
				id=str(item["id"]),
				name=str(item["name"]),
				seed=int(item["seed"]),
				momentum=float(item["momentum"]),
				hype=float(item["hype"]),
				pressure=float(item["pressure"]),
				chaos=float(item["chaos"]),
				brand_code=float(item["brand_code"]),
			)
		)
	if len(teams) != 64:
		raise ValueError(f"Expected 64 teams, got {len(teams)}")
	for t in teams:
		if not (1 <= t.seed <= 16):
			raise ValueError(f"Bad seed for {t.name}: {t.seed}")
	return teams


def group_by_seed(teams: Iterable[Team]) -> dict[int, list[Team]]:
	out: dict[int, list[Team]] = {}
	for t in teams:
		out.setdefault(t.seed, []).append(t)
	return out
