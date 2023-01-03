export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
selects a given number of sentences from a parallel czech-english conllu file
and prints them to output file
used during development when not necessery to process the whole corpus
selects corresponding lines from alignment file
run from total.sh
input:
    parallel bilingual conllu file (b_conllu)
    corresponding word alignment file (b_aligned)
output:
    analogous, but only first $sent_num sentences selected from both input files
# '

sents_num=$1
select_name=$2
corp_name=$3
L1_mark=$4
L2_mark=$5

data=../data

#: '
python3 sent_selector.py \
	$sents_num \
	"$data"/b_conllu/"$corp_name".conllu \
	"$data"/b_conllu/"$corp_name"_"$select_name".conllu \
	$L1_mark \
	$L2_mark

cat "$data"/b_aligned/"$corp_name" \
| head -n"$sents_num" \
> "$data"/b_aligned/"$corp_name"_"$select_name"
# '