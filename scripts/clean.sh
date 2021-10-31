#!/bin/bash
#
# Clean development environment.

set -e

to_remove=(
    .coverage dist htmlcov py2 py3 pypy
)

for item in "${to_remove[@]}"; do
    if [ -e "$item" ]; then
        rm -r "$item"
    fi
done
