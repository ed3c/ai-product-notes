PYTHON ?= python3

.PHONY: check test compile

check:
	$(PYTHON) scripts/check_repository_contract.py
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

test: check

compile:
	$(PYTHON) scripts/compile_opportunity.py \
		examples/signals/vendor-api-blast-radius.json \
		--assets data/assets/registry.json \
		--public-portfolio config/public-portfolio.json \
		--output /tmp/vendor-api-opportunity.json
	$(PYTHON) scripts/compile_opportunity.py --check /tmp/vendor-api-opportunity.json
