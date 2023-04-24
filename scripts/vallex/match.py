"""
script to match frames extracted from the corpus by frame extractor (EXT) with the frames from vallex (VAL)
TODO: prepositions and reflexive pronouns
"""

import logging, sys, pickle
from vallex_loader import *
from c_vallex_matcher import C_vallex_matcher
from e_vallex_matcher import E_vallex_matcher
from cc_vallex_matcher import Cc_vallex_matcher
sys.path.append( "../../udapi-python/udapi/block/valency/")

if __name__ == "__main__":
    matcher_type = sys.argv[ 1 ]
    if matcher_type in [ "c", "e", "cc" ]:
        ext_name = sys.argv[ 2 ]
        val_name = sys.argv[ 3 ]
        out_name = sys.argv[ 4 ]

        with open( ext_name, "rb" ) as ext_file, \
                open( val_name, "rb" ) as val_file, \
                open( out_name, 'wb') as out_file:
            ext_dict = pickle.load( ext_file)
            val_dict = pickle.load( val_file)
            matcher_dict = { "c":  C_vallex_matcher,
                             "e":  E_vallex_matcher,
                             "cc": Cc_vallex_matcher }

            vallex_matcher = matcher_dict[ matcher_type ]( ext_dict, val_dict,
                                                           unique_method=False)
            vallex_matcher.match_frames()
            out_ext_dict, out_val_dict = vallex_matcher.get_matched()
            pickle.dump( out_ext_dict, out_file)

    elif matcher_type == "ce":
        ext_name = sys.argv[ 2 ]
        cs_val_name = sys.argv[ 3 ]
        en_val_name = sys.argv[ 4 ]
        out_name = sys.argv[ 5 ]

        with open( ext_name, "rb" ) as ext_file, \
                open( cs_val_name, "rb" ) as cs_val_file, \
                open( en_val_name, "rb" ) as en_val_file, \
                open( out_name, 'wb') as out_file:
            cs_ext_dict, en_ext_dict = pickle.load( ext_file)
            cs_val_dict = pickle.load( cs_val_file)
            en_val_dict = pickle.load( en_val_file)

            cs_vallex_matcher = Cc_vallex_matcher( cs_ext_dict, cs_val_dict)
            cs_vallex_matcher.match_frames()
            out_cs_ext_dict, out_cs_val_dict = cs_vallex_matcher.get_matched()

            en_vallex_matcher = E_vallex_matcher( en_ext_dict, en_val_dict)
            en_vallex_matcher.match_frames()
            out_en_ext_dict, out_en_val_dict = en_vallex_matcher.get_matched()

            out_dicts = ( out_cs_ext_dict, out_cs_val_dict,
                            out_en_ext_dict, out_en_val_dict )

            #logging.info( sys.getrecursionlimit())
            #logging.info( sys.getsizeof( out_dicts))
            #sys.setrecursionlimit( 50000)
            #logging.info( sys.getrecursionlimit())
            pickle.dump( out_dicts, out_file)


