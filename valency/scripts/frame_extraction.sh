#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

udapy read.Conllu files=../docs/cs_pdt-ud-concat.conllu valency.Frame_extractor > ../docs/cs_output.txt
udapy read.Conllu files=../docs/fi_tdt-ud-concat.conllu valency.Frame_extractor > ../docs/fi_output.txt
