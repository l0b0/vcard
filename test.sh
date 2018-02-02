#!/usr/bin/env bash

set -o errexit

PYTHONPATH=vcard coverage run setup.py test
coverage report --include='vcard/*' --fail-under=80
