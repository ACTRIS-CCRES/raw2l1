#!/usr/bin/bash

# run tests
nosetests --with-xunit --with-coverage --cover-xml --cover-branches --xunit-file=../.reports/nosetests.xml --cover-xml-file=../.reports/coverage.xml

exit 0
