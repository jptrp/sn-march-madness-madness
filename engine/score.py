from __future__ import annotations

import random
from collections import Counter

from .simulate import pick_winner
from .types import Bracket, SignalReport, Team


def _clamp01(x: float) -> float:
	return max(0.0, min(1.0, x))


def _avg(vals: list[float]) -> float:
	return sum(vals) / max(1, len(vals))


def _seed_gap(a: Team, b: Team) -> int:
	return abs(a.seed - b.seed)


def _winner_and_loser(game) -> tuple[Team, Team]:
	assert game.winner is not None
	loser = game.team_b if game.winner is game.team_a else game.team_a
	return game.winner, loser


def _archetype(scores: dict[str, float]) -> str:
	oc = float(scores.get("overconfidence", 0.0))
	chaos = float(scores.get("chaos_addiction", 0.0))
	brand = float(scores.get("brand_bias", 0.0))
	narrative = float(scores.get("narrative_bias", 0.0))
	collapse = float(scores.get("collapse_risk", 0.0))

	# 1) Strong single-axis archetypes (orthogonal triggers)
	if chaos >= 0.62:
		return "Chaos Goblin"

	if narrative >= 0.72:
		return "Narrative Romantic"

	if brand >= 0.78:
		return "Brand Worshipper"

	# 2) Paradox archetype (safe-but-wrong energy)
	# Note: do NOT require collapse here; it's already funny even when stable.
	if oc >= 0.74 and chaos <= 0.20:
		return "Spreadsheet Liar"

	# 3) Stability archetype
	if collapse <= 0.38:
		return "Quiet Assassin"

	# 4) Fallback bucket
	return "Social Copycat"


def score_bracket(bracket: Bracket, rng: random.Random, sims: int = 400) -> SignalReport:
	"""
	Scores a completed bracket (must have winners for all games in rounds 1..6).
	If bracket is partially filled, scores based on available picks and estimates risk.
	"""
	played = [g for g in bracket.games if g.winner is not None]
	if not played:
		raise ValueError("Bracket has no winners yet. Generate picks first.")

	# Upset addiction: count upsets weighted by seed gap and round importance
	upset_weights: list[float] = []
	brand_favorite_picks: list[float] = []
	narrative_picks: list[float] = []
	favorite_confidence: list[float] = []

	tag_counts = Counter()
	for g in played:
		winner, loser = _winner_and_loser(g)
		gap = _seed_gap(g.team_a, g.team_b)
		is_upset = winner.seed > loser.seed

		# Round weight: later upsets are "bolder"
		round_w = 0.65 + (g.round * 0.10)

		if is_upset:
			upset_weights.append(_clamp01((gap / 15.0) * round_w))
		else:
			upset_weights.append(0.0)

		# Brand bias proxy: picking higher brand_code when it's not justified by momentum
		brand_pull = winner.brand_code - loser.brand_code
		momentum_pull = winner.momentum - loser.momentum
		brand_favorite_picks.append(_clamp01(0.5 + (brand_pull - 0.5 * momentum_pull)))

		# Narrative bias: choosing hype over momentum
		hype_pull = winner.hype - loser.hype
		narrative_picks.append(_clamp01(0.5 + (hype_pull - 0.6 * momentum_pull)))

		# Overconfidence: picking favorites repeatedly with low chaos tolerance
		favored = winner.seed < loser.seed
		if favored:
			favorite_confidence.append(_clamp01(0.55 + (gap / 18.0) - winner.chaos * 0.25))

		for t in (g.reason_tags or []):
			tag_counts[t] += 1

	chaos_addiction = _clamp01(_avg(upset_weights) * 1.35)
	brand_bias = _clamp01(_avg(brand_favorite_picks))
	narrative_bias = _clamp01(_avg(narrative_picks))
	overconfidence = _clamp01(_avg(favorite_confidence) if favorite_confidence else 0.45)

	# Collapse risk: estimate via Monte Carlo vs a simulated "reality"
	# We simulate tournament outcomes and measure mismatch depth.
	# If your bracket disagrees early, you "die" early.
	collapse_risk = _estimate_collapse_risk(bracket, rng, sims=sims)

	scores = {
		"overconfidence": overconfidence,
		"chaos_addiction": chaos_addiction,
		"brand_bias": brand_bias,
		"narrative_bias": narrative_bias,
		"collapse_risk": collapse_risk,
	}

	archetype = _archetype(scores)
	reasons = _reasons_from(scores, tag_counts)

	return SignalReport(scores=scores, archetype=archetype, reasons=reasons)


def _estimate_collapse_risk(bracket: Bracket, rng: random.Random, sims: int) -> float:
	"""
	Simulate plausible "realities" and compute how early your bracket diverges.
	Outputs 0..1 where 1 = collapses early often.
	"""
	# Organize picks by slot
	pick_by_slot: dict[str, str] = {}
	for g in bracket.games:
		if g.winner is not None:
			pick_by_slot[g.slot] = g.winner.id

	# We'll recreate the tournament structure from the played bracket's initial R1 matchups.
	# Use bracket games order: R1 games define the field.
	r1_games = [g for g in bracket.games if g.round == 1]
	if len(r1_games) != 32:
		# If bracket isn't full, degrade gracefully
		r1_games = r1_games[:32]

	def simulate_one() -> float:
		"""
		Returns survival fraction 0..1 where 1 = matched all picked games.
		Weighted by round so later matches count more.
		"""
		current = [(g.team_a, g.team_b, f"R1-G{idx:02d}") for idx, g in enumerate(r1_games, start=1)]
		matched = 0.0
		possible = 0.0

		for rnd in range(1, 7):
			winners: list[Team] = []
			round_weight = 0.7 + (rnd * 0.25)

			for i, (a, b, slot) in enumerate(current, start=1):
				w, _tags = pick_winner(a, b, rng, rnd, mode="reality")
				winners.append(w)

				if slot in pick_by_slot:
					possible += round_weight
					if pick_by_slot[slot] == w.id:
						matched += round_weight

			next_current: list[tuple[Team, Team, str]] = []
			for j in range(0, len(winners), 2):
				if j + 1 >= len(winners):
					break
				next_slot = f"R{rnd+1}-G{(j//2)+1:02d}"
				next_current.append((winners[j], winners[j + 1], next_slot))
			current = next_current

			if not current:
				break

		if possible <= 0:
			return 0.0
		return matched / possible

	survivals = []
	for _ in range(max(80, sims)):
		survivals.append(simulate_one())

	avg_survival = sum(survivals) / len(survivals)
	return _clamp01(1.0 - avg_survival)


def _reasons_from(scores: dict[str, float], tags) -> list[str]:
	lines: list[str] = []

	if scores["chaos_addiction"] > 0.75:
		lines.append("You picked upsets like you were speedrunning regret.")
	elif scores["chaos_addiction"] < 0.40:
		lines.append("You avoided upsets like they were a malware attachment.")

	if scores["overconfidence"] > 0.75:
		lines.append("Your confidence is louder than your math.")
	elif scores["overconfidence"] < 0.45:
		lines.append("You hedge emotionally, even when the bracket begs for a stance.")

	if scores["brand_bias"] > 0.75:
		lines.append("You bowed to legacy aura. The brand owns you.")
	elif scores["brand_bias"] < 0.40:
		lines.append("You rejected brand names on principle. Respectfully: that's suspicious.")

	if scores["narrative_bias"] > 0.70:
		lines.append("You fell for hype. You're drafting storylines, not winners.")
	elif scores["narrative_bias"] < 0.45:
		lines.append("You ignored the storyline and followed the signal. Cold-blooded.")

	if scores["collapse_risk"] > 0.70:
		lines.append("This bracket has early-collapse energy. Beautiful, tragic, inevitable.")
	elif scores["collapse_risk"] < 0.45:
		lines.append("This bracket is annoyingly stable. You will be insufferable about it.")

	# Add one tag-based flavor line
	if tags.get("big_upset", 0) >= 4:
		lines.append("You didn't just pick chaos-you hosted it.")
	if tags.get("choke", 0) >= 3:
		lines.append("You love a collapse narrative. Therapy would be cheaper.")

	# Keep it tight
	return lines[:6]
