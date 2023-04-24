export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
script for loading individual vallex-style dictionaries
they are used for evaluation
run from total.sh
input:
    xml file containing particular vallex-style dictionary
output:
    binary file with loaded vallex-style dictionary structure
# '

type=$1

data=../data

# general, not used
if [ -z $type ]; then
	python3 vallex/vallex_loader.py \
		$data/vallex_3.0.xml \
		$data/val_bin/vallex_frames
# vallex CS
elif [ $type == "c" ]; then
	python3 vallex/cs_vallex_loader.py \
		$data/vallex_4.5.xml \
		$data/val_bin/cs_vallex_frames
# vallex EN (engvallex)
elif [ $type == "e" ]; then
	python3 vallex/engvallex_loader.py \
		$data/engvallex_2.0.xml \
		$data/val_bin/en_vallex_frames
# czengvallex CS
elif [ $type == "cc" ]; then
	python3 vallex/czengvallex_cs_loader.py \
		$data/czengvallex/vallex_cz.xml \
		$data/val_bin/cs_czengvallex_frames
# czengvallex EN
elif [ $type == "ee" ]; then
	# not a mistake, also used for EN czengvallex
	python3 vallex/engvallex_loader.py \
		$data/czengvallex/vallex_en.xml \
		$data/val_bin/en_czengvallex_frames
fi
