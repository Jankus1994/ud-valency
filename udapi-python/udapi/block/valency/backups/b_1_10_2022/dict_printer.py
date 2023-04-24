class Dict_printer:
    @staticmethod
    def print_verb_pairs( a_b_valency_dict):
        print( len( a_b_valency_dict.keys()))
        for a_verb_lemma in a_b_valency_dict.keys():
            print( a_verb_lemma)
            a_verb_record = a_b_valency_dict[ a_verb_lemma ]
            for a_frame_type in a_verb_record.frame_types:
                for a_b_ft_link in a_frame_type.links:
                    b_frame_type = a_b_ft_link.get_the_other_frame_type( a_frame_type)
                    b_verb_lemma = b_frame_type.verb_lemma
                    print( '\t', a_verb_lemma, b_verb_lemma)