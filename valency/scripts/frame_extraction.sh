#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

udapy read.Conllu files=../data/cs_pdt-ud-concat.conllu valency.Frame_extractor > ../data/cs_output.txt
udapy read.Conllu files=../data/fi_tdt-ud-concat.conllu valency.Frame_extractor > ../data/fi_output.txt
