NAME = $(notdir $(CURDIR))

# Release
GPG_ID ?= 92126B54
gpg_keyring = $(build_directory)/keyring.gpg

# Git
GIT := /usr/bin/git
GIT_TAG = $(GIT) tag -au $(GPG_ID)

# Python
virtualenv_python = $(virtualenv_directory)/bin/python
python_version_major = 2
python_version_minor = 7
python_version_patch = 6
python_series = $(python_version_major).$(python_version_minor)
python_version = $(python_series).$(python_version_patch)
python_release = Python-$(python_version)
system_python = $(python_prefix)/bin/python$(python_series)

python_url = http://www.python.org/ftp/python

python_tarball = $(python_release).tgz
python_tarball_url = $(python_url)/$(python_version)/$(python_tarball)
python_tarball_path = $(build_directory)/$(python_tarball)

python_tarball_signature = $(python_release).tgz.asc
python_tarball_signature_url = $(python_url)/$(python_version)/$(python_tarball_signature)
python_tarball_signature_path = $(build_directory)/$(python_tarball_signature)

python_tarball_pgp_public_key_id = 18ADD4FF

python_path = $(build_directory)/$(python_release)
python_prefix = $(CURDIR)/$(build_directory)

virtualenv = $(build_directory)/bin/virtualenv
virtualenv_version = 1.11
virtualenv_release = virtualenv-$(virtualenv_version)
virtualenv_tarball = $(virtualenv_release).tar.gz
virtualenv_tarball_url = https://pypi.python.org/packages/source/v/virtualenv/$(virtualenv_tarball)
virtualenv_tarball_path = $(build_directory)/$(virtualenv_tarball)
virtualenv_path = $(build_directory)/$(virtualenv_release)
virtualenv_prefix = $(CURDIR)/$(build_directory)

SETUP = setup.py
INSTALL_OPTIONS := -O2
UPLOAD_OPTIONS = --sign --identity=$(GPG_ID)

# System
RM := /bin/rm -f

build_directory = build
virtualenv_directory = $(build_directory)/virtualenv

.PHONY: all
all: $(build_directory)

$(python_tarball_path):
	wget --timestamp --directory-prefix=$(build_directory) $(python_tarball_url)

$(python_tarball_signature_path):
	wget --timestamp --directory-prefix=$(build_directory) $(python_tarball_signature_url)

$(gpg_keyring):
	gpg --keyserver keys.gnupg.net --no-default-keyring --keyring $(gpg_keyring) --recv-keys $(python_tarball_pgp_public_key_id)

$(system_python): $(python_tarball_path) $(python_tarball_signature_path) $(gpg_keyring)
	gpg --no-default-keyring --keyring $(gpg_keyring) $(python_tarball_signature_path)
	tar -C $(build_directory) -zxvf $(python_tarball_path)
	cd $(python_path) && ./configure --prefix $(python_prefix)
	make -C $(python_path)
	make -C $(python_path) altinstall

$(virtualenv): $(system_python)
	wget --timestamp --directory-prefix=$(build_directory) $(virtualenv_tarball_url)
	tar -C $(build_directory) -zxvf $(virtualenv_tarball_path)
	cd $(virtualenv_path) && $(system_python) setup.py install --prefix $(virtualenv_prefix)

$(virtualenv_python): $(system_python) $(virtualenv)
	$(virtualenv) --python=$(system_python) $(virtualenv_directory)

.PHONY: test
test: $(virtualenv_python)
	. $(virtualenv_directory)/bin/activate && $(virtualenv_python) $(SETUP) test

$(build_directory): test $(virtualenv_python)
	. $(virtualenv_directory)/bin/activate && $(virtualenv_python) $(SETUP) build

.PHONY: clean
clean: distclean
	-$(RM) -r $(build_directory) isodate-*.egg $(NAME).egg-info
	-$(FIND) . -type d -name '__pycache__' -delete
	-$(FIND) . -type f -name '*.pyc' -delete

.PHONY: install
install: $(virtualenv_python)
	. $(virtualenv_directory)/bin/activate && $(virtualenv_python) $(SETUP) install $(INSTALL_OPTIONS)
	for dir in /etc/bash_completion.d /usr/share/bash-completion/completions; \
	do \
		if [ -d "$$dir" ]; \
		then \
			install --mode 644 bash-completion/$(NAME) "$$dir" || exit 1; \
			break; \
		fi; \
	done

.PHONY: register
register: $(virtualenv_python)
	. $(virtualenv_directory)/bin/activate && $(virtualenv_python) $(SETUP) register

.PHONY: distclean
distclean:
	-$(RM) -r dist

.PHONY: release
release: $(build_directory) register $(virtualenv_python)
	. $(virtualenv_directory)/bin/activate && $(virtualenv_python) $(SETUP) sdist bdist_egg upload $(UPLOAD_OPTIONS)
	$(GIT_TAG) -m 'PyPI release' v$(shell $(virtualenv_python) version.py)
	@echo 'Remember to `git push --tags`'

include make-includes/python.mk
include make-includes/variables.mk
