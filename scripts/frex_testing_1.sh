#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python:../../udapi-python/udapi/block/valency:$PYTHONPATH


#name="UD_pud_test.CS"
name="onesent_test"
#name="UD_pud_test.EN"
#name="acquis_cs_sk.sk"
data=../data

#extractor=Frame_extractor
#extractor=Cs_frame_extractor
extractor=En_frame_extractor
#extractor=Extract_control_printer

output_form=text
#output_form=stats
control_gold=../data/test_results/en_control_gold
#control_auto=../data/test_results/en_control_auto
control_auto=""

udapy \
    read.Conllu \
        files="$data"/m_conllu/"$name".conllu \
    valency.$extractor output_form=$output_form
#valency.$extractor output_form=$output_form
#valency.$extractor control_out_name=$control_auto output_form=$output_form

#python3 extract_control_evaluer.py $control_gold $control_auto