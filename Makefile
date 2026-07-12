.PHONY: test lint validate-experiments reproduce reproduce-all

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

lint:
	python3 -m compileall -q src tests scripts

validate-experiments:
	python3 scripts/validate_experiment_registry.py

reproduce:
	python3 scripts/reproduce.py --paper "$(PAPER)" --experiment "$(EXP)"

reproduce-all:
	python3 scripts/reproduce_all.py
