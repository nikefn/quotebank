<!-- README.md | Markdown | created 2026-09-29 | what this repository holds and how to use and update it -->

# quotebank

Quotations, poems, prose passages, proverbs and lyrics by public figures, mirrored from a private quote bank. Read them in [QUOTES.md](QUOTES.md), grouped by category.

## Files

| File | Content |
| --- | --- |
| `quotes.csv` | One row per entry, sorted by id. |
| `quotes.json` | The same rows as `{"count": N, "entries": [...]}`; `tags` is a list. |
| `authors.csv` | One row per author name in `quotes.csv`: dates, places, short biography. |
| `QUOTES.md` | Reading view: categories A to Z, entries by id, each original after its translation. |
| `datapackage.json` | The schema ([Frictionless Data Package](https://datapackage.org)): every column, its meaning and its allowed values. |
| `tools/mirror.py` | Builds the four data files above from a quote bank and checks them. Holds the rules for what stays private. |
| `tools/qotd.py` | Prints the quote of the day or a random quote. |
| `CLAUDE.md` | Rules for anyone, human or agent, changing this repository. |

The data files are generated; do not edit them by hand. Ids are permanent and never reused.

## Using the data

Every file is served at `https://raw.githubusercontent.com/nikefn/quotebank/main/<file>`.

`tools/qotd.py` needs only Python 3. It gives everyone the same quote on the same (UTC) day, with the other renderings of the same passage:

    python3 tools/qotd.py                         # today's quote
    python3 tools/qotd.py --lang en --verified    # English, sourcing checked
    python3 tools/qotd.py --category stoicism --random
    python3 tools/qotd.py --json --url https://raw.githubusercontent.com/nikefn/quotebank/main/quotes.json

Filters: `--lang`, `--category`, `--type`, `--author`, `--tag`, `--verified`; `--date YYYY-MM-DD` for another day.

## Updating

On the machine that holds the private bank:

    python3 tools/mirror.py <path to the private bank>
    python3 tools/mirror.py --check
    git diff

`--check` rebuilds from this repository in memory and fails if a row breaks the schema, if private material shows, or if a file differs from the rebuild.

## Rights

The texts belong to their authors. The collection is published for personal, non-commercial use.
