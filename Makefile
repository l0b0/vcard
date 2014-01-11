# Release
GPG_ID ?= 92126B54

# Git
GIT := /usr/bin/git
GIT_TAG = $(GIT) tag -au $(GPG_ID)

# Python
virtualenv_python = $(virtualenv_directory)/bin/python
python_version_major = 2
python_version_minor = 7
system_python = python$(python_version_major).$(python_version_minor)
SETUP = ./setup.py
INSTALL_OPTIONS := -O2
UPLOAD_OPTIONS = --sign --identity=$(GPG_ID)

# System
RM := /bin/rm -f

NAME = $(notdir $(CURDIR))

build_directory = build
virtualenv_directory = $(build_directory)/virtualenv

.PHONY: all
all: $(build_directory)

$(virtualenv_directory):
	virtualenv --python=$(system_python) $(virtualenv_directory)

.PHONY: test
test: $(virtualenv_directory)
	. $(virtualenv_directory)/bin/activate && $(SETUP) test

$(build_directory): test $(virtualenv_directory)
	. $(virtualenv_directory)/bin/activate && $(SETUP) build

.PHONY: clean
clean: distclean
	-$(RM) -r $(build_directory) isodate-*.egg $(NAME).egg-info
	-$(FIND) . -type d -name '__pycache__' -delete
	-$(FIND) . -type f -name '*.pyc' -delete

.PHONY: install
install: $(virtualenv_directory)
	. $(virtualenv_directory)/bin/activate && $(SETUP) install $(INSTALL_OPTIONS)
	for dir in /etc/bash_completion.d /usr/share/bash-completion/completions; \
	do \
		if [ -d "$$dir" ]; \
		then \
			install --mode 644 bash-completion/$(NAME) "$$dir" || exit 1; \
			break; \
		fi; \
	done

.PHONY: register
register: $(virtualenv_directory)
	. $(virtualenv_directory)/bin/activate && $(SETUP) register

.PHONY: distclean
distclean:
	-$(RM) -r dist

.PHONY: release
release: $(build_directory) register $(virtualenv_directory)
	. $(virtualenv_directory)/bin/activate && $(SETUP) sdist bdist_egg upload $(UPLOAD_OPTIONS)
	$(GIT_TAG) -m 'PyPI release' v$(shell $(virtualenv_python) version.py)
	@echo 'Remember to `git push --tags`'

include make-includes/python.mk
include make-includes/variables.mk
