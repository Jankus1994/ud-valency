export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

name=$1
python3 html_creator.py \
	../data/pic/cs_en_"$name".pic \
	../data/html/cs_en_"$name".html

