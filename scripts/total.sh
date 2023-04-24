#export PATH=../../udapi-python/bin:$PATH
#export PYTHONPATH=../../udapi-python/udapi/block/valency:$PYTHONPATH

#sents_num=$1
#select_name=$2

#corp_name=acquis_cs_en
corp_name=acquis_cs_sk
#corp_name=UD_pud
L1_mark=cs
L2_mark=en
#L2_mark=sk

name="$corp_name"_"$select_name"
#name=acquis_cs_en_5k
#name=UD_pud
#name=acquis_cs_sk
name=acquis_cs_en
#model1=czech-pdt-ud-2.3-181115.udpipe
#model2=czech-pdt-ud-2.3-181115.udpipe
model1=czech-pdt-ud-2.5-191206.udpipe
model2=slovak-snk-ud-2.5-191206.udpipe
source=acquis/alignedCorpus_cs_en.xml
#source=acquis/alignedCorpus_cs_sk.xml


: '
# PREPARING THE CORPUS
bash prepare_corpus.sh \
	$L1_mark \
	$L2_mark \
	$model1 \
	$model2 \
	$name \
	$source
# '

: '
# Sentences selection
act_time=$(date +"%T")
echo $corp_name
echo -e "\n$act_time\tPreparation of the corpus - selection of sentences"
bash sent_selector.sh $sents_num $select_name $corp_name $L1_mark $L2_mark > /dev/null
act_time=$(date +"%T")
echo -e "\n$act_time"
# '

#: '
# FRAME EXTRACTION
corp_name=$1
sents_num=$2
test_corp_name="$corp_name"_test
sel_corp_name="$test_corp_name"_$sents_num
#name="$corp_name"_"$select_name"
#name="$corp_name"_"$select_name"
run_num=$3

#python3 sampler.py $corp_name $test_corp_name $sents_num

act_time=$(date +"%T")
#echo -e "\n$act_time\tExtraction of frames from a parallel corpus"
bash frame_extraction.sh $sel_corp_name $run_num > ../data/test_results/"$test_corp_name"_"$run_num"_"$sents_num" #> /dev/null
act_time=$(date +"%T")
#echo -e "\n$act_time"

python3 frame_extraction_tester.py $test_corp_name $sents_num $run_num

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


: '
# CZENGVALLEX EVALUATION
act_time=$(date +"%T")
echo -e "\n$act_time\tEvaluation"
bash czengvallex_evaluate.sh $name
# '