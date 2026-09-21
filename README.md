# CLI lab

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
```

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
│   └── substitutor.py      # $var-подстановка и разбиение на argv
└── commands/               # commands implementations
    ├── __init__.py         # COMMANDS registry, lookup
    ├── command.py
    ├── cat.py
    └── echo.py
```