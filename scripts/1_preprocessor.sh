#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
script for parsing tokenized sentences into conllu
not used anymore
it is better to use independent UDPipe
see parallexctract script
# '


udapy \
    read.Sentences files=../data/cs/cs.tok.1z4 \
    udpipe.Cs \
    write.Conllu files=../data/cs/cs_1z4.conllu
#udapy read.Conllu files=../data/moj_pokus.conllu
#udapy read.Conllu files=../data/cs_en_merged/cs_en_merged.conllu
#python3 html_creator.py ../data/cs_en_merged/cs_en_1_1.pic > ../data/cs_en_1_1.html
