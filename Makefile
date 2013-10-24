# Release
GPG_ID ?= 92126B54

# Git
GIT := /usr/bin/git
GIT_TAG = $(GIT) tag -au $(GPG_ID)

# Python
PYTHON = python
SETUP = ./setup.py
INSTALL_OPTIONS := -O2
UPLOAD_OPTIONS = --sign --identity=$(GPG_ID)

# System
RM := /bin/rm -f

NAME = $(notdir $(CURDIR))

.PHONY: all
all: build

.PHONY: test
test:
	$(SETUP) test

build: test
	$(SETUP) build

.PHONY: clean
clean: distclean
	-$(RM) -r build isodate-*.egg $(NAME).egg-info
	-$(FIND) . -type d -name '__pycache__' -delete
	-$(FIND) . -type f -name '*.pyc' -delete

.PHONY: install
install:
	$(SETUP) install $(INSTALL_OPTIONS)
	for dir in /etc/bash_completion.d /usr/share/bash-completion/completions; \
	do \
		if [ -d "$$dir" ]; \
		then \
			install --mode 644 bash-completion/$(NAME) "$$dir" || exit 1; \
			break; \
		fi; \
	done

.PHONY: register
register:
	$(SETUP) register

.PHONY: distclean
distclean:
	-$(RM) -r dist

.PHONY: release
release: build register
	$(SETUP) sdist bdist_egg upload $(UPLOAD_OPTIONS)
	$(GIT_TAG) -m 'PyPI release' v$(shell $(PYTHON) version.py)
	@echo 'Remember to `git push --tags`'

include make-includes/python.mk
include make-includes/variables.mk
