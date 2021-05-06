#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
script running the most important part of the program - the valency frame extraction
uses Udapi scenario, which reads a parallel bilingual conllu file
and then runs the extraction on it
this script is run from total.sh
# '

name=$1

udapy \
    read.Conllu \
        files=../data/cs_en_merged/cs_en_"$name"_merged.conllu \
    valency.Cs_En_frame_aligner \
        align_file_name=../data/cs_en_align/cs-en_"$name".ali \
	output_folder=../data/pic/ \
	output_name=ext_"$name".pic

