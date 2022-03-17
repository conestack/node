#!/bin/sh
./$1/bin/coverage run \
    --source=src/node \
    --omit=src/node/testing/profiling.py \
    -m node.tests.__init__
./$1/bin/coverage report
./$1/bin/coverage html
