.PHONY: test lint reproduce

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

lint:
	python3 -m compileall -q src tests scripts

reproduce:
	python3 scripts/reproduce.py --paper "$(PAPER)" --experiment "$(EXP)"

