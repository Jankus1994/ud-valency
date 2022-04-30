#!/bin/bash

export PATH=../../fast_align/build:$PATH
export PATH=../../udpipe/bin-linux64:$PATH

data=../data
models=../../udpipe/models

L1=CS
L1_zone_mark=cs
L2=EN
L2_zone_mark=en
corp_name=UD_pud
udpipe_model_L1=czech-pdt-ud-2.3-181115.udpipe
udpipe_model_L2=english-lines-ud-2.3-181115.udpipe
#
#: '
# >> Extraction of sentences from UD corpus <<
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: extraction of sentences"
# corpora - input: initial corpus file (format dependent on the corpus)
# sents - output: plain text sentences extracted from the corpus, on separate lines
python3 ud_sent_extractor.py \
	$data/m_conllu/$corp_name.$L1.conllu \
	> $data/sents/$corp_name.$L1
python3 ud_sent_extractor.py \
	$data/m_conllu/$corp_name.$L2.conllu \
	> $data/sents/$corp_name.$L2
# '

#: '
# >> Tokenization <<
act_time=$(date +"%T")
echo -e "\n$act_time\tCorpus preparation: tokenization of senteces"
# sents - udpipe input: plain text sentences extracted from the corpus
# toksents - udpipe output: tokenized plain text sentences
# fast_align - merged tokenized sentences, each pair on one line,
#              in format required by Fast align
cat $data/sents/$corp_name.$L1\
| udpipe --tokenizer="presegmented" --output=horizontal \
	$models/$udpipe_model_L1 \
	> $data/toksents/$corp_name.$L1
cat $data/sents/$corp_name.$L2 \
| udpipe --tokenizer="presegmented" --output=horizontal \
	$models/$udpipe_model_L2 \
	> $data/toksents/$corp_name.$L2
paste \
	$data/toksents/$corp_name.$L1 \
	$data/toksents/$corp_name.$L2 \
| sed "s/\t/ ||| /" \
> $data/fast_align/$corp_name
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
# '

#: '
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
# '
