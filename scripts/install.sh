#!/bin/bash

./scripts/clean.sh

function install {
    local interpreter=$1
    local target=$2

    if [ -x "$(which $interpreter)" ]; then
        virtualenv --clear -p $interpreter $target
        ./$target/bin/pip install wheel coverage
        ./$target/bin/pip install -e .
    else
        echo "Interpreter $interpreter not found. Skip install."
    fi
}

install python2 py2
install python3 py3
install pypy3 pypy3
