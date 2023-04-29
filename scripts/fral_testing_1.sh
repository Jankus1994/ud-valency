#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

data=../data
allres="allres"

run_test () {
  corp=$1
  run_num=$2
  sample_id=$3
  frame_aligner=$4
  test_corp=$5
  gold_results=$5


}

process_corp () {
  corp=$1
  frame_aligner=$2
  all_results=$data/test_results/"$corp"_"$allres"
  : > $all_results
  for sample_id in 1 #12 123
  do
    test_corp="$corp"_"$sample_id"
    gold_results=../data/test_results/gold_"$test_corp"
    log_file=../data/logs/"$test_corp"
    python3 data_examiner.py $gold_results >> $all_results
    for run_num in 21
    do
      auto_results=../data/test_results/auto_"$test_corp"_"$run_num"

      udapy  \
          read.Conllu \
              files="$data"/b_conllu/"$test_corp".conllu \
          valency."$frame_aligner" \
              gold_file_name=$gold_results \
              run_num="$run_num" \
              align_file_name="$data"/b_aligned/"$test_corp" \
              output_form=$output_form \
              output_folder="$data"/ext_bin/ \
              output_name="$test_corp" \
              log_file_name="$log_file" \
          > $auto_results #> /dev/null

      echo $corp "sample:" $sample_id "run num:" $run_num \
        >> $all_results

      echo "----------" >> $all_results

      python3 frame_extraction_tester.py $gold_results $auto_results \
          >> $all_results

      echo "====================" >> $all_results
    done
  done
}



if [ $1 == en ]
then
  corp=UD_pud #acquis_cs_en
  frame_aligner=Cs_En_fral_tester
elif [ $1 == sk ]
then
  corp=acquis_cs_sk
  frame_aligner=Cs_Sk_fral_tester
fi

output_folder="$data""text_out/"
output_suffix=".txt"
if [ $output_form = "html" ] || [ $output_form = "htmlw" ]; then
  output_folder="$data""html_out/"
  output_suffix=".html"
elif [ $output_form = "bin" ]; then
  output_folder="$data""ext_bin/"
  output_suffix=".bin"
elif [ $output_form = "test" ]; then
  output_folder="$data""test_results/"
fi

process_corp $corp $frame_aligner $output_form $output_suffix $output_folder


