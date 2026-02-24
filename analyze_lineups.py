import csv
import os

BASE = r"c:\Users\JTeno\Desktop\Sports Analytics\NBA"

SEASON_PAIRS = [
    ("2021-2022 - shooting freq.csv", "2022 playoffs - four factors.csv", "2021-22"),
    ("2022-2023 - shooting freq.csv", "2023 playoffs - four factors.csv", "2022-23"),
    ("2023-2024 - shooting freq.csv", "2024 Playoffs - four factors.csv", "2023-24"),
    ("2024-2025 - shooting freq.csv", "2025 Playoffs - four factors.csv", "2024-25"),
]


def parse_pct(val):
    """Convert '10%' -> 10, '0%' -> 0, etc."""
    val = val.strip().replace("%", "")
    try:
        return int(val)
    except ValueError:
        return None


def load_shooting_freq(filepath):
    """
    Returns a dict: (player_name, team) -> all_three_pct
    Also builds a fallback dict: player_name -> list of (team, all_three_pct, minutes)
    """
    by_team = {}
    by_name = {}
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["Player"].strip()
            team = row["Team"].strip()
            all_three = parse_pct(row["All Three"])
            minutes = int(row["MIN"]) if row["MIN"].strip() else 0
            if all_three is not None:
                by_team[(name, team)] = all_three
                by_name.setdefault(name, []).append((team, all_three, minutes))
    return by_team, by_name


def load_playoff_lineups(filepath):
    """Returns list of dicts with team + player names."""
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
            diff = row.get("Diff", "").strip()
            lineups.append({
                "team": team,
                "players": players,
                "poss": poss,
                "diff": diff,
            })
    return lineups


def lookup_player(name, team, by_team, by_name):
    """
    Look up a player's All Three %. Try exact (name, team) first,
    then fall back to name-only using the entry with the most minutes.
    """
    if (name, team) in by_team:
        return by_team[(name, team)]
    if name in by_name:
        entries = by_name[name]
        entries_sorted = sorted(entries, key=lambda x: x[2], reverse=True)
        return entries_sorted[0][1]
    return None


def main():
    print("=" * 100)
    print("PLAYOFF LINEUPS WITH 2+ PLAYERS HAVING 'ALL THREE' < 10%")
    print("=" * 100)

    grand_total = 0

    for freq_file, playoff_file, season_label in SEASON_PAIRS:
        freq_path = os.path.join(BASE, freq_file)
        playoff_path = os.path.join(BASE, playoff_file)

        if not os.path.exists(freq_path) or not os.path.exists(playoff_path):
            print(f"\n  Skipping {season_label}: file(s) not found")
            continue

        by_team, by_name = load_shooting_freq(freq_path)
        lineups = load_playoff_lineups(playoff_path)

        season_results = []

        for lineup in lineups:
            low_three_players = []
            unknown_players = []
            for player in lineup["players"]:
                pct = lookup_player(player, lineup["team"], by_team, by_name)
                if pct is not None and pct < 10:
                    low_three_players.append((player, pct))
                elif pct is None:
                    unknown_players.append(player)

            if len(low_three_players) >= 2:
                season_results.append({
                    "team": lineup["team"],
                    "players": lineup["players"],
                    "poss": lineup["poss"],
                    "diff": lineup["diff"],
                    "low_three": low_three_players,
                    "unknown": unknown_players,
                })

        print(f"\n{'-' * 100}")
        print(f"  SEASON: {season_label} (Regular Season Shooting -> Playoffs)")
        print(f"  Files: {freq_file}  +  {playoff_file}")
        print(f"  Total playoff lineups analyzed: {len(lineups)}")
        print(f"  Lineups with 2+ players <10% All Three: {len(season_results)}")
        print(f"{'-' * 100}")

        if not season_results:
            print("  (none found)")
        else:
            for i, res in enumerate(season_results, 1):
                print(f"\n  {i}. {res['team']}  |  Poss: {res['poss']}  |  Diff: {res['diff']}")
                print(f"     Lineup: {' / '.join(res['players'])}")
                low_str = ", ".join(
                    f"{p} ({pct}%)" for p, pct in res["low_three"]
                )
                print(f"     Players <10% 3PA freq: {low_str}")
                if res["unknown"]:
                    print(f"     (Could not find shooting data for: {', '.join(res['unknown'])})")

        grand_total += len(season_results)

    print(f"\n{'=' * 100}")
    print(f"GRAND TOTAL across all seasons: {grand_total} lineups with 2+ players <10% All Three")
    print(f"{'=' * 100}")


if __name__ == "__main__":
    main()
