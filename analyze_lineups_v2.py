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
    val = val.strip().replace("%", "")
    try:
        return int(val)
    except ValueError:
        return None


def load_shooting_freq(filepath):
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
    if (name, team) in by_team:
        return by_team[(name, team)], True
    if name in by_name:
        entries = by_name[name]
        entries_sorted = sorted(entries, key=lambda x: x[2], reverse=True)
        return entries_sorted[0][1], True
    return None, False


def main():
    print("=" * 100)
    print("PLAYOFF LINEUPS WITH 2+ PLAYERS HAVING 'ALL THREE' < 15%")
    print("=" * 100)

    grand_total = 0
    all_unmatched = []

    for freq_file, playoff_file, season_label in SEASON_PAIRS:
        freq_path = os.path.join(BASE, freq_file)
        playoff_path = os.path.join(BASE, playoff_file)

        if not os.path.exists(freq_path) or not os.path.exists(playoff_path):
            print(f"\n  Skipping {season_label}: file(s) not found")
            continue

        by_team, by_name = load_shooting_freq(freq_path)
        lineups = load_playoff_lineups(playoff_path)

        season_hits = []
        season_near_misses = []
        season_unmatched = set()

        for lineup in lineups:
            low_three_players = []
            borderline_players = []
            unknown_players = []

            for player in lineup["players"]:
                pct, found = lookup_player(player, lineup["team"], by_team, by_name)
                if not found:
                    unknown_players.append(player)
                    season_unmatched.add(player)
                elif pct < 15:
                    low_three_players.append((player, pct))
                elif pct == 15:
                    borderline_players.append((player, pct))

            if len(low_three_players) >= 2:
                season_hits.append({
                    "team": lineup["team"],
                    "players": lineup["players"],
                    "poss": lineup["poss"],
                    "diff": lineup["diff"],
                    "low_three": low_three_players,
                    "borderline": borderline_players,
                    "unknown": unknown_players,
                })
            elif len(low_three_players) == 1 and (borderline_players or unknown_players):
                season_near_misses.append({
                    "team": lineup["team"],
                    "players": lineup["players"],
                    "poss": lineup["poss"],
                    "diff": lineup["diff"],
                    "low_three": low_three_players,
                    "borderline": borderline_players,
                    "unknown": unknown_players,
                })

        print(f"\n{'-' * 100}")
        print(f"  SEASON: {season_label}")
        print(f"  Total playoff lineups analyzed: {len(lineups)}")
        print(f"  MATCHES (2+ players <15%): {len(season_hits)}")
        print(f"{'-' * 100}")

        if season_hits:
            for i, res in enumerate(season_hits, 1):
                print(f"\n  {i}. {res['team']}  |  Poss: {res['poss']}  |  Net Rating: {res['diff']}")
                print(f"     Lineup: {' / '.join(res['players'])}")
                low_str = ", ".join(f"{p} ({pct}%)" for p, pct in res["low_three"])
                print(f"     >>> Players <15% All Three: {low_str}")
                if res["borderline"]:
                    bdr_str = ", ".join(f"{p} ({pct}%)" for p, pct in res["borderline"])
                    print(f"     Also at exactly 10%: {bdr_str}")
        else:
            print("  (none found)")

        if season_near_misses:
            print(f"\n  Near-misses (1 player <15% + borderline/unknown players):")
            for res in season_near_misses:
                low_str = ", ".join(f"{p} ({pct}%)" for p, pct in res["low_three"])
                extra = []
                if res["borderline"]:
                    extra.append("at 10%: " + ", ".join(f"{p}" for p, _ in res["borderline"]))
                if res["unknown"]:
                    extra.append("no data: " + ", ".join(res["unknown"]))
                print(f"    - {res['team']}: {' / '.join(res['players'])}")
                print(f"      <10%: {low_str}  |  {' | '.join(extra)}")

        if season_unmatched:
            print(f"\n  Players in playoff lineups NOT found in shooting freq data:")
            for p in sorted(season_unmatched):
                print(f"    - {p}")

        grand_total += len(season_hits)

    print(f"\n{'=' * 100}")
    print(f"GRAND TOTAL: {grand_total} playoff lineups with 2+ players <15% All Three")
    print(f"{'=' * 100}")

    # Bonus: show all players who appeared in playoffs with <10% All Three
    print(f"\n\n{'=' * 100}")
    print("ALL PLAYOFF PLAYERS WITH <15% ALL THREE (across all seasons)")
    print(f"{'=' * 100}")

    for freq_file, playoff_file, season_label in SEASON_PAIRS:
        freq_path = os.path.join(BASE, freq_file)
        playoff_path = os.path.join(BASE, playoff_file)

        if not os.path.exists(freq_path) or not os.path.exists(playoff_path):
            continue

        by_team, by_name = load_shooting_freq(freq_path)
        lineups = load_playoff_lineups(playoff_path)

        seen = set()
        low_players = []
        for lineup in lineups:
            for player in lineup["players"]:
                if player in seen:
                    continue
                seen.add(player)
                pct, found = lookup_player(player, lineup["team"], by_team, by_name)
                if found and pct < 15:
                    low_players.append((player, lineup["team"], pct))

        low_players.sort(key=lambda x: x[2])
        print(f"\n  {season_label}:")
        if low_players:
            for p, t, pct in low_players:
                print(f"    {p:30s} ({t})  -  All Three: {pct}%")
        else:
            print("    (none)")


if __name__ == "__main__":
    main()
