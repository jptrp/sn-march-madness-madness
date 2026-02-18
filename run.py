from __future__ import annotations

import argparse
import json
import random
import shutil
import time
from pathlib import Path

from engine.bracket import build_empty_bracket, load_bracket, write_bracket
from engine.roast import select_roast_lines
from engine.persona import profile_from_seed
from engine.duel import render_duel_card
from engine.pool import render_office_summary_card, render_superlatives_card, summarize_pool
from engine.post import build_post
from engine.rank import score_shareability
from engine.score import score_bracket
from engine.share import get_headline, render_share_card
from engine.simulate import pick_winner
from engine.teams import load_teams


ROOT = Path(__file__).parent
DATA = ROOT / "data" / "teams.json"

def _bar_ascii(x: float, width: int = 9) -> str:
	n = int(round(max(0.0, min(1.0, x)) * width))
	return "#" * n + "." * (width - n)


def _write_report_md(report_path: Path, archetype: str, scores: dict[str, float], reasons: list[str]) -> None:
	lines = []
	lines.append("# SIGNAL REPORT - MARCH MADNESS MADNESS")
	lines.append("")
	lines.append(f"**Archetype:** **{archetype}**")
	lines.append("")
	for key in ["overconfidence", "chaos_addiction", "narrative_bias", "brand_bias", "collapse_risk"]:
		val = float(scores[key])
		label = key.replace("_", " ").title()
		lines.append(f"- **{label}:** `{_bar_ascii(val)}` **{val:.2f}**")
	lines.append("")
	lines.append("## Roast Lines")
	for r in reasons[:3]:
		lines.append(f"- {r}")
	lines.append("")
	lines.append("> Built by Signal. Not a prediction engine. A personality test wearing a bracket mask.")
	report_path.parent.mkdir(parents=True, exist_ok=True)
	report_path.write_text("\n".join(lines), encoding="utf-8")


def _complete_bracket(bracket, seed: int) -> None:
	"""
	Given a bracket with Round 1 games present, simulate forward and append rounds 2..6.
	"""
	rng = random.Random(seed)
	profile = profile_from_seed(seed)

	# Round 1
	r1 = [g for g in bracket.games if g.round == 1]
	for g in r1:
		w, tags = pick_winner(g.team_a, g.team_b, rng, 1, mode="bracket", profile=profile)
		g.winner = w
		g.reason_tags = tags

	winners = [g.winner for g in r1]
	assert all(winners)

	total_rounds = 6
	current_winners = winners  # type: ignore
	for rnd in range(2, total_rounds + 1):
		next_games = []
		for i in range(0, len(current_winners), 2):
			if i + 1 >= len(current_winners):
				break
			a = current_winners[i]
			b = current_winners[i + 1]
			slot = f"R{rnd}-G{(i // 2) + 1:02d}"

			from engine.types import Game  # local import to avoid circular import warnings

			game = Game(slot=slot, round=rnd, team_a=a, team_b=b, winner=None, reason_tags=[])
			w, tags = pick_winner(a, b, rng, rnd, mode="bracket", profile=profile)
			game.winner = w
			game.reason_tags = tags
			next_games.append(game)

		bracket.games.extend(next_games)
		current_winners = [g.winner for g in next_games]  # type: ignore
		if len(current_winners) <= 1:
			break


def build_sharepack(out_dir: Path, results_sorted: list[dict], summary: dict, duel_text: str) -> Path:
	sharepack = out_dir / "sharepack"
	top3_dir = sharepack / "top3"

	if sharepack.exists():
		shutil.rmtree(sharepack)

	top3_dir.mkdir(parents=True, exist_ok=True)

	(sharepack / "pool_card.txt").write_text(render_office_summary_card(summary), encoding="utf-8")
	(sharepack / "superlatives_card.txt").write_text(render_superlatives_card(summary), encoding="utf-8")
	(sharepack / "duel_card.txt").write_text(duel_text, encoding="utf-8")

	(sharepack / "leaderboard.json").write_text(json.dumps(results_sorted, indent=2), encoding="utf-8")

	top3 = summary["top3"]
	for i, r in enumerate(top3, start=1):
		seed = r["seed"]
		src = out_dir / f"share_card_{seed}.txt"
		dst = top3_dir / f"{i}_share_card_seed_{seed}.txt"
		if src.exists():
			shutil.copyfile(src, dst)
		else:
			dst.write_text(f"(missing source card for seed {seed})", encoding="utf-8")

	readme = []
	readme.append("SIGNAL MADNESS - SHARE PACK")
	readme.append("")
	readme.append("Files:")
	readme.append("- pool_card.txt")
	readme.append("- superlatives_card.txt")
	readme.append("- duel_card.txt")
	readme.append("- leaderboard.json")
	readme.append("- top3/ (top 3 share cards)")
	readme.append("")
	readme.append("Tip: paste pool_card.txt + superlatives_card.txt in Slack.")
	(sharepack / "README.txt").write_text("\n".join(readme), encoding="utf-8")

	return sharepack


def pool_archetype(scores: dict[str, float], t: dict[str, float]) -> str:
	oc = float(scores.get("overconfidence", 0.0))
	chaos = float(scores.get("chaos_addiction", 0.0))
	brand = float(scores.get("brand_bias", 0.0))
	narr = float(scores.get("narrative_bias", 0.0))
	collapse = float(scores.get("collapse_risk", 0.0))

	# Standout archetypes relative to pool
	if chaos >= t["chaos_p75"]:
		return "Chaos Goblin"
	if narr >= t["narr_p75"]:
		return "Narrative Romantic"
	if brand >= t["brand_p75"]:
		return "Brand Worshipper"

	# Paradox archetype: high OC + low chaos (relative)
	if oc >= t["oc_p75"] and chaos <= t["chaos_p25"]:
		return "Spreadsheet Liar"

	# Stability archetype: low collapse (relative)
	if collapse <= t["collapse_p25"]:
		return "Quiet Assassin"

	return "Social Copycat"


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Signal March Madness Madness - bracket personality test.")
	p.add_argument("--seed", type=str, default="42", help="Seed for bracket generation (integer or 'random').")
	p.add_argument("--sims", type=int, default=400, help="Monte Carlo sims for collapse risk.")
	p.add_argument(
		"--roast",
		type=str,
		default="normal",
		choices=["friendly", "normal", "unhinged"],
		help="Roast intensity.",
	)
	p.add_argument("--pool", type=int, default=0, help="Office Pool Mode: generate N brackets and summarize.")
	p.add_argument("--count", type=int, default=1, help="Generate N brackets/cards with seed sweep.")
	p.add_argument("--out", type=str, default="output", help="Output directory (default: output).")
	p.add_argument("--force", action="store_true", help="Regenerate bracket even if output/bracket.json exists.")
	p.add_argument("--load", action="store_true", help="Load existing bracket from output/bracket.json (default).")
	return p.parse_args()


def main() -> None:
	args = parse_args()
	
	# Resolve seed: support "random" or integer
	if args.seed == "random":
		resolved_seed = int(time.time() * 1000) % 1_000_000_000
		print(f"[Signal] Generated random seed: {resolved_seed}")
	else:
		try:
			resolved_seed = int(args.seed)
		except ValueError:
			raise ValueError(f"--seed must be an integer or 'random', got: {args.seed}")
	
	out_dir = ROOT / args.out
	if args.pool and args.pool > 0:
		args.count = args.pool
	teams = load_teams(DATA)
	out_dir.mkdir(parents=True, exist_ok=True)

	results = []
	print("Generated:")
	for i in range(max(1, args.count)):
		seed_i = resolved_seed + i
		bracket_path = out_dir / f"bracket_{seed_i}.json"
		report_json = out_dir / f"signal_report_{seed_i}.json"
		report_md = out_dir / f"signal_report_{seed_i}.md"
		share_card = out_dir / f"share_card_{seed_i}.txt"

		if args.force or not bracket_path.exists():
			bracket = build_empty_bracket(teams)
			_complete_bracket(bracket, seed=seed_i)
			write_bracket(bracket, bracket_path)
		else:
			try:
				bracket = load_bracket(bracket_path, teams)
			except (json.JSONDecodeError, KeyError, ValueError):
				bracket = build_empty_bracket(teams)
				_complete_bracket(bracket, seed=seed_i)
				write_bracket(bracket, bracket_path)
			else:
				rounds_present = {g.round for g in bracket.games if g.winner is not None}
				if 6 not in rounds_present:
					_complete_bracket(bracket, seed=seed_i)
					write_bracket(bracket, bracket_path)

		report = score_bracket(bracket, rng=random.Random(1337), sims=args.sims)
		roast_lines = select_roast_lines(report.reasons, args.roast)
		headline = get_headline(report.archetype, report.scores)
		rank = score_shareability(report.archetype, report.scores, headline, roast_lines)

		report_json.write_text(
			json.dumps(
				{"archetype": report.archetype, "scores": report.scores, "reasons": report.reasons},
				indent=2,
			),
			encoding="utf-8",
		)
		_write_report_md(report_md, report.archetype, report.scores, roast_lines)

		share_card.write_text(
			render_share_card(report.archetype, report.scores, roast_lines),
			encoding="utf-8",
		)

		results.append(
			{
				"seed": seed_i,
				"archetype": report.archetype,
				"headline": headline,
				"shareability_score": rank["score"],
				"breakdown": rank["breakdown"],
				"scores": report.scores,
			}
		)

		print(f"- {bracket_path}")
		print(f"- {report_json}")
		print(f"- {report_md}")
		print(f"- {share_card}")

	results_sorted = sorted(results, key=lambda r: r["shareability_score"], reverse=True)

	if args.pool and args.pool > 0:
		summary = summarize_pool(results_sorted)
		t = summary["thresholds"]
		for r in results_sorted:
			r["archetype"] = pool_archetype(r["scores"], t)
			summary = summarize_pool(results_sorted)
		pool_json = out_dir / "pool_summary.json"
		pool_card = out_dir / "pool_card.txt"
		sup_path = out_dir / "superlatives_card.txt"
		duel_path = out_dir / "duel_card.txt"
		pool_text = render_office_summary_card(summary)
		sup_text = render_superlatives_card(summary)
		pool_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
		pool_card.write_text(pool_text, encoding="utf-8")
		sup_path.write_text(sup_text, encoding="utf-8")

		sup = summary["superlatives"]
		seed_left = sup["safest_but_dead"]["seed"]
		seed_right = sup["most_brand"]["seed"]

		def _find(seed: int):
			return next(r for r in results_sorted if r["seed"] == seed)

		left = _find(seed_left)
		right = _find(seed_right)
		duel_text = render_duel_card(left, right)
		duel_path.write_text(duel_text, encoding="utf-8")
		post = build_post(summary, duel_text, summary["top3"])
		post = post.replace("(POOL)", pool_text)
		post = post.replace("(SUPERLATIVES)", sup_text)
		post = post.replace("(DUEL)", duel_text)

		print("\n" + render_office_summary_card(summary))
		print("\n" + sup_text)
		print("\n" + duel_text)
		sharepack_path = build_sharepack(out_dir, results_sorted, summary, duel_text)
		post_path = sharepack_path / "POST.txt"
		post_path.write_text(post, encoding="utf-8")
		print("\n📣 POST (copy/paste)\n")
		print(post)
		print(f"- {pool_json}")
		print(f"- {pool_card}")
		print(f"- {sup_path}")
		print(f"- {duel_path}")
		print(f"- {post_path}")
		print(f"- {sharepack_path}")

	leaderboard_path = out_dir / "leaderboard.json"
	leaderboard_path.write_text(json.dumps(results_sorted, indent=2), encoding="utf-8")

	print("\nTOP 3 SHARE CARDS")
	for i, r in enumerate(results_sorted[:3], start=1):
		print(
			f"{i}) seed {r['seed']} - {r['archetype']} - {r['shareability_score']:.2f} - {r['headline']}"
		)
	print(f"- {leaderboard_path}")


if __name__ == "__main__":
	main()
