import heapq
import re
import datetime

class General_measurer:
    def __init__( self, allow_substitution=True):
        self.allow_substitution = allow_substitution
    def find_closest_verbs(self, a_verb, list_of_b_verbs, out, min_dist=1000):
        min_verbs = []
        b_verbs_sorted = sorted( list_of_b_verbs, key=lambda b_verb:
                                 self.sort_by_letter( a_verb, b_verb))
        for b_verb in b_verbs_sorted:
            dist = self.levenshtein(a_verb, b_verb, min_dist, 0)
            if dist < min_dist:
                min_dist = dist
                min_verbs = [ b_verb ]
            elif dist == min_dist:
                min_verbs.append( b_verb)
        return min_dist, min_verbs

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

class Cs_Sk_distance_measurer( General_measurer):

    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.dist_00_strings = [('t$', 'ť$'),
                                ('ci$', 'cť$')
                                ]
        self.poly_00_strings = self.dist_00_strings

        self.dist_02_strings = [('a', 'á'), ('á', 'a'),
                                ('e', 'é'), ('é', 'e'), ('ě', 'e'),
                                ('i', 'í'), ('í', 'i'),
                                ('ů', 'ô'),
                                ('u', 'ú'), ('ou', 'ú'), ('ou', 'u'),
                                ('y', 'ý'), ('ý', 'y'),
                                ('a', 'ia'), ('á', 'ia'), ('é', 'ia'), ('í', 'ia'),
                                ('é', 'ie'), ('ě', 'ie'), ('í', 'ie'),
                                ('c', 'č'), ('č', 'c'),
                                ('d', 'ď'), ('ď', 'd'),
                                ('l', 'ľ'),
                                ('lou', 'ĺ'),
                                ('n', 'ň'), ('ň', 'n'),
                                ('r', 'ř'),
                                ('s', 'š'), ('š', 's'),
                                ('t', 'ť'), ('ť', 't'),
                                ('z', 'ž'), ('ž', 'z'), ('z', 'dz'),
                                ('^pro', '^pre'), ('^pře', '^pre'),
                               ]
        self.mono_02_strings = [ ( a_str, b_str ) for a_str, b_str in self.dist_02_strings
                                 if len( a_str) == 1 and len ( b_str) == 1 ]
        self.poly_02_strings = [ ( a_str, b_str ) for a_str, b_str in self.dist_02_strings
                                 if len( a_str) > 1 or len ( b_str) > 1 ]
        self.dist_05_strings = []
        cs_vowels = [ 'a', 'á', 'e', 'é', 'ě', 'i', 'í', 'o', 'ó',
                   'u', 'ú', 'ů', 'y', 'ý' ]
        sk_vowels = [ 'a', 'á', 'ä', 'e', 'é', 'i', 'í', 'o', 'ó', 'ô',
                   'u', 'ú', 'y', 'ý', 'ia', 'ie', 'iu' ]

        for cs_vowel in cs_vowels:
            for sk_vowel in sk_vowels:
                vowel_pair = ( cs_vowel, sk_vowel )
                if vowel_pair not in self.dist_02_strings:
                    self.dist_05_strings.append( vowel_pair)

        self.mono_05_strings = [ ( a_str, b_str ) for a_str, b_str in self.dist_05_strings
                                 if len( a_str) == 1 and len ( b_str) == 1 ]
        self.poly_05_strings = [ ( a_str, b_str ) for a_str, b_str in self.dist_05_strings
                                 if len( a_str) > 1 or len ( b_str) > 1 ]

    def find_closest_verbs( self, a_verb, list_of_b_verbs, out, min_dist=1000, reverse=False):
        gener_a_verbs_plus = self.multichar_changes( a_verb)  # with indices
        #gener_a_verbs_plus = [ ( a_verb, 0, None ) ]
        gener_a_verbs = [ ( gener_a_verb, act_dist ) for gener_a_verb, act_dist, _
                          in gener_a_verbs_plus ]
        min_verbs = []
        for gener_a_verb, act_dist in gener_a_verbs:
            gener_min_dist, gener_min_verbs = super().find_closest_verbs( gener_a_verb, list_of_b_verbs, out, min_dist)
            full_dist = act_dist + gener_min_dist
            if full_dist < min_dist:
                min_dist = full_dist
                min_verbs = gener_min_verbs
            elif full_dist == min_dist:
                min_verbs += gener_min_verbs
        return min_dist, min_verbs

    def multichar_changes( self, verb_a):
        dist = 0
        act_index = 0
        changed_strings = []
        prev_changed_strings = [ ( verb_a, dist, act_index ) ]
        new_changed_strings = []
        chaneges_lists = [ ( self.poly_00_strings, 0 ),
                           ( self.poly_02_strings, 0.2 ),
                           ( self.poly_05_strings, 0.5)
                         ]
        #chaneges_lists = [ ( dist_00_strings, 0 ), ( dist_02_strings, 0.2 ), ( dist_05_strings, 0.5 )]
        finished = False
        while not finished:
            finished = True
            new_changed_strings = []
            for string, dist, act_index in prev_changed_strings:
                for poly_strings, change_dist in chaneges_lists:
                    for a_str, b_str in poly_strings:
                        start_index = string.find( a_str)
                        if start_index >= act_index:
                            finished = False
                            str_1 = string[ :start_index ]
                            str_2 = string[ start_index: ]
                            new_str_2 = re.sub( a_str, b_str, str_2, count=1)
                            new_string = str_1 + new_str_2
                            new_dist = dist + change_dist
                            new_index = start_index + len( b_str)
                            new_changed_strings.append( ( new_string, new_dist, new_index ))
            #new_changed_strings = list( set( new_changed_strings))
            changed_strings += prev_changed_strings
            prev_changed_strings = new_changed_strings
            # tie indexy postupne su zle, lebo pri zkrateni mozes nieco stratit a naopak pro predlzeni mozes aplikovat
            # zmenu na tom istom mieste. musis si tam tie indexy ukladat individualne
        changed_strings += prev_changed_strings
        return changed_strings

    def perform_substitution( self, a_char, b_char):
        if ( a_char, b_char ) in self.mono_02_strings:
            return 0.2
        if ( a_char, b_char ) in self.mono_05_strings:
            return 0.5
        return 1