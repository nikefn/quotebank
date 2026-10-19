#!/usr/bin/env python3
"""Print a quote of the day, or a random quote, from quotes.json.

The day's quote is picked by hashing the UTC date, so every caller gets the
same entry on the same day for the same filters and data. An entry comes with
the other renderings of the same passage (original, translations).

Reads:  this repository's quotes.json, or --url (e.g. the raw GitHub file)
Writes: standard output (text, or one JSON object with --json)

Usage:
    python3 tools/qotd.py [--date YYYY-MM-DD | --random]
                          [--lang en] [--category Stoicism] [--type poem]
                          [--author Seneca] [--tag love] [--verified]
                          [--url URL] [--json]

Filters ignore case; --author matches part of a name.

Example:
    python3 tools/qotd.py --lang en --verified
    python3 tools/qotd.py --url https://raw.githubusercontent.com/nikefn/quotebank/main/quotes.json

File: tools/qotd.py, Python 3, created 2026-10-19.
"""
import argparse
import datetime
import hashlib
import json
import os
import random
import sys
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKED = {"verified", "paraphrase", "reattributed"}


def load(url):
    if url:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)["entries"]
    with open(os.path.join(HERE, "quotes.json"), encoding="utf-8") as f:
        return json.load(f)["entries"]


def same(value, wanted):
    return not wanted or value.casefold() == wanted.casefold()


def checked(e, entries):
    """Sourcing checked; an original counts if one of its renderings is."""
    if e["attribution"] == "original":
        return any(o["attribution"] in CHECKED for o in versions(e, entries))
    return e["attribution"] in CHECKED


def matches(e, a, entries):
    return (same(e["language"], a.lang) and same(e["category"], a.category)
            and same(e["entry_type"], a.type)
            and (not a.author or a.author.casefold() in e["author"].casefold())
            and (not a.tag or a.tag.casefold() in e["tags"])
            and (not a.verified or checked(e, entries)))


def pick(pool, a):
    if a.random:
        return random.choice(pool)
    digest = hashlib.sha256(a.date.isoformat().encode()).digest()
    return pool[int.from_bytes(digest[:8], "big") % len(pool)]


def versions(entry, entries):
    """The entry's original and other translations, if any."""
    group = entry["translation_group"]
    return [e for e in entries if group and e["translation_group"] == group
            and e["id"] != entry["id"]]


def show(e):
    text = e["quote"].replace(" / ", "\n")
    by = [e["author"] or "Unknown", e["source_work"]]
    if e["author"] and e["source_work"].startswith(e["author"]):
        by = [e["source_work"]]
    tag = e["id"] if e["language"] == "en" else f"{e['id']}, {e['language']}"
    return f"{text}\n -- {', '.join(filter(None, by))}  [{tag}]"


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--date", type=datetime.date.fromisoformat,
                   default=datetime.datetime.now(datetime.timezone.utc).date())
    p.add_argument("--random", action="store_true", help="ignore the date")
    p.add_argument("--lang", help="ISO 639 code, e.g. en, de, la")
    p.add_argument("--category")
    p.add_argument("--type", help="quote, prose, poem, lyric or proverb")
    p.add_argument("--author")
    p.add_argument("--tag")
    p.add_argument("--verified", action="store_true",
                   help="only entries whose sourcing was checked")
    p.add_argument("--url", help="read quotes.json from this URL")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    entries = load(a.url)
    pool = sorted((e for e in entries if matches(e, a, entries)),
                  key=lambda e: e["id"])
    if not pool:
        sys.exit("No entry matches these filters.")
    entry = pick(pool, a)
    others = versions(entry, entries)

    if a.json:
        date = None if a.random else a.date.isoformat()
        print(json.dumps({"date": date, "entry": entry,
                          "versions": others}, ensure_ascii=False, indent=2))
    else:
        print(show(entry))
        for other in others:
            print("\n" + show(other))


if __name__ == "__main__":
    main()
