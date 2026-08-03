"""
 __  __     __     ______     __  __     ______     __    __     ______    
/\ \_\ \   /\ \   /\  ___\   /\ \_\ \   /\  __ \   /\ "-./  \   /\  __ \   
\ \  __ \  \ \ \  \ \___  \  \ \  __ \  \ \  __ \  \ \ \-./\ \  \ \ \/\ \  
 \ \_\ \_\  \ \_\  \/\_____\  \ \_\ \_\  \ \_\ \_\  \ \_\ \ \_\  \ \_____\ 
  \/_/\/_/   \/_/   \/_____/   \/_/\/_/   \/_/\/_/   \/_/  \/_/   \/_____/ 
                                                                           
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from fourd import analysis, scraper, visualize

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"


def cmd_scrape(args) -> None:
    result = scraper.scrape(
        DATA_DIR, mode=args.mode, batch_size=args.batch_size, delay=args.delay
    )
    wins_path, numbers_path = scraper.export_csv(result, DATA_DIR)
    print(f"Saved {wins_path} and {numbers_path} ({len(result.numbers):,} numbers).")


def cmd_analyse(_args) -> None:
    wins, numbers = analysis.load_data(DATA_DIR)
    print(analysis.summarise(wins, numbers))


def cmd_visualise(args) -> None:
    wins, numbers = analysis.load_data(DATA_DIR)
    paths = visualize.render_all(wins, numbers, OUTPUT_DIR, n=args.top)
    print("Charts written:")
    for p in paths:
        print(f"  {p}")


def cmd_all(args) -> None:
    if not (DATA_DIR / "wins.csv").exists() or args.force:
        cmd_scrape(args)
    else:
        print(f"Using cached data in {DATA_DIR} (use --force to re-scrape).")
    cmd_analyse(args)
    cmd_visualise(args)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Singapore Pools 4D lottery analyser")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_scrape_opts(p):
        p.add_argument("--mode", choices=["combinations", "all"], default="combinations",
                       help="combinations: 715 permutation-batched requests (default); "
                            "all: query each of the 10,000 numbers explicitly")
        p.add_argument("--batch-size", type=int, default=5,
                       help="numbers per request (default 5)")
        p.add_argument("--delay", type=float, default=0.4,
                       help="seconds between requests (default 0.4)")

    p_scrape = sub.add_parser("scrape", help="download win history for all 10,000 numbers")
    add_scrape_opts(p_scrape)
    p_scrape.set_defaults(func=cmd_scrape)

    p_analyse = sub.add_parser("analyse", help="print summary statistics")
    p_analyse.set_defaults(func=cmd_analyse)

    p_vis = sub.add_parser("visualise", help="render charts to output/")
    p_vis.add_argument("--top", type=int, default=20, help="rows in top/bottom charts")
    p_vis.set_defaults(func=cmd_visualise)

    p_all = sub.add_parser("all", help="scrape (if needed), analyse and visualise")
    add_scrape_opts(p_all)
    p_all.add_argument("--top", type=int, default=20)
    p_all.add_argument("--force", action="store_true", help="re-scrape even if cached")
    p_all.set_defaults(func=cmd_all)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted - progress is checkpointed; re-run to resume.")
        sys.exit(1)
