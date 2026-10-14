# CLI lab

## Links to flowcharts
Project scheme in `docs/`:
- `project_obsidian_scheme.excalidraw.pdf` pdf file
- `project_obsidian_scheme.excalidraw` raw file 

Also discussion, comment, schemes, etc:

`https://lucid.app/lucidchart/20ccc53d-12f5-4c8f-971a-dcc61eefd2f5/edit?invitationId=inv_52fd8ae5-e6c2-45e4-9e0b-1f9c70f42986`

## Project structure
```
src/
├── main.py                 # entrypoint
├── runtime/                # runtime context: EnvScope, FdTriple
│   ├── __init__.py
│   ├── envscope.py
│   └── fdtriple.py
├── interpreter/            # main conveyer's structure:
│   ├── __init__.py         # Parser, MasterClass, subtitutor, etc
│   ├── parser.py           
│   ├── masterclass.py      
│   └── substitutor.py
└── commands/               # commands implementations
    ├── __init__.py         # COMMANDS registry, lookup
    ├── command.py
    ├── cat.py
    └── echo.py
```

## Build requirements

Build virtual environment (after cloning):
```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Activate virtual environment (when openning):
```
source .venv/bin/activate
```

Project should satisfy `black` linter. Before commiting run `black .` in it's root.

To install `black` use
```
pip install black==24.2.0
```

Class naming: CamelCase, functions naming: snake_case.

## Run
```
:~/apps/cli-lab$ python src/main.py
>> echo hello | cat
hello
:~/apps/cli-lab$ python src/main.py
>> echo a; echo b; echo c
a
b
c
```
## grep

Specification of the `grep` library built-in.
```
grep [-i] [-w] [-A NUM] PATTERN [FILE...]
```

| Key | Meaning |
| --- | --- |
| `-i`, `--ignore-case` | case-insensitive search |
| `-w`, `--word-regexp` | match whole words only |
| `-A NUM`, `--after-context NUM` | also print `NUM` lines after each match |
| `-h`, `--help` | print usage |

`PATTERN` is a Python regular expression (`re`), so `^`, `$`, `.`, `[...]`,
`*`, `+`, `?`, `|` and groups all work. With no `FILE` the standard input is
read, which makes `grep` usable in pipelines.

Exit codes: `0` — at least one line matched, `1` — nothing
matched, `2` — a usage, pattern or I/O error.

Examples (against a file whose first line is `Минимальный синтаксис grep`):

```
:~/apps/cli-lab$ python src/main.py
>> grep "Минимальный" notes.md
Минимальный синтаксис grep

>> grep "Минимальный$" notes.md

>> grep "^Минимальный" notes.md
Минимальный синтаксис grep

>> grep -i "минимальный" notes.md
Минимальный синтаксис grep

>> grep -w "Минимал" notes.md

>> grep -A 1 "II" notes.md
часть II
строка после II

>> cat notes.md | grep -w grep | wc
1 3 47
```

## Choosing the command line argument parsing library

`grep` is the first built-in with non-trivial keys (`-i`, `-w`, `-A NUM`,
clustering such as `-iw`, the `--` terminator), so the parsing is delegated to
a library rather than hand-written. The
candidates for parsing arguments were chosen from:

| Library | Verdict |
| --- | --- |
| **`argparse`** (stdlib) | **chosen**, embeddable, most popular, dependency-free |
| `getopt` (stdlib) | low-level |
| `optparse` (stdlib) | deprecated since 3.2 |
| `click` (third-party) | designed to *own* the process |
| `typer` (third-party) | same, plus a heavier dependency |
| `docopt` (third-party) | unmaintained, no validation |



In short: `argparse` is the only candidate that is both dependency-free and
*embeddable*, which is what a shell built-in requires.
