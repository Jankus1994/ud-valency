#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

udapy read.Conllu files=../docs/cs_pdt-ud-concat.conllu valency.Frame_extractor > cs_output.txt
udapy read.Conllu files=../docs/fi_tdt-ud-concat.conllu valency.Frame_extractor > fi_output.txt
