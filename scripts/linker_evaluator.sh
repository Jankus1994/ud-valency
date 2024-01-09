#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

eval_type=$1  # vall / gold
prep_eval=$2  # vall: prep / feval / aeval ; gold: feval / aeval

tolink_name="../data/text_out/UD_pud.txt.tolink"
cs_val_name="../data/val_bin/cs_czengvallex_frames"
en_val_name="../data/val_bin/en_czengvallex_frames"
val_align_name="../data/czengvallex/frames_pairs.xml"

gold_align_name="../data/gold_results/gold_res.cs_en.txt"

start=`date +%s` #date +"%T.%N"
if [ "$eval_type" == "gold" ]; then
  python3 linking/gold_linker_evaluator.py $tolink_name $gold_align_name $prep_eval
else
  python3 linking/vallex_linker_evaluator.py $tolink_name $cs_val_name $en_val_name $val_align_name \
        $prep_eval
fi
end=`date +%s`
echo Execution time was `expr $end - $start` seconds.



