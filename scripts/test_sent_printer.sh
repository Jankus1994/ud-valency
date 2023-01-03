#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python:../../udapi-python/udapi/block/valency:$PYTHONPATH

name="acquis_cs_en_test"
data=../data

udapy \
    read.Conllu \
        files=$data/b_conllu/"$name".conllu \
    valency.Test_sent_printer \
        out_file_name=$data/test_results/"$name"_2