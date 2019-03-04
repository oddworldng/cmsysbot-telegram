.PHONY: run

PY := python3
CONFIG_FILE := config/config.json
REQS := requirements.txt


run:
	$(PY) main.py -c $(CONFIG_FILE)


install:
	$(PY) -m pip install -r $(REQS)
