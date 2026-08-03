from __future__ import annotations

import itertools
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.singaporepools.com.sg"
PAGE_URL = BASE_URL + "/en/product/Pages/4d_cpwn.aspx"
API_URL = BASE_URL + "/_layouts/15/FourD/FourDCommon.aspx/Get4DNumberCheckResultsJSON"

HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Referer": PAGE_URL,
    "X-Requested-With": "XMLHttpRequest",
}

PRIZE_NAMES = {
    "1": "First",
    "2": "Second",
    "3": "Third",
    "S": "Starter",
    "C": "Consolation",
}

ALL_NUMBERS = [f"{i:04d}" for i in range(10_000)]


def fetch_page_info(session: requests.Session | None = None) -> dict:
    """Fetch the public results page and parse it with BeautifulSoup.

    Serves as a connectivity check and returns the page title/description so
    the scraper can show what it is talking to.
    """
    sess = session or requests.Session()
    resp = sess.get(PAGE_URL, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else "(no title)"
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""
    heading = soup.find(["h1", "h2"])
    return {
        "title": title,
        "description": description,
        "heading": heading.get_text(strip=True) if heading else "",
    }


def digit_multisets() -> list[str]:
    """All 715 sorted-digit representatives, e.g. '0012' but never '0021'."""
    return ["".join(c) for c in itertools.combinations_with_replacement("0123456789", 4)]


def _chunks(seq: list[str], size: int) -> list[list[str]]:
    return [seq[i : i + size] for i in range(0, len(seq), size)]


@dataclass
class ScrapeResult:
    """Accumulates per-number results across batches."""

    # number -> {"appearances": int, "prizes": [(epoch_ms, prize_code), ...]}
    numbers: dict[str, dict] = field(default_factory=dict)

    def add_api_rows(self, rows: list[dict]) -> None:
        for row in rows:
            prizes = [
                (_parse_ms_date(p["DrawDate"]), p["PrizeCode"])
                for p in row.get("Prizes") or []
            ]
            self.numbers[row["Number"]] = {
                "appearances": int(row.get("NumberOfAppearances") or 0),
                "prizes": prizes,
            }


def _parse_ms_date(raw: str) -> int:
    """'/Date(1354291200000)/' -> 1354291200000."""
    return int(raw.strip("/").removeprefix("Date(").removesuffix(")"))


def query_batch(
    session: requests.Session,
    numbers: list[str],
    check_combinations: bool,
    retries: int = 4,
) -> list[dict]:
    """POST one batch of numbers; return the parsed 'data' rows."""
    payload = {
        "numbers": numbers,
        "checkCombinations": "true" if check_combinations else "false",
        "sortTypeInteger": "1",
    }
    delay = 2.0
    for attempt in range(retries):
        try:
            resp = session.post(API_URL, headers=HEADERS, data=json.dumps(payload), timeout=60)
            resp.raise_for_status()
            inner = json.loads(resp.json()["d"])
            return inner.get("data") or []
        except (requests.RequestException, KeyError, ValueError) as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"Batch {numbers[:2]}... failed after {retries} tries: {exc}")
            time.sleep(delay)
            delay *= 2
    return []


def scrape(
    data_dir: Path,
    mode: str = "combinations",
    batch_size: int = 5,
    delay: float = 0.4,
    progress: bool = True,
) -> ScrapeResult:
    """Scrape win history for every 4-digit number 0000-9999.

    mode='combinations' sends the 715 digit-multiset representatives with
    checkCombinations=true (~143 requests). mode='all' sends every one of the
    10,000 numbers explicitly with checkCombinations=false (1,000 requests) —
    slower and noisier, kept for verification.

    Progress is checkpointed to <data_dir>/checkpoint.jsonl after every batch,
    so an interrupted scrape resumes where it left off.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = data_dir / "checkpoint.jsonl"

    if mode == "combinations":
        queries, combos = digit_multisets(), True
    elif mode == "all":
        queries, combos = ALL_NUMBERS, False
    else:
        raise ValueError(f"unknown mode: {mode}")

    result = ScrapeResult()
    done_keys: set[str] = set()
    if checkpoint.exists():
        with checkpoint.open(encoding="utf-8") as fh:
            for line in fh:
                entry = json.loads(line)
                done_keys.add(entry["key"])
                result.add_api_rows(entry["rows"])
        if progress and done_keys:
            print(f"Resuming: {len(done_keys)} batches already checkpointed, "
                  f"{len(result.numbers)} numbers loaded.")

    session = requests.Session()
    try:
        info = fetch_page_info(session)
        if progress:
            print(f"Connected to: {info['title']}")
    except requests.RequestException as exc:
        raise RuntimeError(f"Cannot reach {PAGE_URL}: {exc}")

    batches = [b for b in _chunks(queries, batch_size) if "|".join(b) not in done_keys]
    total = len(batches)
    if progress and total:
        print(f"Scraping {total} batches of up to {batch_size} queries "
              f"(mode={mode}, delay={delay}s)...")

    with checkpoint.open("a", encoding="utf-8") as fh:
        for i, batch in enumerate(batches, 1):
            rows = query_batch(session, batch, check_combinations=combos)
            result.add_api_rows(rows)
            fh.write(json.dumps({"key": "|".join(batch), "rows": rows}) + "\n")
            fh.flush()
            if progress and (i % 10 == 0 or i == total):
                print(f"  batch {i}/{total} - {len(result.numbers)} numbers collected", flush=True)
            if i < total:
                time.sleep(delay)

    missing = set(ALL_NUMBERS) - set(result.numbers)
    if missing:
        print(f"WARNING: {len(missing)} numbers missing (e.g. {sorted(missing)[:5]}). "
              "Re-run scrape to fill in.")
    return result


def export_csv(result: ScrapeResult, data_dir: Path) -> tuple[Path, Path]:
    """Write wins.csv (one row per win event) and numbers.csv (all 10,000)."""
    import pandas as pd

    win_rows = [
        {"number": num, "draw_date_ms": ms, "prize_code": code,
         "prize_category": PRIZE_NAMES.get(code, code)}
        for num, info in sorted(result.numbers.items())
        for ms, code in info["prizes"]
    ]
    wins = pd.DataFrame(win_rows, columns=["number", "draw_date_ms", "prize_code", "prize_category"])
    wins["draw_date"] = pd.to_datetime(wins["draw_date_ms"], unit="ms").dt.date
    wins = wins.drop(columns=["draw_date_ms"])

    numbers = pd.DataFrame(
        [{"number": num, "appearances": info["appearances"]}
         for num, info in sorted(result.numbers.items())],
        columns=["number", "appearances"],
    )

    wins_path = data_dir / "wins.csv"
    numbers_path = data_dir / "numbers.csv"
    wins.to_csv(wins_path, index=False)
    numbers.to_csv(numbers_path, index=False)
    return wins_path, numbers_path
