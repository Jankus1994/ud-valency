import pickle, sys
from vallex.c_vallex_matcher import C_vallex_matcher
from collections import Counter

class Functor_projector:
    def __init__( self, cs_sk_ext_name, vallex_name, output_name, unique_handling):
        self.cs_sk_ext_name = cs_sk_ext_name
        self.vallex_name = vallex_name
        self.output_name = output_name

        self.unique_handling = unique_handling
        self.get_vallex_functors = self.get_all_vallex_fucntors
        if self.unique_handling:
            self.get_vallex_functors = self.get_best_functor

        self.stats = Counter()

    def choose_most_frequents( self, item_list):
        freq_counter = Counter( item_list)
        if freq_counter:
            max_freq = max( freq_counter.values())
            most_freqents = [ key for key, value in freq_counter.items() if value == max_freq ]
            return most_freqents
        else:
            return []

    def get_best_functor( self, cs_ext_arg):
        functors = self.get_all_vallex_fucntors( cs_ext_arg)
        if len( functors) == 1:
            self.stats[ "simple_cs_choice" ] += 1
            return functors[ 0 ]
        elif len( functors) > 1:
            self.stats[ "hard_cs_choice" ] += 1
            return functors[ 0 ]
        else:
            self.stats[ "no_cs_choice" ] += 1
            return []


    def get_all_vallex_fucntors( self, cs_ext_arg):
        functors = [ val_arg.functor for val_arg in cs_ext_arg.matched_args ]

        return functors

    def choose_functor( self, sk_arg, functors):
        chosen_functors = self.choose_most_frequents( functors)
        if len( chosen_functors) == 1:
            self.stats[ "simple_sk_choice" ] += 1
            self.write_functor( sk_arg, chosen_functors[ 0 ])
        elif len( chosen_functors) > 1:
            self.stats[ "hard_sk_choice" ] += 1
            self.write_functor( sk_arg, chosen_functors[ 0 ])
        else:
            self.stats[ "no_sk_choice" ] += 1

    def write_functor( self, sk_arg, functor):
        sk_arg.form += f"*{functor}"

    def load_data( self):
        with open( self.cs_sk_ext_name, 'rb') as cs_sk_ext_dict_file, \
                open( self.vallex_name, "rb" ) as val_file:
            cs_sk_ext_dict, sk_cs_ext_dict = pickle.load( cs_sk_ext_dict_file)
            cs_vallex = pickle.load( val_file)
            return cs_sk_ext_dict, sk_cs_ext_dict, cs_vallex

    def print_stats( self):
        self.stats[ "functors_per_sk_arg" ] = round( self.stats[ "all_handed_functor_num" ] /
                                                     self.stats[ "sk_args_num" ], 2)
        self.stats[ "functors_per_cs_arg" ] = round( self.stats[ "all_handed_functor_num" ] /
                                                     self.stats[ "cs_args_pseudonum" ], 2)
        for key, val in self.stats.items():
            print( key, val)

    def project_functors( self):
        cs_sk_ext_dict, sk_cs_ext_dict, cs_vallex = self.load_data()
        vallex_matcher = C_vallex_matcher( cs_sk_ext_dict, cs_vallex, unique_method=False)
        vallex_matcher.match_frames()

        for verb_record in sk_cs_ext_dict.values():
            for frame in verb_record.frame_types:
                for sk_arg in frame.args:
                    self.stats[ "sk_args_num" ] += 1
                    functors = []
                    for arg_link in sk_arg.links:
                        cs_arg = arg_link.get_other_frame_type_arg( sk_arg)
                        self.stats[ "cs_args_pseudonum" ] += 1
                        self.stats[ "all_handed_functor_num" ] += len( functors)
                        functors += self.get_vallex_functors( cs_arg)
                        self.choose_functor( sk_arg, functors)
                    sk_arg.links = []
                frame.links = []
        self.print_stats()
        with open( self.output_name, 'wb') as output_file:
            sys.setrecursionlimit( 50000)
            pickle.dump( sk_cs_ext_dict, output_file)

if __name__ == "__main__":
     cs_sk_ext_name = sys.argv[ 1 ]
     vallex_name = sys.argv[ 2 ]
     output_name = sys.argv[ 3 ]
     unique_handling = bool( int( sys.argv[ 4 ]))  # 0 / 1
     functor_projector = Functor_projector( cs_sk_ext_name, vallex_name, output_name, unique_handling)
     functor_projector.project_functors()
