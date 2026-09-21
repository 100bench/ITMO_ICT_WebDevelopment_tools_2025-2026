PYTHON ?= python3
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
INSTALL_STAMP := $(VENV)/.requirements-installed

.PHONY: run install sums parsers

run: sums parsers

install: $(INSTALL_STAMP)

$(INSTALL_STAMP): requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install -r requirements.txt
	touch $(INSTALL_STAMP)

sums: install
	$(VENV_PYTHON) -m sums.threading_sum
	$(VENV_PYTHON) -m sums.multiprocessing_sum
	$(VENV_PYTHON) -m sums.async_sum

parsers: install
	$(VENV_PYTHON) -m parsers.threading_parser
	$(VENV_PYTHON) -m parsers.multiprocessing_parser
	$(VENV_PYTHON) -m parsers.async_parser
