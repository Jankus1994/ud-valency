#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python:../../udapi-python/udapi/block/valency:$PYTHONPATH

file_name=../data/match_pic/_acquis_cs_sk_test_123
#file_name=../data/match_pic/_acquis_cs_sk_5k
# extract czech-slovak valency dictionary
#bash fral_testing_1.sh

# load czech vallex frames
#bash vallex_loader.sh c

# match extracted and vallex czech frames
bash vallex_match.sh c _acquis_cs_sk_test_123
#bash vallex_match.sh c _acquis_cs_sk_5k

# transfer vallex information from czech to slovak
#python3 vallex_projector.py $file_name