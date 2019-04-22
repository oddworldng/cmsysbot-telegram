PROJECT = cmsysbot

VENV = venv

BIN := $(VENV)/bin

PY :=  $(BIN)/python
PIP := $(BIN)pip

REQS := requirements.txt
DEV_REQS := requirements.txt

CONFIG_FILE := config/config.json


.PHONY: run, install, test

run:
	$(PY) $(MAIN) -c $(CONFIG_FILE)


install:
	virtualenv -p python3 $(VENV)
	$(PIP) install -r $(REQS)


dev-install:
	virtualenv -p python3 $(VENV)
	$(PIP) install -r $(REQS)
	$(PIP) install -r $(DEV_REQS)


clean:
	rm -rf $(VENV)


test:
	$(PY) -m pytest
