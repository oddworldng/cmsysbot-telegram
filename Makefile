.PHONY: run

PY := python3
CONFIG_FILE := config/config.json
REQS := requirements.txt

MAIN := cmsysbot


run:
	$(PY) $(MAIN) -c $(CONFIG_FILE)


install:
	$(PY) -m pip install -r $(REQS)
