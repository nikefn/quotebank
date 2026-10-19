#!/usr/bin/env python3
"""Build this repository's data files from a quote bank, or check them.

The source is a directory with quotes.csv and authors.csv: the private bank,
or this repository itself. datapackage.json is the schema: only its columns
are published, and every row must fit it.

Left out:
    entries in PRIVATE_CATEGORIES, and every entry by their authors
    entries whose id is in PRIVATE_IDS
    entries by an author in PRIVATE_AUTHORS, or by an alias of one
    author rows no published entry uses

Stops without writing if a check fails: schema (required, unique, enum,
pattern, foreign keys), translation groups of one entry, kept notes naming a
left-out id, a kept field naming a PRIVATE_CATEGORIES author, local paths or
e-mail addresses.

Reads:  <source>/quotes.csv, <source>/authors.csv, datapackage.json
Writes: quotes.csv, authors.csv, quotes.json, QUOTES.md (repository root)

Usage:
    python3 tools/mirror.py <path to the private bank>
    python3 tools/mirror.py --check    rebuild from this repository in memory;
                                       fail if a check fails or a file differs

File: tools/mirror.py, Python 3, created 2026-09-29.
"""
import collections
import csv
import io
import json
import os
import re
import sys

PRIVATE_CATEGORIES = {"Own Writing"}
PRIVATE_IDS = {
    "Q0250",  # no author found
    "Q0313",  # complete copyrighted poem
    "Q0523",  # complete copyrighted song lyric
    "Q0531",  # speaker unidentified
    "Q0609",  # performer unidentified
    "Q0639",  # private person
    "Q0648",  # complete copyrighted poem
}
# Not public figures of note: names known only from quotation aggregators,
# blogs or social media, and minor self-help writers.
PRIVATE_AUTHORS = {
    "Alfred A. Montapert", "Ali Owens", "Andrea Balt", "Anthony D'Angelo",
    "Bryant McGill", "Byron Pulsifer", "Dale Partridge", "Edward Ericson",
    "George E. Miller", "Isaac Lidsky", "Ivan Nuru", "John De Paola",
    "Kamand Kojouri", "Karolyn James", "Keshavan Nair", "Lee Mildon",
    "Mary Parrish", "Matt Zotti", "Nicole Reed", "Prasad Mahes",
    "Ralph Marston", "Roger Mills", "Saim A. Cheeda",
}
LEAKS = re.compile(r"/home/|/Users/|[A-Z]:\\|[\w.+-]+@[\w-]+\.[\w.]+")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def csv_text(columns, rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, columns, lineterminator="\n",
                            extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def schema(package, name):
    resource = next(r for r in package["resources"] if r["name"] == name)
    return resource["schema"]["fields"]


def select(quotes, authors):
    """Published entries and author rows, and the ids left out."""
    own = {q["author"] for q in quotes
           if q["category"] in PRIVATE_CATEGORIES and q["author"]}
    hidden = own | PRIVATE_AUTHORS | {
        a["name"] for a in authors if a["alias_of"] in PRIVATE_AUTHORS}
    kept = [q for q in quotes if q["id"] not in PRIVATE_IDS
            and q["author"] not in hidden
            and q["category"] not in PRIVATE_CATEGORIES]
    names = {q["author"] for q in kept}
    names |= {a["alias_of"] for a in authors if a["name"] in names}
    people = [a for a in authors if a["name"] in names]
    left_out = {q["id"] for q in quotes} - {q["id"] for q in kept}
    return kept, people, left_out, own


def check_rows(fields, rows, label):
    errors = []
    for f in fields:
        c = f.get("constraints", {})
        values = [r.get(f["name"], "") for r in rows]
        for r, v in zip(rows, values):
            key = r.get("id") or r.get("name")
            if c.get("required") and not v:
                errors.append(f"{label} {key}: {f['name']} is empty")
            if v and "enum" in c and v not in c["enum"]:
                errors.append(f"{label} {key}: {f['name']} '{v}' not allowed")
            if v and "pattern" in c and not re.fullmatch(c["pattern"], v):
                errors.append(f"{label} {key}: {f['name']} '{v}' bad form")
        if c.get("unique"):
            for v, n in collections.Counter(values).items():
                if n > 1:
                    errors.append(f"{label}: {f['name']} '{v}' {n} times")
    return errors


def check(kept, people, left_out, own, package):
    errors = check_rows(schema(package, "quotes"), kept, "quotes")
    errors += check_rows(schema(package, "authors"), people, "authors")
    names = {a["name"] for a in people}
    bios = {a["name"] for a in people if a["status"] == "bio"}
    errors += [f"quotes {q['id']}: author '{q['author']}' has no row"
               for q in kept if q["author"] and q["author"] not in names]
    errors += [f"authors {a['name']}: alias_of '{a['alias_of']}' is no bio"
               for a in people if a["alias_of"] and a["alias_of"] not in bios]
    groups = collections.Counter(q["translation_group"] for q in kept)
    errors += [f"{g} has one entry" for g, n in groups.items() if g and n < 2]
    for q in kept:
        errors += [f"quotes {q['id']}: notes name left-out {i}"
                   for i in left_out if i in q["notes"]]
    for row in kept + people:
        text = " ".join(row.values())
        key = row.get("id") or row["name"]
        errors += [f"{key}: mentions {n}" for n in own if n in text]
        errors += [f"{key}: local path or e-mail '{m.group()}'"
                   for m in LEAKS.finditer(text)]
    return errors


def counts(rows, key):
    return ", ".join(f"{v} {n}" for v, n in
                     collections.Counter(r[key] for r in rows).most_common())


def entry_md(q):
    out = ["> " + "  \n> ".join(q["quote"].split(" / ")), ">"]
    if q["transliteration"]:
        lines = q["transliteration"].split(" / ")
        out += ["> " + "  \n> ".join(f"*{t}*" for t in lines), ">"]
    by = f"> -- {q['author'] or 'Unknown'}"
    if q["source_work"]:
        by += f", *{q['source_work']}*"
    by += f"  `{q['id']}`"
    if q["language"] != "en":
        by += f"  `{q['language']}`"
    if q["attribution"] not in ("verified", "original"):
        by += f"  `{q['attribution']}`"
    return "\n".join(out + [by])


def ordered(entries):
    """By id, each original right after the first translation of its group."""
    originals = collections.defaultdict(list)
    for q in entries:
        if q["attribution"] == "original" and q["translation_group"]:
            originals[q["translation_group"]].append(q)
    out, done = [], set()
    for q in entries:
        if q["id"] in done:
            continue
        if q in originals.get(q["translation_group"], []):
            continue
        out.append(q)
        done.add(q["id"])
        for o in originals.pop(q["translation_group"], []):
            out.append(o)
            done.add(o["id"])
    out += [o for group in originals.values() for o in group]
    return out


def quotes_md(kept, created):
    parts = [
        f"<!-- QUOTES.md | Markdown | created {created} | "
        "generated from quotes.csv by tools/mirror.py -->",
        "# Quote bank",
        f"{len(kept)} entries, generated from `quotes.csv` by "
        "`tools/mirror.py`.",
        f"**By type:** {counts(kept, 'entry_type')}",
        f"**By language:** {counts(kept, 'language')}",
        f"**By sourcing:** {counts(kept, 'attribution')}",
    ]
    for category in sorted({q["category"] for q in kept}):
        parts.append(f"## {category}")
        parts += [entry_md(q) for q in
                  ordered([q for q in kept if q["category"] == category])]
    return "\n\n".join(parts) + "\n"


def build(source):
    package = json.load(open(os.path.join(ROOT, "datapackage.json"),
                             encoding="utf-8"))
    quotes = sorted(read_csv(os.path.join(source, "quotes.csv")),
                    key=lambda q: q["id"])
    authors = sorted(read_csv(os.path.join(source, "authors.csv")),
                     key=lambda a: a["name"].casefold())
    kept, people, left_out, own = select(quotes, authors)
    errors = check(kept, people, left_out, own, package)
    if errors:
        sys.exit("\n".join(errors))

    quote_cols = [f["name"] for f in schema(package, "quotes")]
    author_cols = [f["name"] for f in schema(package, "authors")]
    entries = [{c: (q[c].split(";") if c == "tags" and q[c] else
                    [] if c == "tags" else q[c]) for c in quote_cols}
               for q in kept]
    files = {
        "quotes.csv": csv_text(quote_cols, kept),
        "authors.csv": csv_text(author_cols, people),
        "quotes.json": json.dumps({"count": len(entries), "entries": entries},
                                  ensure_ascii=False, indent=2) + "\n",
        "QUOTES.md": quotes_md(kept, package["created"][:10]),
    }
    return files, f"{len(kept)} entries, {len(people)} author rows"


def main(args):
    if args == ["--check"]:
        files, summary = build(ROOT)
        stale = [n for n, text in files.items()
                 if open(os.path.join(ROOT, n), encoding="utf-8").read() != text]
        if stale:
            sys.exit("Differs from a rebuild: " + ", ".join(stale))
        print(f"OK: {summary}")
    elif len(args) == 1:
        files, summary = build(os.path.abspath(os.path.expanduser(args[0])))
        for name, text in files.items():
            with open(os.path.join(ROOT, name), "w", encoding="utf-8",
                      newline="") as f:
                f.write(text)
        print(f"Wrote {summary}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
