<!-- CLAUDE.md | Markdown | created 2026-09-29 | rules for agents working on this public repository -->

# Rules for agents

This repository is public. It mirrors a private quote bank that lives in a separate, local repository (see that repository's `README.md` and `AGENTS.md`).

- Change the data files only with `python3 tools/mirror.py <path to the private bank>`. Never edit `quotes.csv`, `authors.csv`, `QUOTES.md`, `quotes.json` or `datapackage.json` by hand.
- Publish only texts by public figures. Never publish:
  - the collector's own writing
  - texts by private persons, or their names
  - note files, ingest or candidate files
  - `source_files`
  - local paths or user names
  - anything from the private repository's `sources/`, `work/` or git history
- If the private bank gains an entry that must stay private, add its id to `PRIVATE_IDS` in `tools/mirror.py` before mirroring.
- Quote text is never changed here.
- Before committing, read `git diff` for anything private.
