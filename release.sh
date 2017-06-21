#!/usr/bin/env bash

# Cut a release tag for this version and push back to repository
release_version=`python setup.py --version`
echo "$release_version "

# Release version check against git tags.
tagvalue=`git describe --abbrev=0`
echo "$tagvalue"

if [ "$release_version" = "$tagvalue" ]; then
    echo "$release_version Tag has already been released and cannot create the same one again"
    exit 1	
else    
    python setup.py  bdist_wheel upload -r pyshop
    git tag -a $release_version -m ""
    git push origin --tags
fi