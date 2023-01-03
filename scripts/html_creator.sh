export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
creation of html valency dictionary for displaying
run from total.sh
input:
    pic/cs_en_ext_"$name".pic - binary file with extracted valency dictionary
output:
    html/cs_en_dic_"$name".html - html file with valency dictionary for displaying
# '

name=$1
data=../data
python3 html_creator.py \
	$data/ext_pic/$name \
	$data/html/$name.html

