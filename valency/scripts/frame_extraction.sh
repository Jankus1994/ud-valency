#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

udapy read.Conllu files=../data/cs_pdt-ud-concat.conllu valency.Frame_extractor > ../data/cs_output.html
udapy read.Conllu files=../data/fi_tdt-ud-concat.conllu valency.Frame_extractor > ../data/fi_output.html
udapy read.Conllu files=../data/en_lines-ud-concat.conllu valency.Frame_extractor > ../data/en_output.html
