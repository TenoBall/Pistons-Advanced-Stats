import os
os.environ["MPLBACKEND"] = "Agg"

import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch
import numpy as np

BASE = r"c:\Users\JTeno\Desktop\Sports Analytics\NBA"
OUTPUT = os.path.join(BASE, "playoff_lineups_low_3pa.png")

SEASON_PAIRS = [
    ("2021-2022 - shooting freq.csv", "2022 playoffs - four factors.csv", "2021-22"),
    ("2022-2023 - shooting freq.csv", "2023 playoffs - four factors.csv", "2022-23"),
    ("2023-2024 - shooting freq.csv", "2024 Playoffs - four factors.csv", "2023-24"),
    ("2024-2025 - shooting freq.csv", "2025 Playoffs - four factors.csv", "2024-25"),
]

TARGET_LINEUPS = [
    ("2021-22", "MIA", ["Gabe Vincent", "Max Strus", "Jimmy Butler", "PJ Tucker", "Bam Adebayo"]),
    ("2021-22", "MIA", ["Kyle Lowry", "Max Strus", "Jimmy Butler", "PJ Tucker", "Bam Adebayo"]),
    ("2022-23", "MIA", ["Gabe Vincent", "Max Strus", "Jimmy Butler", "Kevin Love", "Bam Adebayo"]),
    ("2022-23", "MIA", ["Gabe Vincent", "Max Strus", "Caleb Martin", "Jimmy Butler", "Bam Adebayo"]),
    ("2022-23", "MIA", ["Kyle Lowry", "Duncan Robinson", "Caleb Martin", "Jimmy Butler", "Bam Adebayo"]),
    ("2022-23", "MIA", ["Kyle Lowry", "Max Strus", "Caleb Martin", "Jimmy Butler", "Bam Adebayo"]),
    ("2022-23", "CLE", ["Darius Garland", "Donovan Mitchell", "Caris LeVert", "Evan Mobley", "Jarrett Allen"]),
    ("2023-24", "CLE", ["Darius Garland", "Donovan Mitchell", "Max Strus", "Evan Mobley", "Jarrett Allen"]),
    ("2024-25", "HOU", ["Fred VanVleet", "Amen Thompson", "Jalen Green", "Dillon Brooks", "Alperen Sengun"]),
    ("2024-25", "DET", ["Cade Cunningham", "Ausar Thompson", "Tim Hardaway Jr.", "Tobias Harris", "Jalen Duren"]),
]


def parse_pct_val(val):
    return float(val.strip().replace("%", ""))


def parse_float(val):
    val = val.strip().replace("+", "")
    return float(val)


def load_shooting_freq(filepath):
    by_team = {}
    by_name = {}
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["Player"].strip()
            team = row["Team"].strip()
            all_three = int(row["All Three"].strip().replace("%", ""))
            minutes = int(row["MIN"]) if row["MIN"].strip() else 0
            by_team[(name, team)] = all_three
            by_name.setdefault(name, []).append((team, all_three, minutes))
    return by_team, by_name


def lookup_player(name, team, by_team, by_name):
    if (name, team) in by_team:
        return by_team[(name, team)]
    if name in by_name:
        entries = sorted(by_name[name], key=lambda x: x[2], reverse=True)
        return entries[0][1]
    return None


def load_playoff_row(filepath, team, players_list):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Team"].strip() != team:
                continue
            lineup = [row[p].strip() for p in ["PG", "SG", "SF", "PF", "C"]]
            if lineup == players_list:
                return row
    return None


def get_season_files(season_label):
    for freq, playoff, label in SEASON_PAIRS:
        if label == season_label:
            return os.path.join(BASE, freq), os.path.join(BASE, playoff)
    return None, None


def build_data():
    rows = []
    for season, team, players in TARGET_LINEUPS:
        freq_path, playoff_path = get_season_files(season)
        by_team, by_name = load_shooting_freq(freq_path)
        row = load_playoff_row(playoff_path, team, players)
        if row is None:
            print(f"WARNING: Could not find lineup {team} {players} in {season}")
            continue

        low_3_players = []
        for p in players:
            pct = lookup_player(p, team, by_team, by_name)
            if pct is not None and pct < 15:
                low_3_players.append(f"{p.split()[-1]} ({pct}%)")

        rows.append({
            "season": season,
            "team": team,
            "lineup_short": " / ".join(p.split()[-1] for p in players),
            "low_3_players": low_3_players,
            "poss": int(row["Poss"]),
            "net_rating": parse_float(row["Diff"]),
            "off_pts": parse_float(row["OFFENSE: Pts/Poss"]),
            "off_efg": parse_pct_val(row["OFFENSE: eFG%"]),
            "off_tov": parse_pct_val(row["OFFENSE: TOV%"]),
            "off_orb": parse_pct_val(row["OFFENSE: ORB%"]),
            "off_ftr": parse_float(row["OFFENSE: FT Rate"]),
            "def_pts": parse_float(row["DEFENSE: Pts/Poss"]),
            "def_efg": parse_pct_val(row["DEFENSE: eFG%"]),
            "def_tov": parse_pct_val(row["DEFENSE: TOV%"]),
            "def_orb": parse_pct_val(row["DEFENSE: ORB%"]),
            "def_ftr": parse_float(row["DEFENSE: FT Rate"]),
            "off_efg_rank": int(row["OFFENSE: eFG% Rank"]),
            "off_tov_rank": int(row["OFFENSE: TOV% Rank"]),
            "off_orb_rank": int(row["OFFENSE: ORB% Rank"]),
            "off_ftr_rank": int(row["OFFENSE: FT Rate Rank"]),
            "def_efg_rank": int(row["DEFENSE: eFG% Rank"]),
            "def_tov_rank": int(row["DEFENSE: TOV% Rank"]),
            "def_orb_rank": int(row["DEFENSE: ORB% Rank"]),
            "def_ftr_rank": int(row["DEFENSE: FT Rate Rank"]),
            "net_rank": int(row["Diff Rank"]),
        })
    return rows


def rank_color(rank, invert=False):
    """Map rank (0-100) to color. Higher rank = better (green). invert for defensive stats where lower is better."""
    if invert:
        rank = 100 - rank
    if rank >= 75:
        return "#2d8a4e"
    elif rank >= 55:
        return "#7ab648"
    elif rank >= 45:
        return "#c4c4c4"
    elif rank >= 25:
        return "#e08a3c"
    else:
        return "#c0392b"


def rank_text_color(rank, invert=False):
    if invert:
        rank = 100 - rank
    if rank >= 75 or rank < 25:
        return "white"
    return "#1a1a1a"


def create_visual(data):
    n = len(data)
    fig_height = 3.5 + n * 0.72
    fig = plt.figure(figsize=(22, fig_height), facecolor="#0e1117")

    # Title area
    fig.text(0.5, 0.96, "Playoff Lineups with 2+ Players Below 15% Three-Point Attempt Frequency",
             ha="center", va="top", fontsize=18, fontweight="bold", color="white",
             fontfamily="sans-serif")
    fig.text(0.5, 0.935, "Four Factors Performance  |  Regular Season Shooting Freq  ->  Playoff Lineups  |  2022-2025",
             ha="center", va="top", fontsize=10, color="#8899aa", fontfamily="sans-serif")

    ax = fig.add_axes([0.02, 0.04, 0.96, 0.87])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n + 2.2)
    ax.axis("off")
    ax.set_facecolor("#0e1117")

    # Column positions and headers
    col_x = {
        "season": 0.035,
        "team": 0.075,
        "lineup": 0.21,
        "low3": 0.385,
        "poss": 0.475,
        "net": 0.52,
        "off_efg": 0.575,
        "off_tov": 0.625,
        "off_orb": 0.675,
        "off_ftr": 0.725,
        "def_efg": 0.785,
        "def_tov": 0.835,
        "def_orb": 0.885,
        "def_ftr": 0.935,
    }

    header_y = n + 1.65
    subheader_y = n + 1.15

    # Group headers
    ax.text(0.65, header_y + 0.45, "OFFENSE", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#5dade2", fontfamily="sans-serif")
    ax.text(0.86, header_y + 0.45, "DEFENSE", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#e74c3c", fontfamily="sans-serif")

    # Separator lines for offense/defense groups
    ax.plot([0.545, 0.755], [header_y + 0.15, header_y + 0.15], color="#5dade2", linewidth=1.5, alpha=0.6)
    ax.plot([0.76, 0.965], [header_y + 0.15, header_y + 0.15], color="#e74c3c", linewidth=1.5, alpha=0.6)

    headers = {
        "season": "Season",
        "team": "Team",
        "lineup": "Lineup",
        "low3": "Low 3PA Players",
        "poss": "Poss",
        "net": "Net Rtg",
        "off_efg": "eFG%",
        "off_tov": "TOV%",
        "off_orb": "ORB%",
        "off_ftr": "FT Rate",
        "def_efg": "eFG%",
        "def_tov": "TOV%",
        "def_orb": "ORB%",
        "def_ftr": "FT Rate",
    }

    for key, label in headers.items():
        ax.text(col_x[key], subheader_y, label, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="#aabbcc", fontfamily="sans-serif")

    # Horizontal line below headers
    ax.plot([0.005, 0.995], [n + 0.75, n + 0.75], color="#333d4a", linewidth=1)

    for i, d in enumerate(data):
        y = n - i - 0.25
        row_bg = "#151b23" if i % 2 == 0 else "#1a2230"
        rect = FancyBboxPatch((0.005, y - 0.35), 0.99, 0.7,
                               boxstyle="round,pad=0.01", facecolor=row_bg,
                               edgecolor="none", linewidth=0)
        ax.add_patch(rect)

        # Season
        ax.text(col_x["season"], y, d["season"], ha="center", va="center",
                fontsize=8.5, color="#8899aa", fontfamily="sans-serif")

        # Team
        ax.text(col_x["team"], y, d["team"], ha="center", va="center",
                fontsize=9.5, fontweight="bold", color="white", fontfamily="sans-serif")

        # Lineup
        ax.text(col_x["lineup"], y, d["lineup_short"], ha="center", va="center",
                fontsize=7.5, color="#ccddee", fontfamily="sans-serif")

        # Low 3PA players
        low3_text = "\n".join(d["low_3_players"])
        ax.text(col_x["low3"], y, low3_text, ha="center", va="center",
                fontsize=7, color="#f39c12", fontweight="bold", fontfamily="sans-serif")

        # Poss
        ax.text(col_x["poss"], y, str(d["poss"]), ha="center", va="center",
                fontsize=9, color="#ccddee", fontfamily="sans-serif")

        # Net Rating
        net_color = "#2ecc71" if d["net_rating"] > 0 else "#e74c3c"
        net_str = f"+{d['net_rating']:.1f}" if d["net_rating"] > 0 else f"{d['net_rating']:.1f}"
        ax.text(col_x["net"], y, net_str, ha="center", va="center",
                fontsize=9.5, fontweight="bold", color=net_color, fontfamily="sans-serif")

        # Offensive four factors with color-coded backgrounds
        off_stats = [
            ("off_efg", f"{d['off_efg']:.1f}%", d["off_efg_rank"], False),
            ("off_tov", f"{d['off_tov']:.1f}%", d["off_tov_rank"], False),
            ("off_orb", f"{d['off_orb']:.1f}%", d["off_orb_rank"], False),
            ("off_ftr", f"{d['off_ftr']:.1f}", d["off_ftr_rank"], False),
        ]

        for key, val_str, rank, inv in off_stats:
            bg = rank_color(rank, inv)
            tc = rank_text_color(rank, inv)
            cell_rect = FancyBboxPatch((col_x[key] - 0.022, y - 0.25), 0.044, 0.5,
                                        boxstyle="round,pad=0.005", facecolor=bg,
                                        edgecolor="none", alpha=0.85)
            ax.add_patch(cell_rect)
            ax.text(col_x[key], y, val_str, ha="center", va="center",
                    fontsize=8, fontweight="bold", color=tc, fontfamily="sans-serif")

        # Defensive four factors (for defense: lower eFG%, ORB%, FT Rate is better; higher TOV% is better)
        def_stats = [
            ("def_efg", f"{d['def_efg']:.1f}%", d["def_efg_rank"], False),
            ("def_tov", f"{d['def_tov']:.1f}%", d["def_tov_rank"], False),
            ("def_orb", f"{d['def_orb']:.1f}%", d["def_orb_rank"], False),
            ("def_ftr", f"{d['def_ftr']:.1f}", d["def_ftr_rank"], False),
        ]

        for key, val_str, rank, inv in def_stats:
            bg = rank_color(rank, inv)
            tc = rank_text_color(rank, inv)
            cell_rect = FancyBboxPatch((col_x[key] - 0.022, y - 0.25), 0.044, 0.5,
                                        boxstyle="round,pad=0.005", facecolor=bg,
                                        edgecolor="none", alpha=0.85)
            ax.add_patch(cell_rect)
            ax.text(col_x[key], y, val_str, ha="center", va="center",
                    fontsize=8, fontweight="bold", color=tc, fontfamily="sans-serif")

    # Legend
    legend_y = -0.15
    legend_items = [
        ("#2d8a4e", "75th+ %ile"),
        ("#7ab648", "55-74th"),
        ("#c4c4c4", "45-54th"),
        ("#e08a3c", "25-44th"),
        ("#c0392b", "Below 25th"),
    ]
    ax.text(0.55, legend_y, "Percentile Rank:", ha="right", va="center",
            fontsize=8, color="#8899aa", fontfamily="sans-serif")
    for j, (color, label) in enumerate(legend_items):
        x = 0.57 + j * 0.075
        rect = FancyBboxPatch((x - 0.008, legend_y - 0.12), 0.016, 0.24,
                               boxstyle="round,pad=0.003", facecolor=color,
                               edgecolor="none", alpha=0.85)
        ax.add_patch(rect)
        ax.text(x + 0.015, legend_y, label, ha="left", va="center",
                fontsize=7, color="#8899aa", fontfamily="sans-serif")

    fig.text(0.02, 0.01, "Data: Cleaning the Glass  |  Threshold: <15% All Three-Point Attempt Frequency",
             fontsize=7.5, color="#556677", fontfamily="sans-serif")

    plt.savefig(OUTPUT, dpi=180, bbox_inches="tight", facecolor="#0e1117", edgecolor="none")
    print(f"Saved to {OUTPUT}")
    plt.close()


if __name__ == "__main__":
    data = build_data()
    print(f"Found {len(data)} lineups to visualize")
    create_visual(data)
