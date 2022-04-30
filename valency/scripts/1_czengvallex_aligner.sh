: '
script for aligning czech and english czengvallex frames
not used at this time, the alignment occurs during evaluation
see czengvallex_evaluate.sh and czengvallex_evaluator.py
'

python3 vallex/czengvallex_aligner.py \
	 ../data/czengvallex/frames_pairs.xml \
	../data/czengvallex_cs_frames_zmaz \
	../data/czengvallex_en_frames_zmaz
