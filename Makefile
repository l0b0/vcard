NAME = $(notdir $(CURDIR))

# Release
GPG_ID ?= 92126B54
gpg_keyring = $(download_directory)/keyring.gpg

# Git
GIT := /usr/bin/git
GIT_TAG = $(GIT) tag -au $(GPG_ID)

FIND = /usr/bin/find

# Python
PYTHON_VERSION = 2.7.6
PEP8_OPTIONS = --max-line-length=120

SETUP = setup.py
INSTALL_OPTIONS := -O2
UPLOAD_OPTIONS = --sign --identity=$(GPG_ID)

# System
RM := /bin/rm -f

build_directory = build
download_directory = download
virtualenv_directory = $(build_directory)/virtualenv

.PHONY: all
all: compile

virtualenv/bin/pep8: virtualenv
	. virtualenv/bin/activate && pip install --requirement python-test-requirements.txt

.PHONY: test
test: virtualenv/bin/pep8
	. virtualenv/bin/activate && \
		python $(SETUP) test && \
		make METHOD=git python-pep8

.PHONY: compile
compile: test virtualenv
	. virtualenv/bin/activate && \
		python $(SETUP) build

index.html:
	markdown README.markdown > $@
	sed -i -e 's# href="\.# href="https://github.com/l0b0/vcard/blob/master#' $@

.PHONY: clean
clean: distclean
	-$(RM) -r $(build_directory) isodate-*.egg $(NAME).egg-info
	-$(FIND) . -type d -name '__pycache__' -delete
	-$(FIND) . -type f -name '*.pyc' -delete

.PHONY: install
install: virtualenv
	. virtualenv/bin/activate && python $(SETUP) install $(INSTALL_OPTIONS)
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

.PHONY: distclean
distclean:
	-$(RM) -r dist

.PHONY: download-clean
	-$(RM) r $(download_directory)

.PHONY: release
release: compile register
	. virtualenv/bin/activate && python $(SETUP) sdist bdist_egg upload $(UPLOAD_OPTIONS)
	$(GIT_TAG) -m 'PyPI release' v$(shell python version.py)
	@echo 'Remember to `git push --tags`'

$(build_directory) $(download_directory):
	mkdir -p $@

include make-includes/python.mk
include make-includes/variables.mk
