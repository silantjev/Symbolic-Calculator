#!/bin/bash
dir="$(dirname -- "$0")"
dir="$(realpath -- "$dir")"

cd "$dir"

if [[ -z "$VIRTUAL_ENV" ]]; then
    VIRTUAL_ENV="$dir"/.venv
    if [[ -d "$VIRTUAL_ENV" ]];  then
        source "$VIRTUAL_ENV/bin/activate"
    else
        echo Warning: directory $VIRTUAL_ENV not found. Install virtual environment >&2
    fi
fi

python3 symcalc.py "$@"
