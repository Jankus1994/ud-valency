export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
selects a given number of sentences from a parallel czech-english conllu file
and prints them to output file
used during development when not necessery to process the whole corpus
selects corresponding lines from alignment file
run from total.sh
input:
    cs_en_merged/cs_en_all_merged.conllu - parallel bilingual conllu file
    cs_en_align/cs-en.ali - alignment file
output: selected sentences
    cs_en_merged/cs_en_"$name"_merged - parallel bilingual conllu file
    cs_en_align/cs-en_"$name" - alignment file
# '

sents_num=$1
name=$2

python3 sent_selector.py \
	$sents_num \
	../data/cs_en_merged/cs_en_all_merged.conllu \
	../data/cs_en_merged/cs_en_"$name"_merged.conllu

cat ../data/cs_en_align/cs-en.ali | \
	head -n"$sents_num" > ../data/cs_en_align/cs-en_"$name".ali
