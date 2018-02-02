NAME = $(notdir $(CURDIR))

PYTHON = /usr/bin/python

# Release
GPG_ID ?= EC92D395260D3194

# Git
GIT := /usr/bin/git
GIT_TAG = $(GIT) tag -au $(GPG_ID)

# Python
SETUP = setup.py
INSTALL_OPTIONS := -O2
UPLOAD_OPTIONS = --sign --identity=$(GPG_ID)

# System
RM := /bin/rm -f

build_directory = $(CURDIR)/build
distribution_directory = $(CURDIR)/dist

docker_image = vcard

.PHONY: all
all: build

.PHONY: docker
docker:
	docker build --build-arg uid=$(shell id --user) --tag $(docker_image) .

.PHONY: test
test: docker
	docker run --rm --user $$UID $(docker_image) pep8 --max-line-length=120 vcard/*.py tests/*.py setup.py version.py
	docker run --rm --user $$UID $(docker_image) ./test.sh

.PHONY: test-clean
test-clean:
	# Run after `make clean`
	test -z "$$($(GIT) clean --dry-run -dx)"

.PHONY: build
build: $(build_directory) docker doc test
	docker run --rm --user $$UID --volume $(build_directory):/build $(docker_image) python setup.py build --build-base /build

.PHONY: doc
doc: $(build_directory)/index.html

$(build_directory)/index.html: $(build_directory)
	markdown README.markdown > $@
	sed -i -e 's# href="\.# href="https://github.com/l0b0/vcard/blob/master#' $@

.PHONY: install
install:
	$(PYTHON) $(SETUP) install $(INSTALL_OPTIONS)
	for dir in /etc/bash_completion.d /usr/share/bash-completion/completions; \
	do \
		if [ -d "$$dir" ]; \
		then \
			install --mode 644 bash-completion/$(NAME) "$$dir" || exit 1; \
			break; \
		fi; \
	done

.PHONY: release
release: build $(distribution_directory) docker
	$(PYTHON) setup.py sdist upload --repository pypi $(UPLOAD_OPTIONS) && \
		$(GIT_TAG) -m 'PyPI release' v$(shell $(PYTHON) version.py)
	@echo 'Remember to `git push --tags`'

$(build_directory) $(distribution_directory):
	mkdir $@

.PHONY: clean
clean: clean-build clean-dist clean-ide

.PHONY: clean-build
clean-build: clean-build-third-party clean-build-local

.PHONY: clean-build-third-party
clean-build-third-party:
	-$(RM) -r $(build_directory)

.PHONY: clean-build-local
clean-build-local:
	-$(RM) -r $(NAME).egg-info
	-$(RM) -r vcard/__pycache__

.PHONY: clean-dist
clean-dist:
	-$(RM) -r $(distribution_directory)

.PHONY: clean-ide
clean-ide:
	-$(RM) -r .idea/copyright

include make-includes/variables.mk
