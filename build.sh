#!/usr/bin/env bash
echo 'installing requirements'
pip install -r requirements.txt

echo 'setting up paths to development'
python setup.py develop

echo 'running nosetests with report generation and coverage options'

nosetests -s BIMLite --with-coverage --cover-erase --cover-inclusive --cover-package=BIMLite --cover-xml --with-xunit > nose_test.out
