#!/bin/bash

export PATH=../../fast_align/build:$PATH
export PATH=../../udpipe/bin-linux64:$PATH

: '
script
# '

data=../data
models=../../udpipe/models

corp_name=acquis_cs_en
corp_file=acquis/alignedCorpus_cs_en.xml
L1=CS
L2=EN
udpipe_model_L1=czech-pdt-ud-2.3-181115.udpipe
udpipe_model_L2=english-lines-ud-2.3-181115.udpipe


# >> Extraction of sentences from paralle corpus <<
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: extraction of sentences"
# corpora - input: initial corpus file (format dependent on the corpus)
# sents - output: plain text sentences extracted from the corpus, on separate lines
python3 acquis_extract.py \
	$data/corpora/$corp_file \
	$data/sents/$corp_name.$L1 \
	$data/sents/$corp_name.$L2


# >> Tokenization <<
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: tokenization of senteces"
# sents - udpipe input: plain text sentences extracted from the corpus
# toksents - udpipe output: tokenized plain text sentences
# fast_align - merged tokenized sentences, each pair on one line,
#              in format required by Fast align
cat $data/sents/$corp_name.$L1\
| udpipe --tokenizer='presegmented' --output=horizontal \
	$models/$udpipe_model_L1 \
	> $data/toksents/$corp_name.$L1
cat $data/sents/$corp_name.$L2 \
| udpipe --tokenizer='presegmented' --output=horizontal \
	$models/$udpipe_model_L2 \
	> $data/toksents/$corp_name.$L2
paste \
	$data/toksents/$corp_name.$L1 \
	$data/toksents/$corp_name.$L2 \
| sed 's/\t/ ||| /' \
> $data/fast_align/$corp_name


# >> Word alignment using Fast align <<
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: word alignment"
# fast_align - fast_align input: tokenized senteces, each pair on one line,
#                                in format required by Fast align
# m_aligned - fast_align output / atools input: one(=mono)-directional alignment file
# b_aligned - atools output: two(=bi)-directional alignment file,
#                            intersection of the two above
fast_align -d -o -v \
	-i $data/fast_align/$corp_name \
	> $data/m_aligned/$corp_name.$L1
fast_align -d -o -v -r \
	-i $data/fast_align/$corp_name \
	> $data/m_aligned/$corp_name.$L2
atools \
	-i $data/m_aligned/$corp_name.$L1 \
	-j $data/m_aligned/$corp_name.$L2 \
	-c intersect \
	> $data/b_aligned/$corp_name


# >> UD annotation: tagging and parsing <<
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: tagging and parsing"
# toksents - input: tokenized sentences, each on separate line
# m_conllu - output: monolingual UD annotated corpus
cat \
	$data/toksents/$corp_name.$L1 \
| udpipe --input=horizontal --tag --parse --output=conllu \
	$models/$udpipe_model_L1 \
> $data/m_conllu/$corp_name.$L1.connlu

cat \
	$data/toksents/$corp_name.$L2 \
| udpipe --input=horizontal --tag --parse --output=conllu \
	$models/$udpipe_model_L2 \
> $data/m_conllu/$corp_name.$L2.connlu

# partition version in case the "all" version does not worke
#for i in `seq 2 5`;
#do
#    cat $data/cs/cs.tok.$i | udpipe --input=horizontal --tag --parse --output=conllu ../../udpipe/models/czech-pdt-ud-2.3-181115.udpipe > $data/cs/cs_$i.conllu
#    cat $data/en/en.tok.$i | udpipe --input=horizontal --tag --parse --output=conllu ../../udpipe/models/english-lines-ud-2.3-181115.udpipe > $data/en/en_$i.conllu
#done


# >> Merging two conllu files <<
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: merging two conllu files"
# m_conllu - input: monolingual UD annotated corpus
# L1, L2 - input: zone marks for distinguisging languages in the output file
# b_conllu - output: parallel bilingual UD annotated corpus
python3 merger.py \
	$L1 \
	$data/m_conllu/$corp_name.$L1.conllu \
	$L2 \
	$data/m_conllu/$corp_name.$L2.conllu \
	$data/b_conllu/$corp_name.conllu
