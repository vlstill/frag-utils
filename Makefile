MYPY_PY = frag-ispol
PY = $(MYPY_PY) common.py

-include local.make

MYPY ?= mypy
FLAKE8 ?= flake8

check : $(MYPY_PY:%=%.mypy)
	$(FLAKE8) $(PY)

%.mypy : %
	$(MYPY) --check-untyped-defs --warn-redundant-casts --warn-return-any $<

.PHONY: %.mypy
