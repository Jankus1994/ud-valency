from linker import Linker

class Sim_linker( Linker):
    #def __init__( self, measurer_features=None, threshold=0, **kwargs):
    def __init__( self, allow_subst=None, **kwargs):
        super().__init__( **kwargs)
        self.allow_subst =allow_subst
        self.lang_spec = False
        #self.threshold = threshold
        #self.matching_finder = Min_matching_finder()

    def compute_frame_pair_score( self, a_frame_inst, b_frame_inst, _, __):
        a_verb = a_frame_inst.type.verb_lemma
        b_verb = b_frame_inst.type.verb_lemma

        dist = self.distance( a_verb, b_verb, 1000, 0)
        score = 1 / ( dist + 1 )

        return score

    def compute_arg_pair_score( self, a_arg_inst, b_arg_inst, _, __):
        a_arg_lemma = a_arg_inst.token.lemma
        b_arg_lemma = b_arg_inst.token.lemma

        dist = self.distance( a_arg_lemma, b_arg_lemma, 1000, 0)
        score = 1 / ( dist + 1 )

        return score
    #
    # def get_feats( self, a_frame_inst, b_frame_inst):
    #     feats_points = []
    #     return feats_points

    def get_params( self):
        return "Sim params:  allow_subst=" + str( self.allow_subst) + ", lang_spec=" + \
               str( self.lang_spec) + ", threshold=" + str( self.threshold)

# === measurer

    def compute_dists( self, a_verb, b_verbs, min_dist=1000):
        dists = []
        for b_verb in b_verbs:
            dist = self.distance( a_verb, b_verb, min_dist, 0)
            dists.append( dist)
        return dists

    def sort_by_letter( self, a_verb, b_verb):
        # language-dependent heuristic: sorting by first letter
        if a_verb[ 0 ] == b_verb[ 0 ]:# and a_verb[ -2 ] == b_verb[ -2 ]:
            return 0
        if a_verb[ 0 ] != b_verb[ 0 ]:# and a_verb[ -2 ] != b_verb[ -2 ]:
            return 2
        return 1

    def distance( self, string_a, string_b, act_min, act_price):
        # heuristic: return if we cannot improve the actual minimum due to the length difference
        len_diff = abs( len( string_b) - len( string_a))
        if act_min < len_diff + act_price:
            return len_diff + act_price

        # joint levenshtein/lcs algorithm
        if string_a == "" or string_b == "":
            return act_price + len( string_a + string_b)
        elif string_a[0] == string_b[0]:
            return self.distance( string_a[1:], string_b[1:], act_min, act_price)
        else:  # first sign differs, so price certainly raises at least by 1
            # heuristic: to improve (or achieve) the minimum, the actual price must be smaller
            if act_min <= act_price:
                return act_price + 1

            insertion = self.distance( string_a[1:], string_b,
                                     act_min, act_price + 1)
            if insertion == act_price + 1:  # other operations cannot achieve better result
                return insertion

            min_act_ins = min( act_min, insertion)  # possible improving actual minimum
            deletion = self.distance( string_a, string_b[1:],
                                    min_act_ins, act_price + 1)
            if deletion == act_price + 1:  # substitution cannot achieve better result
                return deletion

            if not self.allow_subst:  # least common substring: insertion and deletion without substitution
                return min( insertion, deletion)
            min_act_ins_del = min( min_act_ins, deletion)  # possible improving actual minimum
            subst_price = self.perform_substitution( string_a[0], string_b[0])
            substitution = self.distance( string_a[1:], string_b[1:],
                                        min_act_ins_del, act_price + subst_price)

            return min( insertion, deletion, substitution)

    def perform_substitution( self, a_char, b_char):
        return 1