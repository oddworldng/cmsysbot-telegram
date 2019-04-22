PROJECT = cmsysbot

VENV = venv
BIN := $(VENV)/bin

PY :=  $(BIN)/python
PIP := $(BIN)/pip
PRE-COMMIT := $(BIN)/pre-commit
PYTEST := $(BIN)/pytest

REQS := requirements.txt
REQS-DEV := requirements-dev.txt

CONFIG_FILE := config/config.json


.PHONY: run install install-dev test clean freeze

run:
	$(PY) $(PROJECT) -c $(CONFIG_FILE)


install:
	virtualenv -p python3 $(VENV)
	$(PIP) install -r $(REQS)


install-dev:
	virtualenv -p python3 $(VENV)
	$(PIP) install -r $(REQS)
	$(PIP) install -r $(REQS-DEV)
	$(PRE-COMMIT) install


test:
	$(PYTEST)


clean:
	rm -rf $(VENV)


freeze:
	$(PIP) freeze

