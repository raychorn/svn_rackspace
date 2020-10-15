#!/bin/bash

git init
find * -size +4M -type f -print >> .gitignore
git add -A
git commit -m "first commit"
git branch -M main
git remote add origin https://raychorn:1af21f4fbdee3ecca8d88ebbfc98d0471bc1f5a7@github.com/raychorn/svn_rackspace.git
git push -u origin main
