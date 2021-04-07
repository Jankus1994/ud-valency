type=$1

# general, not used
if [ -z $type ]; then
	python3 vallex/vallex_loader.py \
		../data/vallex_3.0.xml \
		../data/pic/vallex_frames.pic
# vallex CS
elif [ $type == "c" ]; then
	python3 vallex/cs_vallex_loader.py \
		../data/vallex_3.0.xml \
		../data/pic/cs_vallex_frames.pic
# vallex EN (engvallex)
elif [ $type == "e" ]; then
	python3 vallex/engvallex_loader.py \
		../data/engvallex.xml \
		../data/pic/en_vallex_frames.pic
# czengvallex CS
elif [ $type == "cc" ]; then
	python3 vallex/czengvallex_cs_loader.py \
		../data/czengvallex/vallex_cz.xml \
		../data/pic/cs_czengvallex_frames.pic
# czengvallex EN
elif [ $type == "ee" ]; then
	# not a mistake, also used for EN czengvallex
	python3 vallex/engvallex_loader.py \
		../data/czengvallex/vallex_en.xml \
		../data/pic/en_czengvallex_frames.pic
fi
