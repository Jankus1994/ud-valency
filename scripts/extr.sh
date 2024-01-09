#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

config="configs/config.yaml"

lang_marks="$1"
if [[ "$lang_marks" == *-* ]]; then
  variant="b"
else
  variant="m"
fi

output_form="$2"  # bin / text / html
treebank=$(grep ^treebank "$config" | sed 's/^[^:]*: *\([^ ]*\).*/\1/' | sed 's/\r//g')
if [ -n "$3" ]; then
  treebank="$3"
fi

input_file="../data/""$variant""_""conllu/""$treebank"".conllu"

start=$(date +%s) #date +"%T.%N"

udapy \
    read.Conllu \
        files="$input_file" \
    valency.Multi_frame_extractor \
        lang_marks="$lang_marks" \
        output_form="$output_form" \
        treebank_name="$treebank" \
        config_name="$config"

end=$(date +%s)
echo Execution time was "$(("$end" - "$start"))" seconds