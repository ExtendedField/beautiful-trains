#!/bin/zsh

python build_db.py "$1"
python build_city.py "$1"
python analyze_city.py "$1"