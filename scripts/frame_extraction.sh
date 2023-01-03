#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python:../../udapi-python/udapi/block/valency:$PYTHONPATH

: '
script running the most important part of the program - the valency frame extraction
uses Udapi scenario, which reads a parallel bilingual conllu file
and then runs the extraction on it
this script is run from total.sh
input:
    cs_en_merged/cs_en_"$name"_merged.conllu - bilingual conllu corpus 
    cs_en_align/cs-en_"$name".ali - word alignment file
output:
    pic/ext_"$name".pic - binary file with extracted valency dictionary
# '

name=$1
run_num=$2

data=../data
#for i in 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
#for i in 2 3 4 5 6 7 8 9 10
#for i in 2
#do
#read.Conllu bundles_per_doc=50 \
#align_file_name=$data/b_aligned/$name \
#for i in 0 1 2 3 4 5 6
#do
udapy \
    read.Conllu \
        files=$data/b_conllu/$name.conllu \
    valency.Cs_Sk_fral_tester \
        run_num=$run_num \
        align_file_name=$data/b_aligned/$name \
        output_folder=$data/ext_pic/ \
        output_name=$name #\
#            obl_ratio_limit=0.5 \
#            min_obl_inst_num=$i
#done