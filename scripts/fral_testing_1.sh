#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python:../../udapi-python/udapi/block/valency:$PYTHONPATH

#l2=en
l2=sk

if [ $l2 == en ]
then
  corp_name=acquis_cs_en
  aligner_name=Cs_En_fral_tester
elif [ $l2 == sk ]
then
  corp_name=acquis_cs_sk
  aligner_name=Cs_Sk_fral_tester
fi

data=../data
#
sample_id=123
test_corp_name="$corp_name"_test
sel_corp_name="$test_corp_name"_"$sample_id"
#sel_corp_name=acquis_cs_sk_5k
overall_results_name="$corp_name"_overall

> $data/test_results/"$overall_results_name"
#python3 rand_sent_selector.py $corp_name $test_corp_name $sample_id
for run_num in 101 #21 #22 23 24 25 26 30 31 32 33 34 35 36
do
  res_name="$test_corp_name"_"$run_num"_"$sample_id"

  udapy \
      read.Conllu \
          files=$data/b_conllu/"$sel_corp_name".conllu \
      valency.$aligner_name \
          run_num=$run_num \
          align_file_name=$data/b_aligned/$sel_corp_name \
          output_folder=$data/ext_pic/ \
          output_name=$sel_corp_name \
      > ../data/test_results/"$res_name" #> /dev/null

  #python3 frame_extraction_tester.py $test_corp_name $sample_id $run_num \
  #    >> $data/test_results/"$overall_results_name"
done