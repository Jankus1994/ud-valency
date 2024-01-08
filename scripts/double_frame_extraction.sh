#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

data="../data"

input_file="$data/b_conllu/UD_pud.conllu"
output_form="txt"

udapy \
    read.Conllu \
        files="$input_file" \
    valency."Cs_En_double_frame_extractor" \
        align_file_name="$data/b_aligned/UD_pud" \
        output_form=$output_form \
        output_name="$data/text_out/cs_en_PUD" \
        config_name="config.txt" \
        log_file_name="$data/logs/log.txt"