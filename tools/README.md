# Document tools

`build_docs.py` builds the version 1.1 design documents as PDFs from Markdown:

| Source | Output |
|--------|--------|
| `SCMS Documents/source/sad_v1.1.md` | `SCMS Documents/SCMS_SAD_v1.1.pdf` |
| `SCMS Documents/source/srs_v1.1.md` | `SCMS Documents/SCMS_SRS_v1.1.pdf` |

The version 1.0 PDFs and the Test Plan are not touched by the build.

## Requirements

Python 3 and `reportlab` (pinned in `requirements-docs.txt`). These are only for the documents and are deliberately not in the application's `requirements.txt`.

```bash
py -3.12 -m pip install -r tools/requirements-docs.txt
```

## Build

Run from the repository root:

```bash
py -3.12 tools/build_docs.py            # build both PDFs
py -3.12 tools/build_docs.py --check    # parse the sources only, write nothing
```

The output is reproducible: building the same sources again gives the same PDF bytes with the same reportlab version.

## Source syntax

The sources use a small Markdown subset: `#`, `##`, `###` headings, paragraphs, `-` and `1.` lists, pipe tables, `**bold**` and `` `code` ``; inside a table cell a backslash followed by `n` is a forced line break. Directives on their own line:

- `@widths 20 30 50` sets relative column widths for the next table.
- `@cover` ... `@endcover` is the centred title block.
- `@pagebreak` starts a new page.
- `@landscape` and `@portrait` start a new page in that orientation.

Anything else (quotes, code fences, links, HTML, other bullet markers, italics) stops the build with a `file:line` message instead of being skipped. Text must be Windows-1252 because the built-in PDF fonts are used, so characters outside that set, such as arrows, are rejected (em dashes and curly quotes are accepted).

Tables repeat their header row on each page and rows are never split across pages. Every page has a "Page X of Y" footer.

## Editing the documents

Change the Markdown source, run the build, and read the generated PDF. State only what the code on `main` shows, and say whether a statement comes from code inspection or from a test run.
