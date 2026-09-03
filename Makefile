PYTHON ?= python3
CUSTOMERS ?= 3000
ORDERS ?= 18000
SEED ?= 42

.PHONY: pipeline test dashboard clean

pipeline:
	$(PYTHON) scripts/run_pipeline.py --seed $(SEED) --customers $(CUSTOMERS) --orders $(ORDERS)

test:
	$(PYTHON) -m unittest discover -s tests -v

dashboard:
	streamlit run app/streamlit_app.py

clean:
	$(PYTHON) -c "from pathlib import Path; [p.unlink() for p in Path('data/processed').glob('*') if p.is_file()]"
