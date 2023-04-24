#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

data=../data

process_corp () {
  corp=$1
  frame_feat_examiner=$2
  test_corp="$corp"_123
  gold_results=../data/test_results/gold_"$test_corp"
  udapy  \
      read.Conllu \
          files="$data"/b_conllu/"$test_corp".conllu \
      valency.$frame_feat_examiner \
          align_name="$data"/b_aligned/"$test_corp" \
          output_name="$data"/logs/"$test_corp" \
          gold_name="$gold_results"
}



if [ $1 == en ]
then
  corp=acquis_cs_en
  frame_feat_examiner=Cs_En_fral_feats_examiner
elif [ $1 == sk ]
then
  corp=acquis_cs_sk
  frame_feat_examiner=Cs_Sk_fral_feats_examiner
fi

process_corp $corp $frame_feat_examiner


