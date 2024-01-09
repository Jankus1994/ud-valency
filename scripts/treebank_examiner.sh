#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

: '
scripts for examining various phenomena in hte treebank, inlcuding
- oblique dependents
- coordination
'
data="../data/"
run_examiner () {
  treebank_name=$1
  gold_name=$2
  lang_mark=$3
  input_file="$data"/m_conllu/"$treebank_name".conllu
  udapy \
      read.Conllu \
          files="$input_file" \
      valency.Obl_examiner \
          gold_name="$data""gold_results/""$gold_name"".txt"
  udapy \
      read.Conllu \
          files="$input_file" \
      valency.Treebank_examiner \
          lang_mark="xx"
}
run_examiner UD_pud.cs gold_res.cs cs
echo ""
echo ""
run_examiner UD_pud.en gold_res.en en
#run_examiner UD_pud.ES