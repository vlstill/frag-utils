PY = frag-ispol

-include local.make

MYPY ?= mypy
FLAKE8 ?= flake8

check : $(PY:%=%.mypy)
	$(FLAKE8) $(PY)

%.mypy : %
	$(MYPY) --check-untyped-defs --warn-redundant-casts --warn-return-any $<

.PHONY: %.mypy