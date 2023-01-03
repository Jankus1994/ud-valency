corp_name=$1
sample_id=$2
test_corp_name="$corp_name"_test
sel_corp_name="$test_corp_name"_$sample_id
run_num=$3


python3 rand_sent_selector.py $corp_name $test_corp_name $sample_id

act_time=$(date +"%T")
#echo -e "\n$act_time\tExtraction of frames from a parallel corpus"
bash frame_extraction.sh $sel_corp_name $run_num > ../data/test_results/"$test_corp_name"_"$run_num"_"$sample_id" #> /dev/null
act_time=$(date +"%T")
#echo -e "\n$act_time"

python3 frame_extraction_tester.py $test_corp_name $sample_id $run_num