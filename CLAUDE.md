# Rules for agents

This repository is public. It mirrors a private quote bank kept in a separate, local repository. Read `README.md` first; it lists every file.

## Data

- Change the data files only with `python3 tools/mirror.py <source>`. The source is the private bank, or a corrected copy of this repository's `quotes.csv` and `authors.csv`.
- Run `python3 tools/mirror.py --check` before every commit.
- The schema is `datapackage.json`. Change a column or an allowed value there, nowhere else.
- What stays private is set at the top of `tools/mirror.py`: `PRIVATE_IDS` for single entries, `PRIVATE_AUTHORS` for names that are not public figures of note (known only from quotation aggregators, blogs or social media).
- Take quote text unchanged from the private bank. Report text errors for the bank to fix.

## Privacy

Publish only texts by public figures. Keep out:
- the collector's own writing, name and note files
- texts by private persons, and the names of private persons (relatives, readers, bloggers), also in notes and bios
- `source_files`, local paths, user names, e-mail addresses
- anything from the private repository's `sources/`, `work/` or git history

Before committing, read `git diff` for anything private.

## Writing

For docs, bios, notes and commit messages:
- State facts: dates, works, places, sources. No reputation words ("famous", "beloved", "one of the most", "above all").
- Short sentences, plain words, no em dashes.
- No filler or AI tropes: "delve", "testament to", "not just X but Y", lists of three for rhythm, hedging.
- Describe the current state. History belongs in commit messages, not in docs or comments.
- One rule in one place. Point to it instead of repeating it.

Markdown files start with a comment line: name, type, creation date, purpose. Python files start with a docstring that ends with file name, language and creation date.

## Code

- Python 3 standard library only.
- Prefer one general rule over special cases. Add an exception only when the data needs it, and put it in the list it belongs to.

## Model choice

- Haiku: run `mirror.py` and `--check`, read diffs for listed patterns, mechanical clean-ups from a given list.
- Sonnet: code changes, doc and schema updates, applying given fixes.
- Opus: sourcing and attribution checks, deciding who is a public figure, privacy and copyright questions, audits.
