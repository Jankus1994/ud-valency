#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

#udapy read.Conllu files=../data/cs_en_pokus.conllu valency.Cs_En_frame_aligner align_file_name=../data/cs_en_pokus.cs_ali output=../data/cs_en_pokus.pic
#python3 html_creator.py ../data/cs_en_pokus.pic > ../data/cs_en_pokus.html

udapy read.Conllu files=../data/cs_en_merged/cs_en_1_1_merged.conllu valency.Cs_En_frame_aligner align_file_name=../data/cs_en_align/cs-en_1_1.ali output=../data/cs_en_merged/cs_en_1_1.pic
python3 html_creator.py ../data/cs_en_merged/cs_en_1_1.pic > ../data/cs_en_1_1.html
