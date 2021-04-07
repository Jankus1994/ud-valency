export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

type=$1
name=$2

# vallex/match.py \
#	type of matcher:
#		c = vallex
#		cc = cs_czengvallex
#		e = engvallex and en_czengvallex
#	extracted frames pickle
#	vallex frames input pickle
#	vallex frames output pickle (with matched extracted frames)

# vallex CS
if [[ $type == "c" ]]; then
        python3 vallex/match.py \
		c \
		../data/pic/cs_en_ext_"$name".pic \
                ../data/pic/cs_vallex_frames.pic
# vallex EN (engvallex)
elif [[ $type == "e" ]]; then
        python3 vallex/match.py \
		e \
                ../data/pic/cs_en_ext_"$name".pic \
                ../data/pic/en_vallex_frames.pic
# czengvallex CS
elif [[ $type == "cc" ]]; then
        python3 vallex/match.py \
		cc \
                ../data/pic/cs_en_ext_"$name".pic \
                ../data/pic/cs_czengvallex_frames.pic
# czengvallex EN
elif [[ $type == "ee" ]]; then
        # not a mistake, "e" matcher also used for EN czengvallex
        python3 vallex/match.py \
		e \
		../data/pic/cs_en_ext_"$name".pic \
                ../data/pic/en_czengvallex_frames.pic
elif [[ $type == "ce" ]]; then
	python3 vallex/match.py \
		ce \
		../data/pic/cs_en_ext_"$name".pic \
		../data/pic/cs_czengvallex_frames.pic \
		../data/pic/en_czengvallex_frames.pic \
		../data/pic/matched_dicts_"$name".pic
fi
