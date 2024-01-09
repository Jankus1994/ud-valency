#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

: '
script running the most important part of the program - the valency frame extraction
uses Udapi scenario, which reads a parallel bilingual conllu file
and then runs the extraction on it
this script is run from total.sh
input:
    cs_en_merged/cs_en_"$name"_merged.conllu - bilingual conllu corpus
    cs_en_align/cs-en_"$name".ali - word alignment file
output:
    pic/ext_"$name".pic - binary file with extracted valency dictionary
# '

#sh eval_frame_extraction.sh m UD_pud.CS cs

variant=$1  # m mu b bu
#treebank_name=$2 #sk_snk-ud-dev
# UD_pud.CS
# UD_pud.EN
#output_form=$3
lang_mark_1=$2
exam_code=$3
#lang_mark_2=$5
#run_num=$6

#modals=""
#
#while getopts ":m:r:" opt; do
#  case $opt in
#    m) modals="$OPTARG"
#    ;;
#    r) run_num="$OPTARG"
#    ;;
#    \?) echo "Invalid option -$OPTARG" >&2
#    exit 1
#    ;;
#  esac
#
#  case $OPTARG in
#    -*) echo "Option $opt needs a valid argument"
#    exit 1
#    ;;
#  esac
#done
#
#echo $modals


#test_config_file="test_config.txt"
#
#while read -r line; do
#  echo $line
#done < "$test_config_file"
#exit

test_config_file="test_config.txt"
while read -r line; do
  if [[ $line != \#* && $line != $(printf '\r')* ]]; then
    line2=$(echo $line | sed 's/ */ /;s/\r//')
    name=$(echo $line2 | sed 's/\(.*\) .*/\1/')
    value=$(echo $line2 | sed 's/.* \(.*\)/\1/')
    if [ -n "$name" ] && [ -n "$value" ]; then
      declare $name"="$value
    else
      echo "Error: Invalid format in line - '$name$IFS$value'"
    fi
  fi
done < "$test_config_file"

# variables from test config: test_data, gold_res

data="../data/"
#output_folder="$data""text_out/"
#output_suffix=".txt"
gold_name="$data""gold_results/""$gold_res"."$lang_mark_1"".txt"
mist_name="$data""logs/eval_mistakes."
#if [ $output_form = "html" ] || [ $output_form = "htmlw" ]; then
#  output_folder="$data""html_out/"
#  output_suffix=".html"
#elif [ $output_form = "bin" ]; then
#  output_folder="$data""pickle/"
#  output_suffix=".bin"
#elif [ $output_form = "test" ]; then
#  output_folder="$data""test_results/"
#fi

input_folder="$data""m_conllu/"
input_suffix=".conllu"

input_file="$input_folder""$test_data"".""$lang_mark_1""$input_suffix"

if [ "$variant" = mu ]; then
  lang_mark_1="xx"
fi

if [ $# -eq 2 ]; then
  udapy \
      read.Conllu \
          files="$input_file" \
      valency."Eval_frame_extractor" \
          lang_mark=$lang_mark_1 \
          gold_name="$gold_name" \
          mist_name="$mist_name"
else
  udapy \
      read.Conllu \
          files="$input_file" \
      valency."Eval_frame_extractor" \
          lang_mark="$lang_mark_1" \
          gold_name="$gold_name" \
          mist_name="$mist_name" \
          exam_code="$exam_code"
fi
#
#if [ $variant = m ]; then
#  input_folder="$data""m_conllu/"
#  input_suffix=".conllu"
#  udapy \
#      read.Conllu \
#          files="$input_folder""$treebank_name""$input_suffix" \
#      valency."val_frame_extractor" \
#          lang_mark=$lang_mark_1 \
#          gold_name="$gold_name" \
#          mist_name="$mist_name" \
#          output_form=$output_form \
#          output_name="$output_folder""$treebank_name""$output_suffix" \
#          exam_code=$exam_code #\
#          #modals="$modals"
#else
#  #for i in 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
#  #for i in 2 3 4 5 6 7 8 9 10
#  #for i in 2
#  #do
#  #read.Conllu bundles_per_doc=50 \
#  #align_file_name=$data/b_aligned/$name \
#  #for i in 0 1 2 3 4 5 6
#  #do
#  udapy \
#      read.Conllu \
#          files=$data/b_conllu/$name.conllu \
#      valency.Cs_Sk_fral_tester \
#          run_num=$run_num \
#          align_file_name=$data/b_aligned/$name \
#          output_form=$data/ext_pic/ \
#          output_name=$name #\
#  #            obl_ratio_limit=0.5 \
#  #            min_obl_inst_num=$i
#  #done
#fi
