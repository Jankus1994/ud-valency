#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

#udapy read.Conllu files=../data/cs_pdt-ud-concat.conllu valency.Frame_extractor output=../data/cs_output.pic
#udapy read.Conllu files=../data/cs_en_pokus.conllu valency.Cs_rame_extractor #> ../data/new_output.txt


#udapy read.Conllu files=../data/cs_pdt-ud-concat.conllu valency.Cs_frame_extractor output=../data/cs_new_output.pic
#python3 html_creator.py ../data/cs_new_output.pic > ../data/cs_new_output.html

#udapy read.Conllu files=../data/pokus_cs valency.Cs_frame_extractor #output=../data/cs_new2_output.pic
#python3 html_creator.py ../data/cs_new2_output.pic > ../data/cs_new2_output.html

#udapy read.Conllu files=../data/cs_pdt-ud-concat.conllu valency.Cs_frame_extractor > cs_raw_new_output.txt
#udapy read.Conllu files=../data/cs_pdt-ud-concat.conllu valency.Old_frame_extractor > cs_raw_old_output.txt
#udapy read.Conllu files=../data/cs_pdt-ud-concat.conllu valency.Cs_frame_extractor > ../data/cs_raw_new2_output.txt

#python3 html_creator.py ../data/cs_output.pic > ../data/cs_output.html
#udapy read.Conllu files=../data/cs_pdt-ud-concat.conllu valency.Frame_extractor > ../data/cs_output.html
#udapy read.Conllu files=../data/fi_tdt-ud-concat.conllu valency.Frame_extractor > ../data/fi_output.html
#udapy read.Conllu files=../data/en_lines-ud-concat.conllu valency.Frame_extractor output=../data/en_output.pic
#python3 html_creator.py ../data/en_output.pic > ../data/en_output.html
#udapy read.Conllu files=../data/en_lines-ud-concat.conllu valency.Old_frame_extractor > ../data/en_output.txt
#udapy read.Conllu files=../data/cs_min valency.Cs_frame_extractor > ../data/cs_red
#udapy read.Conllu files=../data/cs_min valency.Frame_extractor > ../data/cs_med

#udapy read.Conllu files=../data/cs_en_pokus.conllu valency.Cs_En_frame_aligner align_file_name=../data/cs_en_pokus.cs_ali output=../data/cs_en_pokus.pic
#python3 html_creator.py ../data/cs_en_pokus.pic > ../data/cs_en_pokus.html
#udapy read.Conllu files=../data/cs_en_merged/cs_en_1_1_merged.conllu valency.Cs_En_frame_aligner align_file_name=../data/cs_en_align/cs-en_1_1.ali output=../data/cs_en_merged/cs_en_1_1.pic
python3 html_creator.py ../data/cs_en_merged/cs_en_1_1.pic > ../data/cs_en_1_1.html
