from linker import *
from matching_finder import Min_matching_finder
from frame_pair import Frame_pair
from collections import defaultdict
from dist_measurer import Dist_measurer

class Sim_linker( Linker):
    #def __init__( self, measurer_features=None, threshold=0, **kwargs):
    def __init__( self, measurer_features=None, **kwargs):
        super().__init__( **kwargs)
        measurer_name = measurer_features[ 0 ]
        self.measurer_parameters = measurer_features[ 1 ]
        self.measurer = measurer_name( **self.measurer_parameters)
        self.allow_subst = self.measurer.allow_substitution
        self.lang_spec = False
        if type( self.measurer) is not Dist_measurer:
            self.lang_spec = True
        #self.threshold = threshold
        #self.matching_finder = Min_matching_finder()

    def compute_frame_pair_score( self, a_frame_inst, b_frame_inst, _, __):
        a_verb = a_frame_inst.type.verb_lemma
        b_verb = b_frame_inst.type.verb_lemma

        dist = self.measurer.levenshtein( a_verb, b_verb, 1000, 0)
        score = 1 / ( dist + 1 )

        return score

    def compute_arg_pair_score( self, a_arg_inst, b_arg_inst, _, __):
        a_arg_lemma = a_arg_inst.token.lemma
        b_arg_lemma = b_arg_inst.token.lemma

        dist = self.measurer.levenshtein( a_arg_lemma, b_arg_lemma, 1000, 0)
        score = 1 / ( dist + 1 )

        return score
    #
    # def get_feats( self, a_frame_inst, b_frame_inst):
    #     feats_points = []
    #     return feats_points

    def get_params( self):
        return "Sim params:  allow_subst=" + str( self.allow_subst) + ", lang_spec=" + \
               str( self.lang_spec) + ", threshold=" + str( self.threshold)
