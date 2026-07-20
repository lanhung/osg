.PHONY: test test-env lint validate-experiments reproduce reproduce-all audit-cases audit-priors audit-effects audit-paper2-decision paper1-release paper1-jog-release

UV ?= uv

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

test-env:
	$(UV) run pytest -q

lint:
	$(UV) run ruff check .
	$(UV) run ruff format --check .
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

audit-paper2-decision:
	python3 scripts/audit_paper2_decision.py --output reports/paper2_decision_status.json

paper1-release:
	python3 scripts/build_paper1_release.py --python python3

paper1-jog-release:
	python3 scripts/build_paper1_jog_release.py --python python3
