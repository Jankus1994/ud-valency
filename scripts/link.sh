#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

config="configs/config.yaml"

lang_marks="$1"
output_form="$2"  # bin / text / html
treebank=$(grep ^treebank "$config" | sed 's/^[^:]*: *\([^ ]*\).*/\1/' | sed 's/\r//g')
if [ -n "$3" ]; then
  treebank="$3"
fi

start=$(date +%s) #date +"%T.%N"

python3 linking/frame_linking.py "$lang_marks" "$output_form" "$treebank" "$config"

end=$(date +%s)
echo Execution time was "$(("$end" - "$start"))" seconds.