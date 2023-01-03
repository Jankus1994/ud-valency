#!/bin/bash

export PATH=../../fast_align/build:$PATH
export PATH=../../udpipe/bin-linux64:$PATH

: '
script for preparing the corpus
language-independent, accepts particular langage-specific parameters

input: initial corpus file, as obtained from the corpus project
output:
    1) parallel bilingual UD annotated (tagged and parsed) corpus in conllu format
    2) word alignment file

parts:
a) extracting the sentences from the corpus to plain text (for each language separately)
b) [a] -> tokenization
c) [b] -> word alignment using fast align tool 
       -> output (2)
d) [b] -> UD tagging and parsing using UDPipe tool to conllu files
e) [d] -> merging the two conllu files into one bilingual conllu file
       -> output (1)
# '

data=../data
models=../udpipe-models

# language-specific parameters
L1=$1  # CS
L2=$2  # EN
L1_zone_mark=$1
L2_zone_mark=$2
udpipe_model_L1=$3  # czech-pdt-ud-2.3-181115.udpipe
udpipe_model_L2=$4  # english-lines-ud-2.3-181115.udpipe
corp_name=$5  # acquis_cs_en
corp_file=$6  # acquis/alignedCorpus_cs_en.xml

#L1=EN
#L1_zone_mark=en
#L2=ES
#L2_zone_mark=es
#udpipe_model_L1=english-lines-ud-2.3-181115.udpipe
#udpipe_model_L2=spanish-ancora-ud-2.3-181115.udpipe
#corp_name=acquis_cs_es
#corp_file=acquis/alignedCorpus_cs_es.xml



: '
# >> Extraction of sentences from parallel corpus <<
# duration: 16 sec
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: extraction of sentences"
# corpora - input: initial corpus file (format dependent on the corpus)
# sents - output: plain text sentences extracted from the corpus, on separate lines
python3 acquis_extract.py \
	$data/corpora/$corp_file \
	$data/sents/$corp_name.$L1 \
	$data/sents/$corp_name.$L2
act_time=$(date +"%T")
echo -e "\n"$act_time" DONE"
# '

: '
# >> Tokenization <<
# duration: 27 min (cs-en)
# duration: 1h 15 min (cs-sk)
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: tokenization of sentences"
# sents - udpipe input: plain text sentences extracted from the corpus
# toksents - udpipe output: tokenized plain text sentences
# fast_align - merged tokenized sentences, each pair on one line,
#              in format required by Fast align
cat $data/sents/$corp_name.$L1\
| ./udpipe --tokenizer="presegmented" --output=horizontal \
	$models/$udpipe_model_L1 \
	> $data/toksents/$corp_name.$L1
cat $data/sents/$corp_name.$L2 \
| ./udpipe --tokenizer="presegmented" --output=horizontal \
	$models/$udpipe_model_L2 \
	> $data/toksents/$corp_name.$L2
paste \
	$data/toksents/$corp_name.$L1 \
	$data/toksents/$corp_name.$L2 \
| sed "s/\t/ ||| /" \
> $data/fast_align/$corp_name
act_time=$(date +"%T")
echo -e "\n"$act_time" DONE"
# '

#: '
# >> Word alignment using Fast align <<
# duration: 23 min 
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: word alignment"
# fast_align - fast_align input: tokenized senteces, each pair on one line,
#                                in format required by Fast align
# m_aligned - fast_align output / atools input: one(=mono)-directional alignment file
# b_aligned - atools output: two(=bi)-directional alignment file,
#                            intersection of the two above
#fast_align -d -o -v \
#	-i $data/fast_align/$corp_name \
#	> $data/m_aligned/$corp_name.$L1
#fast_align -d -o -v -r \
#	-i $data/fast_align/$corp_name \
#	> $data/m_aligned/$corp_name.$L2
python3 fa_interpreter.py \
  $data/m_aligned/$corp_name.$L1 \
  $data/m_aligned/$corp_name.$L2 \
	$data/b_aligned/$corp_name
# '

: '
# >> UD annotation: tagging and parsing <<
# duration: 6 h 56 min (cs - cca 4:40 h, en - cca  4:15)
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: tagging and parsing"
# toksents - input: tokenized sentences, each on separate line
# m_conllu - output: monolingual UD annotated corpus
cat \
	$data/toksents/$corp_name.$L1 \
| udpipe --input=horizontal --tag --parse --output=conllu \
	$models/$udpipe_model_L1 \
> $data/m_conllu/$corp_name.$L1.conllu
act_time=$(date +"%T")
echo -e "\n$act_time"
cat \
	$data/toksents/$corp_name.$L2 \
| udpipe --input=horizontal --tag --parse --output=conllu \
	$models/$udpipe_model_L2 \
> $data/m_conllu/$corp_name.$L2.conllu
act_time=$(date +"%T")
echo -e "\n$act_time"

# partition version in case the "all" version does not work
#for i in `seq 2 5`;
#do
#    cat $data/cs/cs.tok.$i | udpipe --input=horizontal --tag --parse --output=conllu ../../udpipe/models/czech-pdt-ud-2.3-181115.udpipe > $data/cs/cs_$i.conllu
#    cat $data/en/en.tok.$i | udpipe --input=horizontal --tag --parse --output=conllu ../../udpipe/models/english-lines-ud-2.3-181115.udpipe > $data/en/en_$i.conllu
#done
# '

: '
# >> Merging two conllu files <<
# duration: 2 min
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: merging two conllu files"
# m_conllu - input: monolingual UD annotated corpus
# L1, L2 - input: zone marks for distinguisging languages in the output file
# b_conllu - output: parallel bilingual UD annotated corpus
python3 merger.py \
	$L1_zone_mark \
	$data/m_conllu/$corp_name.$L1.conllu \
	$L2_zone_mark \
	$data/m_conllu/$corp_name.$L2.conllu \
	$data/b_conllu/$corp_name.conllu
act_time=$(date +"%T")
echo -e "\n$act_time"
# '
