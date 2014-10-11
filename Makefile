NAME = $(notdir $(CURDIR))

# Release
GPG_ID ?= 92126B54

# Git
GIT := /usr/bin/git
GIT_TAG = $(GIT) tag -au $(GPG_ID)

FIND = /usr/bin/find

# Python
SYSTEM_PYTHON = /usr/bin/python2
PYTHON_VERSION = 2.7.6
PIP = pip
PEP8_OPTIONS = --max-line-length=120

SETUP = setup.py
INSTALL_OPTIONS := -O2
UPLOAD_OPTIONS = --sign --identity=$(GPG_ID)

# System
RM := /bin/rm -f

ONLINE = true

build_directory = build
distribution_directory = dist

.PHONY: all
all: build

.PHONY: test-dependencies
test-dependencies: virtualenv
	if $(ONLINE); then \
		. virtualenv/bin/activate && $(PIP) install --requirement python-test-requirements.txt || exit $$?; \
	fi

.PHONY: test
test: test-dependencies
	. virtualenv/bin/activate && \
		make METHOD=git python-pep8 && \
		PYTHONPATH=vcard coverage run $(SETUP) test && \
		coverage report --include='vcard/*' --fail-under=80

.PHONY: build
build: test virtualenv doc
	mkdir -p $@
	. virtualenv/bin/activate && \
		python $(SETUP) build

.PHONY: doc
doc: index.html

index.html:
	markdown README.markdown > $@
	sed -i -e 's# href="\.# href="https://github.com/l0b0/vcard/blob/master#' $@

.PHONY: install
install: virtualenv
	$(SYSTEM_PYTHON) $(SETUP) install $(INSTALL_OPTIONS)
	for dir in /etc/bash_completion.d /usr/share/bash-completion/completions; \
	do \
		if [ -d "$$dir" ]; \
		then \
			install --mode 644 bash-completion/$(NAME) "$$dir" || exit 1; \
			break; \
		fi; \
	done

.PHONY: register
register: virtualenv
	. virtualenv/bin/activate && python $(SETUP) register

.PHONY: release
release: build register
	. virtualenv/bin/activate && \
		python $(SETUP) sdist upload $(UPLOAD_OPTIONS) && \
		$(GIT_TAG) -m 'PyPI release' v$(shell python version.py)
	@echo 'Remember to `git push --tags`'

.PHONY: clean
clean: clean-build clean-dist clean-doc clean-test

.PHONY: clean-build
clean-build: clean-build-third-party clean-build-local

.PHONY: clean-build-third-party
clean-build-third-party:
	-$(RM) -r $(build_directory) isodate-*.egg

.PHONY: clean-build-local
clean-build-local:
	-$(RM) -r $(NAME).egg-info
	-$(FIND) . -type d -name '__pycache__' -delete
	-$(FIND) . -type f -name '*.pyc' -delete

.PHONY: clean-dist
clean-dist:
	-$(RM) -r $(distribution_directory)

.PHONY: clean-doc
clean-doc:
	-$(RM) index.html

.PHONY: clean-test
clean-test:
	-$(RM) .coverage
	-$(RM) virtualenv

include make-includes/python.mk
include make-includes/variables.mk
