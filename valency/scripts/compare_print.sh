#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

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

#name=$1
#name="acquis_cs_en_5k"
#name="acquis_cs_en_cent"
name="UD_pud_cent"

data=../data

udapy \
    read.Conllu \
        files=$data/b_conllu/$name.conllu \
    valency.control.Compare_printer \
    	corpus_name=$name \
        align_file_name=$data/b_aligned/$name \
	gold_file_name=$data/gold/$name \
	output_folder=$data/gold/ \
	a_lang_mark=cs \
	b_lang_mark=en

