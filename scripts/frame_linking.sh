#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

data="../data"

input_file="$data/ext_bin/cs_en_PUD"
output_file="$data/link_bin/cs_en_PUD"

start=`date +%s` #date +"%T.%N"
python3 linking/frame_linking.py $input_file $output_file
end=`date +%s`
echo Execution time was `expr $end - $start` seconds.