name=$1
python3 merger.py cs ../data/cs/cs_"$name".conllu en ../data/en/en_"$name".conllu > \
	../data/cs_en_merged/cs_en_"$name"_merged.conllu
