#!/bin/sh

# Requires rpm package
cd $(dirname $0) && \
python setup.py test && \
python setup.py $1 bdist_egg bdist_rpm bdist_wininst sdist upload clean && \
rm -fr *.pyc build dist temp vCard_module.egg-info