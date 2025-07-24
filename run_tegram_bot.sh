#!/bin/bash
dir="$(dirname "$0")"
cd "$dir"
python3 telegram/bot.py "$@"
