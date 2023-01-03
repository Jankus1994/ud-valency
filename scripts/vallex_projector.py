import sys
import pickle
from collections import defaultdict
from vallex.vallex_frame import Vallex_frame
from vallex.vallex_argument import Vallex_argument
sys.path.append("vallex/")

class Vallex_projector:
    def __init__( self):
        self.lang_2_mark = "sk"

    def project_vallex_info( self, input_name):
        with open( input_name, "rb") as input_file:
            cs_dict = pickle.load( input_file)
            sk_vallex_dict = defaultdict( list)
            for cs_verb_lemma in cs_dict.keys():
                cs_verb_record = cs_dict[ cs_verb_lemma ]
                for cs_frame_type in cs_verb_record.frame_types:
                    cs_vallex_frames = cs_frame_type.matched_frames
                    cs_sk_links = cs_frame_type.links
                    sk_frame_types = [ link.get_the_other_frame_type( cs_frame_type)
                                       for link in cs_sk_links ]
                    for cs_vallex_frame in cs_vallex_frames:
                        for sk_frame_type in sk_frame_types:
                            sk_vallex_frame = self.create_vallex_frame(
                                    cs_vallex_frame, sk_frame_type)
                            sk_vallex_frame = self.transfer_args(
                                    cs_vallex_frame, sk_vallex_frame)
                            sk_verb_lemma = sk_frame_type.verb_lemma
                            sk_vallex_dict[ sk_verb_lemma ].append( sk_vallex_frame)
            return sk_vallex_dict


    def create_vallex_frame( self, cs_vallex_frame, sk_frame_type):
        sk_vallex_frame = Vallex_frame( self.lang_2_mark, cs_vallex_frame.id)
        lemmas = [ sk_frame_type.verb_lemma ]
        sk_vallex_frame.set_lemmas( lemmas)
        sk_vallex_frame.set_refl( cs_vallex_frame.refl)
        return sk_vallex_frame

    def transfer_args( self, cs_vallex_frame,  sk_vallex_frame):
        for cs_arg in cs_vallex_frame.arguments:
            sk_arg = Vallex_argument()
            sk_arg.set_functor( cs_arg.functor)
            sk_arg.set_form( cs_arg.form)
            sk_arg.is_obligatory = cs_arg.is_obligatory
            sk_arg.type = cs_arg.type
            sk_vallex_frame.add_argument( sk_arg)
        return sk_vallex_frame

if __name__ == "__main__":
    if len( sys.argv) == 2:
        input_name = sys.argv[ 1 ]
        vallex_projector = Vallex_projector()
        sk_vallex_dict = vallex_projector.project_vallex_info( input_name)
        sk_val_frame_strs = []
        for sk_val_frames in sk_vallex_dict.values():
            for sk_val_frame in sk_val_frames:
                sk_val_frame_str = sk_val_frame.to_string()
                sk_val_frame_strs.append( sk_val_frame_str)
        sk_val_frame_strs = sorted( list( set( sk_val_frame_strs)))
        actual_lemma = ""
        for sk_val_frame_str in sk_val_frame_strs:
            if actual_lemma not in sk_val_frame_str:
                print ( "")
            actual_lemma = sk_val_frame_str.split( ' ')[ 0 ]
            print( sk_val_frame_str)



