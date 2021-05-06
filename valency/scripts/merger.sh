#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
merges czech and english conllu files into one parallel file
the languages are distinguished by zones
the original files must have the same number of sentences
not included into total.sh for this moment
# '

name=$1
python3 merger.py \
	cs \
	../data/cs/cs_"$name".conllu \
	en \
	../data/en/en_"$name".conllu \
	../data/cs_en_merged/cs_en_"$name"_merged.conllu
