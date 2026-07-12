.PHONY: test lint validate-experiments reproduce reproduce-all audit-cases audit-priors audit-effects

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

audit-cases:
	python3 scripts/audit_published_cases.py --output reports/published_case_reproduction_status.json

audit-priors:
	python3 scripts/audit_process_prior_readiness.py --output reports/process_prior_readiness.json

audit-effects:
	python3 scripts/audit_effect_composition.py --output reports/paper2_effect_composition_status.json
