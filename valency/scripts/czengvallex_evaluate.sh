export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

name=$1

python3 vallex/czengvallex_evaluator.py \
	../data/czengvallex/frames_pairs.xml \
	../data/pic/matched_dicts_"$name".pic
