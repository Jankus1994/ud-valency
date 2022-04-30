"""
script for aligning czech and english czengvallex frames
run from czengvallex_aligner.sh
not used at this time, the alignment occurs during evaluation
see czengvallex_evaluate.sh and czengvallex_evaluator.py
"""

import sys
import pickle
import xml.etree.ElementTree as et

class Functor_pair:
    def __init__:
        self.cs_functor = None
        self.en_functor = None

#def join_frames( cs_frame, en_frame, cs_en_functor_pairs):


def get_frame_pairs( cs_id_val_frame_dict, en_id_val_frame_dict, align_file_name):
    cs_en_val_frame_pairs = []

    tree = et.ElementTree( file=align_name)
    root = tree.getroot()
    en_frames = root.findall( ".//en_frame")
    for en_frame in en_frames:
        en_frame_id = en_frame.attrib[ "en_id" ]
        en_frame = en_id_frame_dict[ en_frame_id ]
        frame_pairs = en_frame.findall( "frame_pair")
        for frame_pair in frame_pairs:
            cs_frame_id = frame_pair.attrib[ "cs_id" ]
            cs_frame = cs_id_frame_dict[ cs_frame_id ]
            frame_pair = ( cs_frame, en_frame )
            cs_en_val_frame_pairs.append( frame_pair)

            ## slots
            #slots = frame_pair.findall( ".//slot")
            #cs_en_functor_pairs = []
            #for slot in slots:
            #    functor_pair = Functor_pair()
            #    functor_pair.cs_functor = slot.attrib[ "cs_functor" ]
            #    functor_pair.en_functor = slot.attrib[ "en_functor" ]
            #    cs_en_functor_pairs.append( functor_pair)

            #join_frames( cs_frame, en_frame, cs_en_functor_pairs)



if __name__ == "__main__":
    if len( sys.argv) ==4:
        align_file_name   = sys.argv[ 1 ] 
        cs_val_dict_filename = sys.argv[ 2 ]
        en_val_dict_filename = sys.argv[ 3 ]
        cs_id_val_frame_dict = pickle.load( open( cs_val_dict_filename, "rb" ))
        en_id_val_frame_dict = pickle.load( open( en_val_dict_filename, "rb" ))
        process_xml( cs_id_val_frame_dict, en_id_val_frame_dict, align_file_name)



