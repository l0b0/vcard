FIND := /usr/bin/find

.PHONY: python-check
python-check:
	-pep8 $(shell $(FIND) . -type f -name '*.py')
	-pychecker $(shell $(FIND) . -type f -name '*.py')
	-pylint $(shell $(FIND) . -type f -name '*.py')
	-pyflakes $(shell $(FIND) . -type f -name '*.py')

.PHONY: variables
variables:
	@$(foreach \
		v, \
		$(sort $(.VARIABLES)), \
		$(if \
			$(filter-out \
				environment% default automatic, \
				$(origin $v)), \
			$(info $v = $($v) ($(value $v)))))                         
	@true

.PHONY: variable-%
variable-%:
	$(info $* = $($*) ($(value $*)))
	@true
