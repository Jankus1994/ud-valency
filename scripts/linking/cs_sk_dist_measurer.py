import re
from dist_measurer import Dist_measurer

class Cs_Sk_dist_measurer( Dist_measurer):

    def __init__( self, lang_reverse=False, **kwargs):
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

        if lang_reverse:
            self.poly_00_strings = self.revert_pairs( self.poly_00_strings)
            self.mono_02_strings = self.revert_pairs( self.mono_02_strings)
            self.poly_02_strings = self.revert_pairs( self.poly_02_strings)
            self.mono_05_strings = self.revert_pairs( self.mono_05_strings)
            self.poly_05_strings = self.revert_pairs( self.poly_05_strings)

    def revert_pairs( self, orig_list):
        reverted_list = []
        for b_item, a_item in orig_list:
            reverted_list.append( ( a_item, b_item ))
        return reverted_list

    # def find_closest_verbs( self, a_verb, list_of_b_verbs, out=None, min_dist=1000):
    #     gener_a_verbs_plus = self.multichar_changes( a_verb)  # with indices
    #     #gener_a_verbs_plus = [ ( a_verb, 0, None ) ]
    #     gener_a_verbs = [ ( gener_a_verb, act_dist ) for gener_a_verb, act_dist, _
    #                       in gener_a_verbs_plus ]
    #     min_verb_indices = []
    #     for gener_a_verb, act_dist in gener_a_verbs:
    #         gener_min_dist, gener_min_verbs_indices = super().find_closest_verbs(
    #                 gener_a_verb, list_of_b_verbs, out, min_dist)
    #         full_dist = act_dist + gener_min_dist
    #         if full_dist < min_dist:
    #             min_dist = full_dist
    #             min_verb_indices = gener_min_verbs_indices
    #         elif full_dist == min_dist:
    #             min_verb_indices += gener_min_verbs_indices
    #     return min_dist, min_verb_indices

    def multichar_changes( self, verb_a):
        dist = 0
        act_index = 0
        changed_strings = []
        prev_changed_strings = [ ( verb_a, dist, act_index ) ]
        new_changed_strings = []
        changes_lists = [ ( self.poly_00_strings, 0 ),
                           ( self.poly_02_strings, 0.2 ),
                           ( self.poly_05_strings, 0.5)
                         ]
        #chaneges_lists = [ ( dist_00_strings, 0 ), ( dist_02_strings, 0.2 ), ( dist_05_strings, 0.5 )]
        finished = False
        while not finished:
            finished = True
            new_changed_strings = []
            for string, dist, act_index in prev_changed_strings:
                for poly_strings, change_dist in changes_lists:
                    for a_str, b_str in poly_strings:
                        if b_str[ 0 ] == '^':
                            b_str = b_str[ 1: ]
                        if b_str[ -1 ] == '$':
                            b_str = b_str[ :-1 ]
                        match = re.search( a_str, string)
                        start_index = match.start() if match else -1
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