export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

sents_num=$1
name=$2

# needed:
# cs conllu file - data/cs/cs_all.conllu
# en conllu file - data/en/en_all.conllu
# align file     - data/cs_en_align/cs-en_all.ali

# >>> PREPARING THE CORPUS <<<



# Sentences selection
echo "Preparation of the corpus - selection of sentences"
bash sent_selector.sh $sents_num $name > /dev/null

# FRAME EXTRACTION
echo "Extraction of frames from a parallel corpus"
bash frame_extraction.sh $name > /dev/null

# HTML DICTIONARY CREATION
echo "Creation of HTML dictionary"
bash html_creator.sh $name > /dev/null

# ((CZ)ENG)VALLEX FRAMES LOADING
#echo "Loading CS Vallexx frames"
#bash vallex_loader.sh c
#echo "Loading EngvVallexx frames"
#bash vallex_loader.sh e
echo "Loading CS CzEngVallexx frames" > /dev/null 
bash vallex_loader.sh cc
echo "Loading EN CzEngVallexx frames" > /dev/null
bash vallex_loader.sh ee


# ((CZ)ENG)VALLEX MATCHING
#echo "Matching frames with CS Vallex"
#bash vallex_match.sh c $name > /dev/null
#echo "Matching frames with EngVallex"
#bash vallex_match.sh e $name > /dev/null
#echo "Matching CS frames with CS CzEngVallex"
#bash vallex_match.sh cc $name > /dev/null
#echo "Matching EN frames with EN CzEngVallex"
#bash vallex_match.sh ee $name > /dev/null
echo "Matching CS and EN frames with CzEngVallex"
bash vallex_match.sh ce $name > /dev/null

# CZENGVALLEX EVALUATION
echo "Evaluation"
bash czengvallex_evaluate.sh $name
