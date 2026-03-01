import csv
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np

BASE = r"c:\Users\JTeno\Desktop\Sports Analytics\NBA"

SEASON_PAIRS = [
    ("2021-2022 Shooting Accuracy.csv", "2022 playoffs - four factors.csv", "2021-22"),
    ("2022-2023 Shooting Accuracy.csv", "2023 playoffs - four factors.csv", "2022-23"),
    ("2023-2024 Shooting Accuracy.csv", "2024 Playoffs - four factors.csv", "2023-24"),
    ("2024-2025 Shooting Accuracy.csv", "2025 Playoffs - four factors.csv", "2024-25"),
]

THRESHOLD = 30

TEAM_COLORS = {
    "MIA": "#98002E", "LAL": "#552583", "ATL": "#E03A3E", "CLE": "#860038",
    "BKN": "#000000", "ORL": "#0077C0", "HOU": "#CE1141", "DET": "#C8102E",
    "DEN": "#0E2240", "BOS": "#007A33", "GSW": "#1D428A", "PHX": "#1D1160",
    "DAL": "#00538C", "MIL": "#00471B", "PHI": "#006BB6", "MIN": "#0C2340",
    "IND": "#002D62", "MEM": "#5D76A9", "NYK": "#F58426", "OKC": "#007AC1",
    "TOR": "#CE1141", "SAS": "#C4CED4", "SAC": "#5A2D81", "NOP": "#0C2340",
    "CHI": "#CE1141", "POR": "#E03A3E", "WAS": "#002B5C", "CHA": "#1D1160",
    "UTA": "#002B5C", "LAC": "#C8102E",
}


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
                "team": team, "players": players,
                "poss": poss, "poss_int": int(poss) if poss.isdigit() else 0,
                "diff_str": diff_str, "diff_val": diff_val,
            })
    return lineups


def lookup_player(name, team, by_team, by_name):
    if (name, team) in by_team:
        return by_team[(name, team)], True
    if name in by_name:
        entries = sorted(by_name[name], key=lambda x: x[2], reverse=True)
        return entries[0][1], True
    return None, False


def gather_data():
    all_hits = []
    for acc_file, playoff_file, season_label in SEASON_PAIRS:
        acc_path = os.path.join(BASE, acc_file)
        playoff_path = os.path.join(BASE, playoff_file)
        if not os.path.exists(acc_path) or not os.path.exists(playoff_path):
            continue
        by_team, by_name = load_shooting_accuracy(acc_path)
        lineups = load_playoff_lineups(playoff_path)
        for lineup in lineups:
            low_acc = []
            for player in lineup["players"]:
                pct, found = lookup_player(player, lineup["team"], by_team, by_name)
                if found and pct <= THRESHOLD:
                    low_acc.append((player, pct))
            if len(low_acc) >= 2:
                all_hits.append({
                    "team": lineup["team"],
                    "players": lineup["players"],
                    "poss_int": lineup["poss_int"],
                    "diff_val": lineup["diff_val"],
                    "low_acc": low_acc,
                    "season": season_label,
                })
    return all_hits


def build_bar_label(hit):
    last_names = []
    for p, pct in hit["low_acc"]:
        parts = p.split()
        last = parts[-1] if parts else p
        last_names.append(f"{last} ({pct}%)")
    return f"{hit['season']} {hit['team']}\n{', '.join(last_names)}"


def build_dot_label(hit):
    last_names = []
    for p in hit["players"]:
        parts = p.split()
        last = parts[-1] if parts else p
        last_names.append(last)
    low_names = ", ".join(
        f"{p.split()[-1]} ({pct}%)" for p, pct in hit["low_acc"]
    )
    return f"{hit['season']} {hit['team']}:  {' / '.join(last_names)}\n<=30%: {low_names}"


def main():
    hits = gather_data()
    if not hits:
        print("No matching lineups found.")
        return

    hits.sort(key=lambda x: x["diff_val"] if x["diff_val"] is not None else 0)

    fig = plt.figure(figsize=(18, 15), facecolor="#0e1117")
    gs = GridSpec(2, 1, figure=fig, hspace=0.40,
                  left=0.18, right=0.95, top=0.92, bottom=0.05,
                  height_ratios=[1, 1])

    fig.suptitle(
        f"Playoff Lineups with 2+ Players at {THRESHOLD}% or Lower  \"All Three\" Accuracy",
        fontsize=17, fontweight="bold", color="white", y=0.97,
    )

    # ── Panel 1: Net rating bar chart ──
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1d23")

    labels = [build_bar_label(h) for h in hits]
    diffs = [h["diff_val"] if h["diff_val"] is not None else 0 for h in hits]
    poss = [h["poss_int"] for h in hits]
    colors = ["#2ecc71" if d > 0 else "#e74c3c" for d in diffs]

    bars = ax1.barh(range(len(hits)), diffs, color=colors,
                    edgecolor="none", linewidth=0, height=0.7, zorder=3)
    ax1.set_yticks(range(len(hits)))
    ax1.set_yticklabels(labels, fontsize=8.5, color="white", fontfamily="monospace")
    ax1.margins(y=0.06)
    ax1.set_xlabel("Net Rating (Pts/100 Poss)", fontsize=11, color="white", labelpad=8)
    ax1.axvline(0, color="#555555", linewidth=1, zorder=2)
    ax1.set_title("Net Rating by Lineup", fontsize=13, fontweight="bold", color="white", pad=10)
    ax1.tick_params(axis="x", colors="white")
    ax1.grid(axis="x", color="#333333", linewidth=0.5, zorder=1)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["bottom"].set_color("#444444")
    ax1.spines["left"].set_color("#444444")

    for bar, d, p in zip(bars, diffs, poss):
        x_pos = bar.get_width()
        offset = 0.4 if d >= 0 else -0.4
        ha = "left" if d >= 0 else "right"
        ax1.text(x_pos + offset, bar.get_y() + bar.get_height() / 2,
                 f"{d:+.1f}  ({p} poss)", va="center", ha=ha,
                 fontsize=8, color="white", fontweight="bold")

    pos_patch = mpatches.Patch(color="#2ecc71", label="Positive Net Rating")
    neg_patch = mpatches.Patch(color="#e74c3c", label="Negative Net Rating")
    ax1.legend(handles=[pos_patch, neg_patch], loc="lower right", fontsize=9,
               facecolor="#1a1d23", edgecolor="#444444", labelcolor="white")

    # ── Panel 2: Dot plot — individual lineups (Possessions vs Net Rating) ──
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1d23")

    dot_x = [h["poss_int"] for h in hits]
    dot_y = [h["diff_val"] if h["diff_val"] is not None else 0 for h in hits]
    dot_colors = [TEAM_COLORS.get(h["team"], "#888888") for h in hits]
    dot_labels = [build_dot_label(h) for h in hits]

    ax2.scatter(dot_x, dot_y, s=180, c=dot_colors,
                edgecolors="white", linewidths=1.2, alpha=0.92, zorder=3)

    placed = []
    for i, h in enumerate(hits):
        x, y = dot_x[i], dot_y[i]
        base_offset_y = 14 if y >= 0 else -14
        va = "bottom" if y >= 0 else "top"

        attempt_offsets = [base_offset_y, -base_offset_y,
                           base_offset_y + 12, -(base_offset_y + 12)]
        chosen_oy = base_offset_y
        for oy in attempt_offsets:
            conflict = False
            for px, py, poy in placed:
                if abs(x - px) < 80 and abs((y + oy / 5.0) - (py + poy / 5.0)) < 4:
                    conflict = True
                    break
            if not conflict:
                chosen_oy = oy
                break

        va_final = "bottom" if chosen_oy > 0 else "top"
        placed.append((x, y, chosen_oy))

        ax2.annotate(
            dot_labels[i],
            (x, y),
            textcoords="offset points", xytext=(0, chosen_oy),
            ha="center", va=va_final, fontsize=7, color="white",
            fontfamily="monospace",
            arrowprops=dict(arrowstyle="-", color="#666666", lw=0.6),
            bbox=dict(boxstyle="round,pad=0.25", fc="#1a1d23", ec="#444444", lw=0.5),
        )

    ax2.axhline(0, color="#555555", linewidth=1, linestyle="--", zorder=2)
    ax2.set_xlabel("Possessions", fontsize=11, color="white", labelpad=8)
    ax2.set_ylabel("Net Rating", fontsize=11, color="white", labelpad=8)
    ax2.set_title("Possessions vs. Net Rating  (each dot = one lineup)",
                   fontsize=13, fontweight="bold", color="white", pad=10)
    ax2.tick_params(axis="both", colors="white")
    ax2.grid(color="#333333", linewidth=0.5, zorder=1)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["bottom"].set_color("#444444")
    ax2.spines["left"].set_color("#444444")

    x_pad = (max(dot_x) - min(dot_x)) * 0.10 if len(dot_x) > 1 else 30
    y_pad = (max(dot_y) - min(dot_y)) * 0.25 if len(dot_y) > 1 else 5
    ax2.set_xlim(min(dot_x) - x_pad, max(dot_x) + x_pad)
    ax2.set_ylim(min(dot_y) - y_pad, max(dot_y) + y_pad)

    total_poss = sum(h["poss_int"] for h in hits)
    wtd = sum(h["poss_int"] * (h["diff_val"] or 0) for h in hits)
    avg_net = wtd / total_poss if total_poss else 0
    n_pos = sum(1 for h in hits if h["diff_val"] is not None and h["diff_val"] > 0)
    n_neg = sum(1 for h in hits if h["diff_val"] is not None and h["diff_val"] < 0)
    summary = (f"Lineups: {len(hits)}   |   Positive: {n_pos}   Negative: {n_neg}   "
               f"|   Poss-Wtd Avg Net: {avg_net:+.1f}   |   Total Poss: {total_poss:,}")
    ax2.text(0.5, -0.10, summary, transform=ax2.transAxes,
             ha="center", va="top", fontsize=9.5, color="#aaaaaa", fontstyle="italic")

    out_path = os.path.join(BASE, "low_accuracy_lineups_visual.png")
    fig.savefig(out_path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved to: {out_path}")


if __name__ == "__main__":
    main()
