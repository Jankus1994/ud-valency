#!/bin/bash

export PATH=../udapi-python/bin:$PATH
export PYTHONPATH=../udapi-python:../udapi-python/udapi/block/valency:$PYTHONPATH

cs_sk_ext_name="../data/b_bin_link/acquis_cs_sk_test300.bin"
vallex_name="../data/val_bin/cs_vallex_frames"
output_name="../data/m_bin_extr/sk_vallexed.bin"
unique_handling=$1  # 0 / 1

python3 functor_projector.py $cs_sk_ext_name $vallex_name $output_name $unique_handling