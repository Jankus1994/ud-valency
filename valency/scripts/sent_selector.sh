export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

sents_num=$1
name=$2

python3 merged_selector.py \
	$sents_num \
	../data/cs_en_merged/cs_en_all_merged.conllu \
	../data/cs_en_merged/cs_en_"$name"_merged.conllu

cat ../data/cs_en_align/cs-en_all.ali | \
	head -n"$sents_num" > ../data/cs_en_align/cs-en_"$name".ali
