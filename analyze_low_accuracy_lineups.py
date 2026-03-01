import csv
import os

BASE = r"c:\Users\JTeno\Desktop\Sports Analytics\NBA"

SEASON_PAIRS = [
    ("2021-2022 Shooting Accuracy.csv", "2022 playoffs - four factors.csv", "2021-22"),
    ("2022-2023 Shooting Accuracy.csv", "2023 playoffs - four factors.csv", "2022-23"),
    ("2023-2024 Shooting Accuracy.csv", "2024 Playoffs - four factors.csv", "2023-24"),
    ("2024-2025 Shooting Accuracy.csv", "2025 Playoffs - four factors.csv", "2024-25"),
]

THRESHOLD = 30  # "All Three" accuracy <= 30%


def parse_pct(val):
    val = val.strip().replace("%", "")
    try:
        return int(val)
    except ValueError:
        return None


def parse_diff(val):
    val = val.strip().replace("+", "")
    try:
        return float(val)
    except ValueError:
        return None


def load_shooting_accuracy(filepath):
    by_team = {}
    by_name = {}
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["Player"].strip()
            team = row["Team"].strip()
            raw = parse_pct(row["All Three"])
            all_three = raw if raw is not None else 0
            minutes = int(row["MIN"]) if row["MIN"].strip() else 0
            by_team[(name, team)] = all_three
            by_name.setdefault(name, []).append((team, all_three, minutes))
    return by_team, by_name


def load_playoff_lineups(filepath):
    lineups = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            team = row["Team"].strip()
            if team == "League Averages":
                continue
            players = []
            for pos in ["PG", "SG", "SF", "PF", "C"]:
                p = row[pos].strip()
                if p:
                    players.append(p)

            poss = row["Poss"].strip()
            diff_str = row.get("Diff", "").strip()
            diff_val = parse_diff(diff_str)

            lineups.append({
                "team": team,
                "players": players,
                "poss": poss,
                "poss_int": int(poss) if poss.isdigit() else 0,
                "diff_str": diff_str,
                "diff_val": diff_val,
            })
    return lineups


def lookup_player(name, team, by_team, by_name):
    if (name, team) in by_team:
        return by_team[(name, team)], True
    if name in by_name:
        entries = by_name[name]
        entries_sorted = sorted(entries, key=lambda x: x[2], reverse=True)
        return entries_sorted[0][1], True
    return None, False


def main():
    print("=" * 110)
    print(f"PLAYOFF LINEUPS WITH 2+ PLAYERS HAVING 'ALL THREE' ACCURACY <= {THRESHOLD}%")
    print("=" * 110)

    grand_total = 0
    grand_positive = 0
    grand_negative = 0
    grand_poss = 0
    grand_weighted_diff = 0.0
    all_hits = []

    for acc_file, playoff_file, season_label in SEASON_PAIRS:
        acc_path = os.path.join(BASE, acc_file)
        playoff_path = os.path.join(BASE, playoff_file)

        if not os.path.exists(acc_path) or not os.path.exists(playoff_path):
            print(f"\n  Skipping {season_label}: file(s) not found")
            continue

        by_team, by_name = load_shooting_accuracy(acc_path)
        lineups = load_playoff_lineups(playoff_path)

        season_hits = []
        season_unmatched = set()

        for lineup in lineups:
            low_acc_players = []
            unknown_players = []

            for player in lineup["players"]:
                pct, found = lookup_player(player, lineup["team"], by_team, by_name)
                if not found:
                    unknown_players.append(player)
                    season_unmatched.add(player)
                elif pct <= THRESHOLD:
                    low_acc_players.append((player, pct))

            if len(low_acc_players) >= 2:
                season_hits.append({
                    "team": lineup["team"],
                    "players": lineup["players"],
                    "poss": lineup["poss"],
                    "poss_int": lineup["poss_int"],
                    "diff_str": lineup["diff_str"],
                    "diff_val": lineup["diff_val"],
                    "low_acc": low_acc_players,
                    "unknown": unknown_players,
                    "season": season_label,
                })

        season_hits.sort(key=lambda x: x["poss_int"], reverse=True)

        season_positive = sum(1 for h in season_hits if h["diff_val"] is not None and h["diff_val"] > 0)
        season_negative = sum(1 for h in season_hits if h["diff_val"] is not None and h["diff_val"] < 0)
        season_neutral = sum(1 for h in season_hits if h["diff_val"] is not None and h["diff_val"] == 0)
        season_poss = sum(h["poss_int"] for h in season_hits)
        season_weighted_diff = sum(
            h["poss_int"] * h["diff_val"]
            for h in season_hits
            if h["diff_val"] is not None
        )

        print(f"\n{'-' * 110}")
        print(f"  SEASON: {season_label}")
        print(f"  Total playoff lineups analyzed: {len(lineups)}")
        print(f"  MATCHES (2+ players <= {THRESHOLD}% All Three accuracy): {len(season_hits)}")
        if season_hits:
            avg_diff = season_weighted_diff / season_poss if season_poss else 0
            print(f"  Positive net rating: {season_positive}  |  Negative: {season_negative}  |  Neutral: {season_neutral}")
            print(f"  Possession-weighted avg net rating: {avg_diff:+.1f}")
        print(f"{'-' * 110}")

        if season_hits:
            for i, res in enumerate(season_hits, 1):
                diff_display = res["diff_str"] if res["diff_str"] else "N/A"
                outcome = ""
                if res["diff_val"] is not None:
                    if res["diff_val"] > 0:
                        outcome = "  [POSITIVE]"
                    elif res["diff_val"] < 0:
                        outcome = "  [NEGATIVE]"
                    else:
                        outcome = "  [EVEN]"

                print(f"\n  {i:2d}. {res['team']:4s}  |  Poss: {res['poss']:>4s}  |  Net Rating: {diff_display}{outcome}")
                print(f"      Lineup: {' / '.join(res['players'])}")
                low_str = ", ".join(f"{p} ({pct}%)" for p, pct in res["low_acc"])
                print(f"      >>> Players <= {THRESHOLD}% All Three: {low_str}")
                if res["unknown"]:
                    print(f"      (No shooting data: {', '.join(res['unknown'])})")
        else:
            print("  (none found)")

        if season_unmatched:
            print(f"\n  Players in playoff lineups NOT found in shooting accuracy data:")
            for p in sorted(season_unmatched):
                print(f"    - {p}")

        grand_total += len(season_hits)
        grand_positive += season_positive
        grand_negative += season_negative
        grand_poss += season_poss
        grand_weighted_diff += season_weighted_diff
        all_hits.extend(season_hits)

    # ── Grand Summary ──
    print(f"\n\n{'=' * 110}")
    print(f"GRAND SUMMARY")
    print(f"{'=' * 110}")
    print(f"  Total lineups with 2+ players <= {THRESHOLD}% All Three: {grand_total}")
    print(f"  Positive net rating: {grand_positive}  ({grand_positive/grand_total*100:.1f}%)" if grand_total else "")
    print(f"  Negative net rating: {grand_negative}  ({grand_negative/grand_total*100:.1f}%)" if grand_total else "")
    if grand_poss:
        overall_avg = grand_weighted_diff / grand_poss
        print(f"  Possession-weighted avg net rating: {overall_avg:+.1f}")
        print(f"  Total possessions across all matching lineups: {grand_poss:,}")

    # ── Breakdown by count of low-accuracy players ──
    print(f"\n{'=' * 110}")
    print(f"BREAKDOWN BY NUMBER OF LOW-ACCURACY SHOOTERS IN LINEUP")
    print(f"{'=' * 110}")
    for count in [2, 3, 4, 5]:
        subset = [h for h in all_hits if len(h["low_acc"]) == count]
        if not subset:
            continue
        pos = sum(1 for h in subset if h["diff_val"] is not None and h["diff_val"] > 0)
        neg = sum(1 for h in subset if h["diff_val"] is not None and h["diff_val"] < 0)
        tot_poss = sum(h["poss_int"] for h in subset)
        w_diff = sum(h["poss_int"] * h["diff_val"] for h in subset if h["diff_val"] is not None)
        avg = w_diff / tot_poss if tot_poss else 0
        print(f"\n  Exactly {count} players <= {THRESHOLD}%:")
        print(f"    Lineups: {len(subset)}  |  Positive: {pos}  |  Negative: {neg}")
        print(f"    Poss-weighted avg net rating: {avg:+.1f}  |  Total poss: {tot_poss:,}")

    # ── Worst offenders (most low-accuracy players) ──
    worst = sorted(all_hits, key=lambda x: (-len(x["low_acc"]), x["diff_val"] or 0))
    print(f"\n{'=' * 110}")
    print(f"LINEUPS WITH MOST LOW-ACCURACY SHOOTERS (sorted by count, then net rating)")
    print(f"{'=' * 110}")
    for res in worst[:20]:
        low_str = ", ".join(f"{p} ({pct}%)" for p, pct in res["low_acc"])
        diff_display = res["diff_str"] if res["diff_str"] else "N/A"
        print(f"  {res['season']} {res['team']:4s}  |  Low shooters: {len(res['low_acc'])}  |  Net: {diff_display:>7s}  |  Poss: {res['poss']:>4s}")
        print(f"    Lineup: {' / '.join(res['players'])}")
        print(f"    {low_str}")

    # ── Team-level aggregation ──
    print(f"\n{'=' * 110}")
    print(f"TEAM-LEVEL AGGREGATION (all seasons)")
    print(f"{'=' * 110}")
    team_data = {}
    for h in all_hits:
        key = h["team"]
        if key not in team_data:
            team_data[key] = {"count": 0, "poss": 0, "weighted_diff": 0.0, "pos": 0, "neg": 0}
        team_data[key]["count"] += 1
        team_data[key]["poss"] += h["poss_int"]
        if h["diff_val"] is not None:
            team_data[key]["weighted_diff"] += h["poss_int"] * h["diff_val"]
            if h["diff_val"] > 0:
                team_data[key]["pos"] += 1
            elif h["diff_val"] < 0:
                team_data[key]["neg"] += 1

    for team in sorted(team_data, key=lambda t: team_data[t]["count"], reverse=True):
        td = team_data[team]
        avg = td["weighted_diff"] / td["poss"] if td["poss"] else 0
        print(f"  {team:4s}  |  Lineups: {td['count']:2d}  |  Poss: {td['poss']:>5,}  |  Pos: {td['pos']}  Neg: {td['neg']}  |  Wtd Avg Net: {avg:+.1f}")


if __name__ == "__main__":
    main()
