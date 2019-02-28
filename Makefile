.PHONY: run

PY := python3
TOKEN_FILE := TOKEN.txt
REQS := requirements.txt


run:
	$(PY) main.py $(TOKEN_FILE)


install:
	$(PY) -m pip install -r $(REQS)
