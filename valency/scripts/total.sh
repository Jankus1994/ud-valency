#export PATH=../../udapi-python/bin:$PATH
#export PYTHONPATH=../../udapi-python/udapi/block/valency:$PYTHONPATH

sents_num=$1
select_name=$2

corp_name=acquis_cs_en
#corp_name=UD_pud
L1_mark=cs
L2_mark=en

name="$corp_name"_"$select_name"
#name=acquis_cs_en_5k
name=UD_pud

: '
# PREPARING THE CORPUS
bash prepare_corpus.sh \
	$L1_mark \
	$L2_mark \
	czech-pdt-ud-2.3-181115.udpipe \
	english-lines-ud-2.3-181115.udpipe \
	$corp_name \
	acquis/alignedCorpus_cs_en.xml
# '

: '
# Sentences selection
act_time=$(date +"%T")
echo -e "\n$act_time\tPreparation of the corpus - selection of sentences"
bash sent_selector.sh $sents_num $select_name $corp_name $L1_mark $L2_mark > /dev/null
# '

#: '
# FRAME EXTRACTION
#name="$corp_name"_"$select_name"
act_time=$(date +"%T")
echo -e "\n$act_time\tExtraction of frames from a parallel corpus"
bash frame_extraction.sh $name #> /dev/null
exit
# '

: '
# HTML DICTIONARY CREATION
act_time=$(date +"%T")
echo -e "\n$act_time\tCreation of HTML dictionary"
bash html_creator.sh $name #> /dev/null
# '

#: '
# ((CZ)ENG)VALLEX FRAMES LOADING
#act_time=$(date +"%T")
#echo -e "\n$act_time\tLoading CS Vallexx frames"
#bash vallex_loader.sh c
#act_time=$(date +"%T")
#echo -e "\n$act_time\tLoading EngvVallexx frames"
#bash vallex_loader.sh e
act_time=$(date +"%T")
echo -e "\n$act_time\tLoading CS CzEngVallex frames" > /dev/null 
bash vallex_loader.sh cc
act_time=$(date +"%T")
echo -e "\n$act_time\tLoading EN CzEngVallex frames" > /dev/null
bash vallex_loader.sh ee
# '

#: '
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
# '


#: '
# CZENGVALLEX EVALUATION
act_time=$(date +"%T")
echo -e "\n$act_time\tEvaluation"
bash czengvallex_evaluate.sh $name
# '
