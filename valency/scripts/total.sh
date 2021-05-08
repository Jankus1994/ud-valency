export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

sents_num=$1
name=$2


: '
# PREPARING THE CORPUS
bash prepare_corpus.sh \
	CS EN \
	czech-pdt-ud-2.3-181115.udpipe \
	english-lines-ud-2.3-181115.udpipe \
	acquis_cs_en \
	acquis/alignedCorpus_cs_en.xml
# '

# Sentences selection
act_time=$(date +"%T")
echo -e "\n$act_time\tPreparation of the corpus - selection of sentences"
bash sent_selector.sh $sents_num $name > /dev/null

# FRAME EXTRACTION
act_time=$(date +"%T")
echo -e "\n$act_time\tExtraction of frames from a parallel corpus"
bash frame_extraction.sh $name > /dev/null

# HTML DICTIONARY CREATION
act_time=$(date +"%T")
echo -e "\n$act_time\tCreation of HTML dictionary"
bash html_creator.sh $name > /dev/null

# ((CZ)ENG)VALLEX FRAMES LOADING
#act_time=$(date +"%T")
#echo -e "\n$act_time\tLoading CS Vallexx frames"
#bash vallex_loader.sh c
#act_time=$(date +"%T")
#echo -e "\n$act_time\tLoading EngvVallexx frames"
#bash vallex_loader.sh e
act_time=$(date +"%T")
echo -e "\n$act_time\tLoading CS CzEngVallexx frames" > /dev/null 
bash vallex_loader.sh cc
act_time=$(date +"%T")
echo -e "\n$act_time\tLoading EN CzEngVallexx frames" > /dev/null
bash vallex_loader.sh ee


# ((CZ)ENG)VALLEX MATCHING
#act_time=$(date +"%T")
#echo -e "\n$act_time\tMatching frames with CS Vallex"
#bash vallex_match.sh c $name > /dev/null
#act_time=$(date +"%T")
#echo -e "\n$act_time\tMatching frames with EngVallex"
#bash vallex_match.sh e $name > /dev/null
#act_time=$(date +"%T")
#echo -e "\n$act_time\tMatching CS frames with CS CzEngVallex"
#bash vallex_match.sh cc $name > /dev/null
#act_time=$(date +"%T")
#echo -e "\n$act_time\tMatching EN frames with EN CzEngVallex"
#bash vallex_match.sh ee $name > /dev/null
act_time=$(date +"%T")
echo -e "\n$act_time\tMatching CS and EN frames with CzEngVallex"
bash vallex_match.sh ce $name > /dev/null

# CZENGVALLEX EVALUATION
act_time=$(date +"%T")
echo -e "\n$act_time\tEvaluation"
bash czengvallex_evaluate.sh $name
