#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH
export PATH=../fast_align/build:$PATH
export PATH=../udpipe/bin-linux64:$PATH

tokenization() {
  treebank="$1"
  lang_mark="$2"
  sents_dir="$3"
  m_toksents_dir="$4"
  udpipe_model="$5"

  act_time=$(date +"%T")
  echo -e "\n$act_time\tCorpus preparation: tokenization of sentences: ""$lang_mark"
  cat "$sents_dir""$treebank"".""$lang_mark" \
  | ./udpipe --tokenizer="presegmented" --output=horizontal "$udpipe_model" \
    > "$m_toksents_dir""$treebank"".""$lang_mark"
  act_time=$(date +"%T")
  echo -e "\n""$act_time"" DONE"
}
word_alignment() {
  treebank="$1"
  a_lang_mark="$2"
  b_lang_mark="$3"
  m_toksents_dir="$4"
  b_toksents_dir="$5"
  m_aligned_dir="$6"
  b_aligned_dir="$7"

  act_time=$(date +"%T")
  echo -e "\n$act_time\tCorpus preparation: word alignment"
  paste \
    "$m_toksents_dir""$treebank"."$a_lang_mark" \
    "$m_toksents_dir""$treebank"."$a_lang_mark" \
    | sed "s/\t/ ||| /" \
    > "$b_toksents_dir""$treebank"
  fast_align -d -o -v -i "$b_toksents_dir""$treebank" \
    > "$m_aligned_dir""$treebank"."$a_lang_mark"
  fast_align -d -o -v -r -i "$b_toksents_dir""$treebank" \
    > "$m_aligned_dir""$treebank"."$b_lang_mark"
  python3 fa_interpreter.py \
    "$m_aligned_dir""$treebank"."$a_lang_mark" \
    "$m_aligned_dir""$treebank"."$b_lang_mark" \
    "$b_aligned_dir""$treebank"
  act_time=$(date +"%T")
  echo -e "\n""$act_time"" DONE"
}
tagging_parsing() {
  treebank="$1"
  lang_mark="$2"
  m_toksents="$3"
  m_conllu="$4"
  udpipe_model="$5"

  act_time=$(date +"%T")
  echo -e "\n$act_time\tCorpus preparation: tagging and parsing: ""$lang_mark"
  cat "$m_toksents""$treebank"".""$lang_mark" \
  | ./udpipe --input=horizontal --tag --parse --output=conllu "$udpipe_model" \
  > "$m_conllu""$treebank"".""$lang_mark"".conllu"
  act_time=$(date +"%T")
  echo -e "\n$act_time"" DONE"
}
whole_udpipe() {
  treebank="$1"
  lang_mark="$2"
  sents_dir="$3"
  m_conllu="$4"
  udpipe_model="$5"

  act_time=$(date +"%T")
  echo -e "\n$act_time\tCorpus preparation: tokenization, tagging and parsing: ""$lang_mark"
  cat "$sents_dir""$treebank"".""$lang_mark" \
  | ./udpipe --tokenizer="presegmented" --tag --parse --output=conllu "$udpipe_model" \
  > "$m_conllu""$treebank"".""$lang_mark"".conllu"
  act_time=$(date +"%T")
  echo -e "\n$act_time"" DONE"
}
conllu_merging() {
  treebank="$1"
  a_lang_mark="$2"
  b_lang_mark="$3"
  m_conllu="$4"
  b_conllu="$5"

  act_time=$(date +"%T")
  echo -e "\n$act_time\tCorpus preparation: merging two conllu files"
  # m_conllu - input: monolingual UD annotated corpus
  # L1, L2 - input: zone marks for distinguisging languages in the output file
  # b_conllu - output: parallel bilingual UD annotated corpus
  python3 conllu_merger.py \
    "$a_lang_mark" "$m_conllu""$treebank"".""$a_lang_mark"".conllu" \
    "$b_lang_mark" "$m_conllu""$treebank"".""$b_lang_mark"".conllu" \
    "$b_conllu""$treebank"".conllu"
  act_time=$(date +"%T")
  echo -e "\n$act_time"" DONE"
}

get_from_config() {
  pattern="$1"
  config="$2"
  result=$(grep ^"$pattern" "$config" | sed 's/^[^:]*: *\([^ ]*\).*/\1/' | sed 's/\r//g')
  echo "$result"
}

config="configs/config.yaml"

lang_marks="$1"
treebank=$(get_from_config "treebank" "$config")
if [ -n "$2" ]; then
  treebank="$2"
fi

if [[ "$lang_marks" == *-* ]]; then
  variant="b"
  a_lang_mark=$(echo "$lang_marks" | sed 's/\(.*\)-.*/\1/')
  b_lang_mark=$(echo "$lang_marks" | sed 's/.*-\(.*\)/\1/')
else
  variant="m"
  a_lang_mark="$lang_marks"
fi

sents_dir=$(get_from_config "sents" "$config")
m_conllu=$(get_from_config "m_conllu" "$config")
a_udpipe_model=$(get_from_config "a_udpipe_model" "$config")

if [ "$variant" = "m" ]; then
  whole_udpipe "$treebank" "$a_lang_mark" "$sents_dir" "$m_conllu" "$a_udpipe_model"
else
  m_toksents=$(get_from_config "m_toksents" "$config")
  b_toksents=$(get_from_config "b_toksents" "$config")
  m_aligned=$(get_from_config "m_aligned" "$config")
  b_aligned=$(get_from_config "b_aligned" "$config")
  b_conllu=$(get_from_config "b_conllu" "$config")
  b_udpipe_model=$(get_from_config "b_udpipe_model" "$config")

  tokenization "$treebank" "$a_lang_mark" "$sents_dir" "$m_toksents" "$a_udpipe_model"
  tokenization "$treebank" "$b_lang_mark" "$sents_dir" "$m_toksents" "$b_udpipe_model"
  word_alignment "$treebank" "$a_lang_mark" "$b_lang_mark" "$m_toksents" "$b_toksents" \
      "$m_aligned" "$b_aligned"
  tagging_parsing "$treebank" "$a_lang_mark" "$m_toksents" "$m_conllu" "$a_udpipe_model"
  tagging_parsing "$treebank" "$b_lang_mark" "$m_toksents" "$m_conllu" "$b_udpipe_model"
  conllu_merging "$treebank" "$a_lang_mark" "$b_lang_mark" "$m_conllu" "$b_conllu"
fi