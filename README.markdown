vCard module
============

This program can be used for strict validation and parsing of vCards.

Additional scripts:

* [`format-TEL.sh`](format-TEL.sh) - Format phone numbers according to national standards
* [`split.sh`](split.sh) - Split a multiple vCards file into individual files
* [`sort-lines.sh`](sort-lines.sh) - Sort vCard property lines according to a custom key
* [`join-lines.sh`](join-lines.sh) - Join previously split vCard lines
* [`split-lines.sh`](split-lines.sh) - Split long vCard lines

Installation / upgrade
----------------------

If your system uses Python 3 as the system Python, you'll have to install `pip2` and use that instead of `pip` below.

    sudo pip install --upgrade vcard

Examples
--------

* [`minimal.vcf`](test/minimal.vcf)
* [`maximal.vcf`](test/maximal.vcf)

Development
-----------

**Download:**

    git clone --recurse-submodules https://github.com/l0b0/vcard.git

**Virtualenv setup:**

    virtualenv --python=python2.7 /path/to/virtualenv
    . /path/to/virtualenv/bin/activate

**Test:**

Requires `setuptools` (part of `virtualenv`).

    make test
