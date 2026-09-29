<!-- CLAUDE.md | Markdown | created 2026-09-29 | rules for agents working on this public repository -->

# Rules for agents

This repository is public. It mirrors a private quote bank kept in a separate, local repository (see that repository's `README.md` and `AGENTS.md`).

- Change the data files (`quotes.csv`, `authors.csv`, `QUOTES.md`, `quotes.json`, `datapackage.json`) with `python3 tools/mirror.py <path to the private bank>`.
- Publish only texts by public figures. Keep out of this repository:
  - the collector's own writing
  - texts by private persons, and their names
  - note files, ingest and candidate files
  - `source_files`
  - local paths and user names
  - anything from the private repository's `sources/`, `work/` or git history
- Add the id of a private-bank entry that stays private to `PRIVATE_IDS` in `tools/mirror.py` before mirroring.
- Take quote text unchanged from the private bank.
- Before committing, read `git diff` for anything private.
