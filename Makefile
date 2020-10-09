MYPY_PY = frag-ispoll frag-gitpoll
PY = $(MYPY_PY) common.py

-include local.make

MYPY ?= mypy
FLAKE8 ?= flake8

all : check

check : $(MYPY_PY:%=%.mypy)
	$(FLAKE8) $(PY)

%.mypy : %
	$(MYPY) --check-untyped-defs --warn-redundant-casts --warn-return-any $<

.PHONY: %.mypy check all
