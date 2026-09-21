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

## Run
```
:~/apps/cli-lab$ python src/main.py
>> echo hello | cat
hello
```