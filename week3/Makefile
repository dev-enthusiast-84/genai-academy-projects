.DEFAULT_GOAL := help
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: help install install-mcp demo start app restart stop kill logs clean reset test recall portal booking offers open-all showcase demo-models doctor

help:
	@echo "make demo        Start all four apps (no proxy)"
	@echo "make restart     Restart the demo; keep saved state"
	@echo "make stop        Stop only processes started by these Make commands"
	@echo "make logs        Show managed demo processes"
	@echo "make doctor      Check configured model connectivity and tool support"
	@echo "make open-all    Open all four apps"
	@echo "make test        Run Python and browser-engine tests"
	@echo "make reset       Reset synthetic data and start a fresh demo"
	@echo "make clean       Remove caches; preserve saved demo data"

install:
	$(PYTHON) -m pip install -r requirements.txt

install-mcp:
	$(PYTHON) -m pip install -r requirements-mcp.txt

doctor:
	@$(PYTHON) -m withdrawal.doctor

# The launcher reads .env and cleans up its owned children.
# Model services are configured separately; no proxy is started.
demo start app:
	@$(PYTHON) -m withdrawal.manage demo

restart:
	@$(MAKE) stop
	@$(MAKE) demo

stop kill:
	@$(PYTHON) -m withdrawal.manage stop

logs:
	@$(PYTHON) -m withdrawal.manage logs

reset:
	@$(MAKE) stop
	@$(PYTHON) -m withdrawal.manage demo --reset

clean:
	@$(PYTHON) -c "import shutil; from pathlib import Path; [shutil.rmtree(p) for p in [Path('__pycache__'), Path('withdrawal/__pycache__'), Path('tests/__pycache__'), Path('.pytest_cache')] if p.exists()]"

# Live model calls are not part of this test target.
test:
	$(PYTHON) -m pytest tests -q
	node --test tests/pages.test.mjs

recall:
	@$(PYTHON) -m webbrowser http://127.0.0.1:8501
portal:
	@$(PYTHON) -m webbrowser http://127.0.0.1:8101
booking:
	@$(PYTHON) -m webbrowser http://127.0.0.1:8102
offers:
	@$(PYTHON) -m webbrowser http://127.0.0.1:8103
open-all: recall portal booking offers

showcase:
	@echo "Club Portal: consent → delete profile → inspect surviving recommendations/offers."
	@echo "Recall: investigate → review → approve → verify removal and preserved booking."

# Read model IDs only; never print credentials.
demo-models:
	@$(PYTHON) -c "from withdrawal.agent import settings; c=settings('.env'); print('Provider:',c['provider']); [print(role+': '+model) for role,model in c['models'].items()]"
