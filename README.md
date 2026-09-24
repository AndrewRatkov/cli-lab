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