#!/bin/sh

python setup.py test && python setup.py $1 bdist_egg bdist_rpm bdist_wininst sdist upload clean && rm -r build dist vCard_module.egg-info *.pyc