# QT Function Grapher

## Installing Dependencies
* On POSIX systems
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```
* On Windows
```postscr
python3 -m venv .venv
source .venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

# Running the program
Make sure you have sourced .venv as before first
```sh
python qt_func_grapher/gui.py
```

# Running the test
Make sure you have sourced .venv as before first
```sh
python -m pytest
```
