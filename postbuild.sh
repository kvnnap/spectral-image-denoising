#!/bin/bash

# Generates version.py

git rev-parse --verify HEAD | xargs printf "git_commit='%s'\n" >  version.py
git log -1 --format=%ci | xargs printf "git_date='%s %s %s'\n" >> version.py
git diff --quiet
printf "git_dirty=%d\n" $? >> version.py
