from __future__ import annotations

import math
import random

from .types import Team

# Round multipliers: later rounds punish chaos more (harder to keep landing upsets)
ROUND_CHAOS_MULT = {1: 1.15, 2: 1.05, 3: 0.95, 4: 0.85, 5: 0.75, 6: 0.65}


def _clamp01(x: float) -> float:
	return max(0.0, min(1.0, x))


def _logit(p: float) -> float:
	import math

	p = _clamp01(p)
	eps = 1e-9
	p = min(1.0 - eps, max(eps, p))
	return math.log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
	import math

	return 1.0 / (1.0 + math.exp(-x))


def pick_winner(
	team_a: Team,
	team_b: Team,
	rng: random.Random,
	round_num: int,
	mode: str = "bracket",
	profile=None,
) -> tuple[Team, list[str]]:
	"""
	Returns (winner, reason_tags).
	Deterministic-ish with controlled randomness; built for "behavior", not truth.
	"""
	# Normalize seed advantage: lower seed number is better
	seed_gap = team_b.seed - team_a.seed  # positive means A is higher seed (better)
	seed_adv_a = _clamp01(0.5 + (seed_gap / 30.0))  # small tilt

	# Core latent strength
	base_a = (
		0.45 * team_a.momentum
		+ 0.20 * team_a.hype
		- 0.20 * team_a.pressure
		+ 0.15 * team_a.brand_code
		+ 0.10 * seed_adv_a
	)
	base_b = (
		0.45 * team_b.momentum
		+ 0.20 * team_b.hype
		- 0.20 * team_b.pressure
		+ 0.15 * team_b.brand_code
		+ 0.10 * (1.0 - seed_adv_a)
	)

	# Chaos noise: average of both teams, scaled by round
	chaos = (team_a.chaos + team_b.chaos) / 2.0
	chaos *= ROUND_CHAOS_MULT.get(round_num, 1.0)

	# Reality is less chaotic than bracket picking.
	# Bracket mode: people inject extra chaos/narrative.
	# Reality mode: outcomes are noisy but not coinflip chaos.
	if mode == "reality":
		chaos *= 0.55
	else:
		chaos *= 1.00

	# Logistic probability from strength difference
	diff = base_a - base_b
	p_a = 1.0 / (1.0 + math.exp(-4.2 * diff))
	# Inject chaos
	p_a = _clamp01(p_a + rng.uniform(-chaos, chaos) * 0.18)

	if mode == "bracket":
		if profile is not None:
			# Identify favorite / underdog
			favorite = team_a if team_a.seed < team_b.seed else team_b
			underdog = team_b if favorite is team_a else team_a

			# Convert p_a -> logit space for stable nudges
			z = _logit(p_a)

			# Risk tolerance pushes toward underdogs (especially early rounds)
			if round_num <= 2:
				push = (profile.risk_tolerance - 0.5) * 1.25
				if underdog is team_a:
					z += push
				else:
					z -= push

			# Contrarian pushes against favorites even in later rounds (smaller effect)
			contra = (profile.contrarian - 0.5) * 0.30
			if favorite is team_a:
				z -= contra
			else:
				z += contra

			# Narrative chasing: hype gets extra weight
			hype_gap = (team_a.hype - team_b.hype)
			z += hype_gap * (profile.narrative_chasing - 0.5) * 0.70

			# Brand loyalty: brand_code gets extra weight
			brand_gap = (team_a.brand_code - team_b.brand_code)
			z += brand_gap * (profile.brand_loyalty - 0.5) * 0.70

			p_a = _clamp01(_sigmoid(z))

		# Humans slightly over-favor underdogs early (everyone wants "a few upsets")
		if round_num == 1:
			underdog = team_a if team_a.seed > team_b.seed else team_b
			# Nudge probability toward underdog if their hype is high
			if underdog.hype > 0.70:
				if underdog is team_a:
					p_a = _clamp01(p_a + 0.04)
				else:
					p_a = _clamp01(p_a - 0.04)

	roll = rng.random()
	winner = team_a if roll < p_a else team_b

	tags: list[str] = []
	favorite = team_a if team_a.seed < team_b.seed else team_b
	underdog = team_b if favorite is team_a else team_a

	if winner is favorite:
		tags.append("favorite")
	else:
		tags.append("upset")

	# Attribute most of the pick to whichever factor dominates in winner's feature vector
	# (This is fake-but-coherent explanation generation.)
	dom = max(
		("momentum", winner.momentum),
		("hype", winner.hype),
		("brand", winner.brand_code),
		key=lambda x: x[1],
	)[0]
	tags.append(dom)

	# Pressure choke narrative
	loser = team_b if winner is team_a else team_a
	if loser.pressure > 0.75 and round_num >= 2:
		tags.append("choke")

	# Big upset tag (seed gap)
	if winner is underdog and abs(team_a.seed - team_b.seed) >= 6:
		tags.append("big_upset")

	return winner, tags
