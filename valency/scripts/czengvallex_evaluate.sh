export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
runs alignment of czengvallex frames and evaluation of the extracted
czech-english valency dictionary against czengvallex
run from total.sh
input:
    czengvallex alignment files
    binary file with matched extracted and czengvallex frames
output:
    evaluation statistics on standard output
# '

name=$1

python3 vallex/czengvallex_evaluator.py \
	../data/czengvallex/frames_pairs.xml \
	../data/pic/matched_dicts_"$name".pic
