from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .types import Bracket, Game, Team


def _pair_first_round(teams: list[Team]) -> list[tuple[Team, Team]]:
	"""
	Build first-round matchup pairs by seed:
	(1 vs 16), (8 vs 9), (5 vs 12), (4 vs 13), (6 vs 11), (3 vs 14), (7 vs 10), (2 vs 15)
	We assume 4 regions worth of each seed (64 teams total).
	"""
	by_seed: dict[int, list[Team]] = {}
	for t in teams:
		by_seed.setdefault(t.seed, []).append(t)

	for s in range(1, 17):
		if len(by_seed.get(s, [])) != 4:
			raise ValueError(f"Expected 4 teams for seed {s}, got {len(by_seed.get(s, []))}")

	# Stable ordering to keep output consistent
	for s in by_seed:
		by_seed[s] = sorted(by_seed[s], key=lambda t: t.id)

	pairs: list[tuple[Team, Team]] = []
	matchup = [(1, 16), (8, 9), (5, 12), (4, 13), (6, 11), (3, 14), (7, 10), (2, 15)]
	for region_idx in range(4):
		for a_seed, b_seed in matchup:
			a = by_seed[a_seed][region_idx]
			b = by_seed[b_seed][region_idx]
			pairs.append((a, b))

	return pairs


def build_empty_bracket(teams: list[Team]) -> Bracket:
	pairs = _pair_first_round(teams)
	games: list[Game] = []
	# Round 1 games: 32
	for i, (a, b) in enumerate(pairs, start=1):
		games.append(Game(slot=f"R1-G{i:02d}", round=1, team_a=a, team_b=b, winner=None, reason_tags=[]))
	return Bracket(games=games)


def bracket_to_json(bracket: Bracket) -> dict:
	return {
		"games": [
			{
				"slot": g.slot,
				"round": g.round,
				"team_a": {"id": g.team_a.id, "name": g.team_a.name, "seed": g.team_a.seed},
				"team_b": {"id": g.team_b.id, "name": g.team_b.name, "seed": g.team_b.seed},
				"winner": None
				if g.winner is None
				else {"id": g.winner.id, "name": g.winner.name, "seed": g.winner.seed},
				"reason_tags": g.reason_tags or [],
			}
			for g in bracket.games
		]
	}


def write_bracket(bracket: Bracket, path: str | Path) -> None:
	p = Path(path)
	p.parent.mkdir(parents=True, exist_ok=True)
	p.write_text(json.dumps(bracket_to_json(bracket), indent=2), encoding="utf-8")


def load_bracket(path: str | Path, teams: Iterable[Team]) -> Bracket:
	p = Path(path)
	raw = json.loads(p.read_text(encoding="utf-8"))
	team_by_id = {t.id: t for t in teams}

	games: list[Game] = []
	for item in raw["games"]:
		a = team_by_id[item["team_a"]["id"]]
		b = team_by_id[item["team_b"]["id"]]
		winner = None
		if item.get("winner"):
			winner = team_by_id[item["winner"]["id"]]
		games.append(
			Game(
				slot=str(item["slot"]),
				round=int(item["round"]),
				team_a=a,
				team_b=b,
				winner=winner,
				reason_tags=list(item.get("reason_tags") or []),
			)
		)
	return Bracket(games=games)
