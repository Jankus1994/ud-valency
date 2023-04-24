#!/bin/bash

#export PATH=../fast_align/build:$PATH
export PATH=../udpipe/bin-linux64:$PATH


data=../data
models=../udpipe/models

# language-specific parameters
udpipe_model=cs_all-ud-2.10-220711.model
# czech-pdt-ud-2.3-181115.udpipe
# english-lines-ud-2.3-181115.udpipe
corp_name=acquis_cs_sk_5k.cs


#: '
# >> UD annotation: tagging and parsing <<
# toksents - input: tokenized sentences, each on separate line
# m_conllu - output: monolingual UD annotated corpus
act_time=$(date +"%T")
echo -e "\n$act_time"
head -n 100 \
	$data/toksents/$corp_name \
| udpipe --input=horizontal --tag --parse --output=conllu \
	$models/$udpipe_model \
> $data/m_conllu/pokus_"$corp_name".conllu
act_time=$(date +"%T")
echo -e "\n$act_time"

# partition version in case the "all" version does not work
#for i in `seq 2 5`;
#do
#    cat $data/cs/cs.tok.$i | udpipe --input=horizontal --tag --parse --output=conllu ../../udpipe/models/czech-pdt-ud-2.3-181115.udpipe > $data/cs/cs_$i.conllu
#    cat $data/en/en.tok.$i | udpipe --input=horizontal --tag --parse --output=conllu ../../udpipe/models/english-lines-ud-2.3-181115.udpipe > $data/en/en_$i.conllu
#done
# '