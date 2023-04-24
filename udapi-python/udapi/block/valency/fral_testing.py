from cs_sk_frame_aligner import Cs_Sk_frame_aligner

from dist_measurer import  Dist_measurer
from cs_sk_dist_measurer import Cs_Sk_dist_measurer

from linker import Linker
from ud_linker import Ud_linker
from fa_linker import Fa_linker
from faud_linker import FaUd_linker
from sim_linker import Sim_linker
from test_gold_linker import Test_gold_linker

def get_test_linker( run_num, a_lang_mark, b_lang_mark):
    sim_treshold = 20
    sim_spec_measurer_name = Dist_measurer
    if b_lang_mark == "sk":
        sim_spec_measurer_name = Cs_Sk_dist_measurer

    run_dict = {
        0: ( Linker, {}),

        # word alignment method
        1: ( Fa_linker, { "onedir_weight": 0 }),
        2: ( Fa_linker, { "onedir_weight": 0.5 }),
        3: ( Fa_linker, { "onedir_weight": 1 }),
        4: ( Fa_linker, { "onedir_weight": 1.5 }),
        5: ( Fa_linker, { "onedir_weight": 2 }),
        6: ( Fa_linker, { "onedir_weight": 2.5 }),
        7: ( Fa_linker, { "onedir_weight": 3 }),


        # sentence structure method
        21: ( Ud_linker, { "params_weights": ( 1, 0, 0, 0, 0, 0 ) }),
        22: ( Ud_linker, { "params_weights": ( 0, 1, 0, 0, 0, 0 ) }),
        23: ( Ud_linker, { "params_weights": ( 0, 0, 1, 0, 0, 0 ) }),
        24: ( Ud_linker, { "params_weights": ( 0, 0, 0, 1, 0, 0 ) }),
        25: ( Ud_linker, { "params_weights": ( 0, 0, 0, 0, 1, 0 ) }),
        26: ( Ud_linker, { "params_weights": ( 0, 0, 0, 0, 0, 1 ) }),

        30: ( Ud_linker, { "params_weights": ( 1, 1, 1, 1, 1, 1 ) }),

        31: ( Ud_linker, { "params_weights": ( 0, 1, 1, 1, 1, 1 ) }),
        32: ( Ud_linker, { "params_weights": ( 1, 0, 1, 1, 1, 1 ) }),
        33: ( Ud_linker, { "params_weights": ( 1, 1, 0, 1, 1, 1 ) }),
        34: ( Ud_linker, { "params_weights": ( 1, 1, 1, 0, 1, 1 ) }),
        35: ( Ud_linker, { "params_weights": ( 1, 1, 1, 1, 0, 1 ) }),
        36: ( Ud_linker, { "params_weights": ( 1, 1, 1, 1, 1, 0 ) }),

        40: ( Test_gold_linker, {}),




        # similarity method
        101: ( Sim_linker, { "measurer_features": ( Dist_measurer,
                                                  { "allow_substitution": False }),
                           "treshold": 20 } ),

        102: ( Sim_linker, { "measurer_features": ( Dist_measurer,
                                                  { "allow_substitution": True }),
                           "treshold": 20 } ),
        103: ( Sim_linker, { "measurer_features": ( sim_spec_measurer_name,
                                                  { "allow_substitution": True }),
                           "treshold": 20 } ),
        104: ( Sim_linker, { "measurer_features": ( sim_spec_measurer_name,
                                                  { "allow_substitution": True }),
                           "treshold": 15 } ),
        105: ( Sim_linker, { "measurer_features": ( sim_spec_measurer_name,
                                                  { "allow_substitution": True }),
                           "treshold": 10 } ),
        106: ( Sim_linker, { "measurer_features": ( sim_spec_measurer_name,
                                                  { "allow_substitution": True }),
                           "treshold": 7 } ),
        107: ( Sim_linker, { "measurer_features": ( sim_spec_measurer_name,
                                                  { "allow_substitution": True }),
                           "treshold": 5 } ),
        108: ( Sim_linker, { "measurer_features": ( sim_spec_measurer_name,
                                                  { "allow_substitution": True }),
                           "treshold": 3 } ),
        109: ( Sim_linker, { "measurer_features": ( sim_spec_measurer_name,
                                                  { "allow_substitution": True }),
                           "treshold": 2 } ),
        110: ( Sim_linker, { "measurer_features": ( sim_spec_measurer_name,
                                                  { "allow_substitution": True }),
                           "treshold": 1 } ),
        111: ( Sim_linker, { "measurer_features": ( sim_spec_measurer_name,
                                                  { "allow_substitution": True }),
                           "treshold": 0 } ),
    }
    linker_name, params_dict = run_dict[ run_num ]
    linker = linker_name( **params_dict)
    return linker