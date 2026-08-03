from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator

from . import analysis

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"

SEQ_BLUES = LinearSegmentedColormap.from_list(
    "seq_blues",
    ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
)


def _new_fig(title: str, subtitle: str = "", figsize=(10, 6)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    fig.suptitle(title, x=0.06, ha="left", fontsize=14, fontweight="bold", color=INK)
    if subtitle:
        ax.set_title(subtitle, loc="left", fontsize=10, color=INK_2, pad=12)
    return fig, ax


def _save(fig, out_dir: Path, name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=150, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_top_numbers(numbers: pd.DataFrame, out_dir: Path, n: int = 20) -> Path:
    top = analysis.top_numbers(numbers, n).iloc[::-1]
    fig, ax = _new_fig(
        f"Top {n} winning 4D numbers",
        "Total prize appearances (1st/2nd/3rd, Starter, Consolation) since 1986",
        figsize=(10, 8),
    )
    bars = ax.barh(top["number"], top["appearances"], color=BLUE, height=0.62)
    ax.bar_label(bars, padding=4, fontsize=8.5, color=INK_2)
    ax.set_xlabel("Prize appearances", color=INK_2, fontsize=10)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    return _save(fig, out_dir, "top_numbers.png")


def plot_bottom_numbers(numbers: pd.DataFrame, out_dir: Path, n: int = 20) -> Path:
    bottom = analysis.bottom_numbers(numbers, n).iloc[::-1]
    fig, ax = _new_fig(
        f"Bottom {n} least-winning 4D numbers",
        "Fewest prize appearances since 1986 (ties broken by number)",
        figsize=(10, 8),
    )
    bars = ax.barh(bottom["number"], bottom["appearances"], color=BLUE, height=0.62)
    ax.bar_label(bars, padding=4, fontsize=8.5, color=INK_2)
    ax.set_xlabel("Prize appearances", color=INK_2, fontsize=10)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    return _save(fig, out_dir, "bottom_numbers.png")


def plot_first_prize_leaders(wins: pd.DataFrame, out_dir: Path, n: int = 20) -> Path:
    leaders = analysis.first_prize_leaders(wins, n).iloc[::-1]
    fig, ax = _new_fig(
        f"Top {n} numbers by First Prize wins",
        "Most 1st-prize wins since 1986 (ties broken by number)",
        figsize=(10, 8),
    )
    bars = ax.barh(leaders["number"], leaders["first_prize_wins"], color=BLUE, height=0.62)
    ax.bar_label(bars, padding=4, fontsize=8.5, color=INK_2)
    ax.set_xlabel("First Prize wins", color=INK_2, fontsize=10)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    return _save(fig, out_dir, "first_prize_top.png")


def plot_digit_heatmap(wins: pd.DataFrame, out_dir: Path) -> Path:
    freq = analysis.digit_position_frequency(wins)
    fig, ax = _new_fig(
        "Digit frequency by position",
        "How often each digit 0-9 was drawn in each of the four positions",
        figsize=(8, 8),
    )
    im = ax.imshow(freq.values, cmap=SEQ_BLUES, aspect="auto")
    ax.set_xticks(range(4), [f"Position {i + 1}" for i in range(4)])
    ax.set_yticks(range(10), freq.index)
    ax.tick_params(length=0)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    vmid = (freq.values.min() + freq.values.max()) / 2
    for r in range(10):
        for c in range(4):
            val = freq.values[r, c]
            ax.text(c, r, f"{val:,}", ha="center", va="center", fontsize=8.5,
                    color="#ffffff" if val > vmid else INK)
    ax.set_ylabel("Digit", color=INK_2, fontsize=10)
    cbar = fig.colorbar(im, ax=ax, shrink=0.7)
    cbar.ax.tick_params(colors=MUTED, labelsize=8)
    cbar.outline.set_visible(False)
    return _save(fig, out_dir, "digit_position_heatmap.png")


def render_all(wins: pd.DataFrame, numbers: pd.DataFrame, out_dir: Path, n: int = 20) -> list[Path]:
    return [
        plot_top_numbers(numbers, out_dir, n),
        plot_bottom_numbers(numbers, out_dir, n),
        plot_first_prize_leaders(wins, out_dir, n),
        plot_digit_heatmap(wins, out_dir),
    ]
