"""
script to match frames extracted from the corpus by frame extractor (EXT) with the frames from vallex (VAL)
TODO: prepositions and reflexive pronouns
"""

import sys, logging
from vallex_extractor import *
from vallex_matcher import Vallex_matcher
from c_vallex_matcher import C_vallex_matcher
from e_vallex_matcher import E_vallex_matcher
from cc_vallex_matcher import Cc_vallex_matcher


if __name__ == "__main__":
    if len( sys.argv) == 6 or len( sys.argv) == 4:
        matcher_type = sys.argv[ 1 ]

        cs_en_ext_dicts_filename = sys.argv[ 2 ]
        cs_en_ext_dicts = pickle.load( open( cs_en_ext_dicts_filename, "rb" ))
        cs_ext_dict, en_ext_dict = cs_en_ext_dicts

        if matcher_type in [ "c", "e", "cc" ]:
            val_dict_filename = sys.argv[ 3 ]
            val_dict = pickle.load( open( val_dict_filename, "rb" ))

            #vallex_matcher_class = Vallex_matcher
            #ext_dict = None
            if matcher_type == 'c':  # cs vallex
                vallex_matcher_class = C_vallex_matcher
                ext_dict = cs_ext_dict
            elif matcher_type == 'e':  # engvallex and en czengvallex
                vallex_matcher_class = E_vallex_matcher
                ext_dict = en_ext_dict
            elif matcher_type == 'cc':  # cs czengvallex
                vallex_matcher_class = Cc_vallex_matcher
                ext_dict = cs_ext_dict

            vallex_matcher = vallex_matcher_class( ext_dict, val_dict)
            vallex_matcher.match_frames()


        elif matcher_type == "ce":
            cs_val_dict_filename = sys.argv[ 3 ]
            en_val_dict_filename = sys.argv[ 4 ]
            output_filename = sys.argv[ 5 ]
            cs_val_dict = pickle.load( open( cs_val_dict_filename, "rb" ))
            en_val_dict = pickle.load( open( en_val_dict_filename, "rb" ))

            cs_vallex_matcher = Cc_vallex_matcher( cs_ext_dict, cs_val_dict)
            cs_vallex_matcher.match_frames()
            out_cs_ext_dict, out_cs_val_dict = cs_vallex_matcher.get_matched()

            en_vallex_matcher = E_vallex_matcher( en_ext_dict, en_val_dict)
            en_vallex_matcher.match_frames()
            out_en_ext_dict, out_en_val_dict = en_vallex_matcher.get_matched()

            out_dicts = ( out_cs_ext_dict, out_cs_val_dict, \
                            out_en_ext_dict, out_en_val_dict )


            logging.info( sys.getrecursionlimit())
            logging.info( sys.getsizeof( out_dicts))
            sys.setrecursionlimit( 50000)
            logging.info( sys.getrecursionlimit())
            pickle.dump( out_dicts, open( output_filename, 'wb'))


