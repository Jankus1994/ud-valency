export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
creation of html valency dictionary for displaying
run from total
# '

name=$1
python3 html_creator.py \
	../data/pic/cs_en_ext_"$name".pic \
	../data/html/cs_en_dic_"$name".html

