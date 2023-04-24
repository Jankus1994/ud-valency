#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

cd ..
bash frame_extraction.sh $1 $2 "test" $3
cd devel_scripts

gold_name="../../data/gold_results/""$2"".txt"
auto_name="../../data/test_results/""$2"".txt"

python3 mono_tester.py "$gold_name" "$auto_name"

