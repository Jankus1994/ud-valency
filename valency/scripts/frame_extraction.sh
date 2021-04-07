#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

#udapy read.Conllu files=../data/cs_en_pokus.conllu valency.Cs_En_frame_aligner align_file_name=../data/cs_en_pokus.cs_ali output=../data/cs_en_pokus.pic
#python3 html_creator.py ../data/cs_en_pokus.pic > ../data/cs_en_pokus.html

name=$1

udapy \
    read.Conllu \
        files=../data/cs_en_merged/cs_en_"$name"_merged.conllu \
    valency.Cs_En_frame_aligner \
        align_file_name=../data/cs_en_align/cs-en_"$name".ali \
	output_folder=../data/pic/ \
	output_name=ext_"$name".pic

#udapy read.Conllu files=../data/moj_pokus.conllu
#udapy read.Conllu files=../data/cs_en_merged/cs_en_merged.conllu
