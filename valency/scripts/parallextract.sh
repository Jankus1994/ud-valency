#!/bin/bash

export PATH=../../fast_align/build:$PATH
export PATH=../../udpipe/bin-linux64:$PATH

: '
script
# '
#python3 parallextract.py ../data/parallel/alignedCorpus_cs_en.xml ../data/ext_cs_en.cs ../data/ext_cs_en.en
#cat ../data/ext_cs_en.cs | udpipe --tokenizer='presegmented' --output=horizontal ../../udpipe/models/czech-pdt-ud-2.3-181115.udpipe > ../data/cs_tokenized
#cat ../data/ext_cs_en.en | udpipe --tokenizer='presegmented' --output=horizontal ../../udpipe/models/english-lines-ud-2.3-181115.udpipe > ../data/en_tokenized
#paste ../data/cs_tokenized ../data/en_tokenized | sed 's/\t/ ||| /' > ../data/cs-en.fa
#fast_align -d -o -v -i ../data/cs-en.fa > ../data/cs-en.cs_ali
#fast_align -d -o -v -i ../data/cs-en.fa -r > ../data/cs-en.en_ali
#atools -i ../data/cs-en.cs_ali -j ../data/cs-en.en_ali -c intersect > ../data/cs-en.ali

for i in `seq 2 5`;
do
    cat ../data/cs/cs.tok.$i | udpipe --input=horizontal --tag --parse --output=conllu ../../udpipe/models/czech-pdt-ud-2.3-181115.udpipe > ../data/cs/cs_$i.conllu
    cat ../data/en/en.tok.$i | udpipe --input=horizontal --tag --parse --output=conllu ../../udpipe/models/english-lines-ud-2.3-181115.udpipe > ../data/en/en_$i.conllu
done
