.PHONY: run

PY := python3
TOKEN_FILE := TOKEN.txt

run:
	$(PY) main.py $(TOKEN_FILE)

