#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

treebank_name=$1

data="../data/"
input_folder="$data""m_conllu/"
input_suffix=".conllu"
output_folder="$data""gold_results/"
output_suffix=".txt"

udapy \
    read.Conllu \
        files="$input_folder""$treebank_name""$input_suffix" \
    valency.Sample_printer\
        output_name="$output_folder""$treebank_name""$output_suffix"