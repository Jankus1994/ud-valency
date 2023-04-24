class Dist_measurer:
    def __init__( self, allow_substitution=True):
        self.allow_substitution = allow_substitution
    # def find_closest_verbs(self, a_verb, list_enum_b_verbs, out, min_dist=1000):
    #     min_verb_indices = []
    #     #min_verbs = []
    #     b_verbs_sorted = sorted( list( list_enum_b_verbs), key=lambda index_verb:
    #                              self.sort_by_letter( a_verb, index_verb[ 1 ]))
    #     for index, b_verb in b_verbs_sorted:
    #         dist = self.levenshtein( a_verb, b_verb, min_dist, 0)
    #         if dist < min_dist:
    #             min_dist = dist
    #             #min_verbs = [ b_verb ]
    #             min_verb_indices = [ index ]
    #         elif dist == min_dist:
    #             min_verb_indices.append( index)
    #             #min_verbs.append( b_verb)
    #     return min_dist, min_verb_indices
    #     #return min_dist, min_verbs

    def compute_dists( self, a_verb, b_verbs, min_dist=1000):
        dists = []
        for b_verb in b_verbs:
            dist = self.levenshtein( a_verb, b_verb, min_dist, 0)
            dists.append( dist)
        return dists

    def sort_by_letter( self, a_verb, b_verb):
        # language-dependent heuristic: sorting by first letter
        if a_verb[ 0 ] == b_verb[ 0 ]:# and a_verb[ -2 ] == b_verb[ -2 ]:
            return 0
        if a_verb[ 0 ] != b_verb[ 0 ]:# and a_verb[ -2 ] != b_verb[ -2 ]:
            return 2
        return 1

    def levenshtein( self, string_a, string_b, act_min, act_price):
        # heuristic: return if we cannot improve the actual minimum due to the length difference
        len_diff = abs( len( string_b) - len( string_a))
        if act_min < len_diff + act_price:
            return len_diff + act_price

        # proper levenshtein algorithm
        if string_a == "" or string_b == "":
            return act_price + len( string_a + string_b)
        elif string_a[0] == string_b[0]:
            return self.levenshtein( string_a[1:], string_b[1:], act_min, act_price)
        else:  # first sign differs, so price certainly raises at least by 1
            # heuristic: to improve (or achieve) the minimum, the actual price must be smaller
            if act_min <= act_price:
                return act_price + 1

            insertion = self.levenshtein( string_a[1:], string_b,
                                     act_min, act_price + 1)
            if insertion == act_price + 1:  # other operations cannot achieve better result
                return insertion

            min_act_ins = min( act_min, insertion)  # possible improving actual minimum
            deletion = self.levenshtein( string_a, string_b[1:],
                                    min_act_ins, act_price + 1)
            if deletion == act_price + 1:  # substitution cannot achieve better result
                return deletion

            if not self.allow_substitution:  # least common substring: insertion and deletion without substitution
                return min( insertion, deletion)
            min_act_ins_del = min( min_act_ins, deletion)  # possible improving actual minimum
            subst_price = self.perform_substitution( string_a[0], string_b[0])
            substitution = self.levenshtein( string_a[1:], string_b[1:],
                                        min_act_ins_del, act_price + subst_price)

            return min( insertion, deletion, substitution)

    def perform_substitution( self, a_char, b_char):

        return 1