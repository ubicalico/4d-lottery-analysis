from __future__ import annotations

from pathlib import Path
import pandas as pd

PRIZE_ORDER = ["First", "Second", "Third", "Starter", "Consolation"]


def load_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load wins.csv / numbers.csv produced by the scraper.

    Numbers are read as strings so leading zeros survive ('0042' != '42').
    """
    wins = pd.read_csv(
        data_dir / "wins.csv",
        dtype={"number": str, "prize_code": str, "prize_category": str},
        parse_dates=["draw_date"],
    )
    numbers = pd.read_csv(data_dir / "numbers.csv", dtype={"number": str})
    return wins, numbers


def top_numbers(numbers: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """The n numbers with the most prize appearances."""
    return (
        numbers.sort_values(["appearances", "number"], ascending=[False, True])
        .head(n)
        .reset_index(drop=True)
    )


def bottom_numbers(numbers: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """The n numbers with the fewest prize appearances (ties broken by number)."""
    return (
        numbers.sort_values(["appearances", "number"], ascending=[True, True])
        .head(n)
        .reset_index(drop=True)
    )


def appearance_distribution(numbers: pd.DataFrame) -> pd.Series:
    """How many numbers have appeared 0 times, 1 time, 2 times, ..."""
    return numbers["appearances"].value_counts().sort_index()


def category_counts(wins: pd.DataFrame) -> pd.Series:
    """Total win events per prize category, in prize order."""
    counts = wins["prize_category"].value_counts()
    return counts.reindex(PRIZE_ORDER).fillna(0).astype(int)


def digit_position_frequency(wins: pd.DataFrame) -> pd.DataFrame:
    """10x4 table: how often each digit 0-9 was drawn in each position.

    Counted over win events, so a number that won 15 times contributes its
    digits 15 times — this measures what the machine actually drew.
    """
    freq = pd.DataFrame(
        0, index=[str(d) for d in range(10)], columns=[f"pos{i + 1}" for i in range(4)]
    )
    for pos in range(4):
        counts = wins["number"].str[pos].value_counts()
        freq[f"pos{pos + 1}"] = counts.reindex(freq.index).fillna(0).astype(int)
    return freq


def digit_overall_frequency(wins: pd.DataFrame) -> pd.Series:
    """Total times each digit 0-9 appeared anywhere in a winning number."""
    return digit_position_frequency(wins).sum(axis=1)


def wins_per_year(wins: pd.DataFrame) -> pd.Series:
    """Number of prize events recorded per calendar year.

    Every draw pays exactly 23 prizes (1st, 2nd, 3rd, 10 starters,
    10 consolations), so this effectively tracks draws held per year.
    """
    return wins.groupby(wins["draw_date"].dt.year).size()


def first_prize_leaders(wins: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Numbers that have won the 1st prize the most times."""
    firsts = wins[wins["prize_category"] == "First"]
    counts = firsts.groupby("number").size().rename("first_prize_wins")
    return (
        counts.reset_index()
        .sort_values(["first_prize_wins", "number"], ascending=[False, True])
        .head(n)
        .reset_index(drop=True)
    )


def summarise(wins: pd.DataFrame, numbers: pd.DataFrame) -> str:
    """Human-readable summary report of the dataset."""
    dist = appearance_distribution(numbers)
    top = top_numbers(numbers, 10)
    bottom = bottom_numbers(numbers, 10)
    cats = category_counts(wins)
    digits = digit_overall_frequency(wins).sort_values(ascending=False)
    firsts = first_prize_leaders(wins, 5)
    never = int((numbers["appearances"] == 0).sum())

    lines = [
        "=" * 62,
        "SINGAPORE POOLS 4D - HISTORICAL WIN ANALYSIS",
        "=" * 62,
        f"Draw dates covered : {wins['draw_date'].min().date()} to {wins['draw_date'].max().date()}",
        f"Distinct draws     : {wins['draw_date'].nunique():,}",
        f"Total prize events : {len(wins):,}",
        f"Numbers tracked    : {len(numbers):,}",
        f"Never won a prize  : {never:,} numbers",
        f"Appearances/number : mean {numbers['appearances'].mean():.2f}, "
        f"median {numbers['appearances'].median():.0f}, "
        f"min {numbers['appearances'].min()}, max {numbers['appearances'].max()}",
        "",
        "TOP 10 MOST-WINNING NUMBERS",
        *[f"  {row.number}  -  {row.appearances} prizes" for row in top.itertuples()],
        "",
        "BOTTOM 10 LEAST-WINNING NUMBERS (ties broken by number)",
        *[f"  {row.number}  -  {row.appearances} prizes" for row in bottom.itertuples()],
        "",
        "PRIZE EVENTS BY CATEGORY",
        *[f"  {name:<12} {count:>8,}" for name, count in cats.items()],
        "",
        "MOST FREQUENT 1ST-PRIZE WINNERS",
        *[f"  {row.number}  -  {row.first_prize_wins} first prizes" for row in firsts.itertuples()],
        "",
        "DIGIT FREQUENCY (all positions, most to least drawn)",
        "  " + "  ".join(f"{d}:{c:,}" for d, c in digits.items()),
        "",
        "NOTE: 4D draws are independent random events. Past frequency has no",
        "predictive power for future draws - this analysis is descriptive only.",
        "=" * 62,
    ]
    return "\n".join(lines)
