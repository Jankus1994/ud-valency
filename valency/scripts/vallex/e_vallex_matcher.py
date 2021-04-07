from vallex_matcher import Vallex_matcher

class E_vallex_matcher( Vallex_matcher):
    def __init__( self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.prepositions = [ "to", "for", "with", "on", "as", "from", "into", "that", \
                                "of", "up", "down", "over", "under", "about", "by" ]
    #def function_agreement( self, ext_arg_deprel, val_arg_functor):
    #    pass

    def form_agreement( self, ext_case_feat, ext_case_mark_rels, val_form):
        """ ext_case_feat relevant for pronouns, ignored for now """
        #print( val_form)
        if len( ext_case_mark_rels) > 1:
            print( "WARNING! TOO MUCH CASE MARK RELS OF EXT ARGUMENT")

        val_prepositions = []
        if val_form != "":
            val_form_list = val_form.split( '[')
            if len( val_form_list) == 1:  # preposition or verbform
                val_prepositions = [ val_form_list[ 0 ] ]
            elif len( val_form_list) == 2:  # preposition
                val_prep_forms = val_form_list[ 0 ].strip( "{}")
                val_prepositions = val_prep_forms.split( ',')
            else:
                print( "WARNING! RARE FORM OF VAL ARGUMENT")
        
        #print( ext_case_mark_rels)
        #print( val_prepositions)
        #print( "---")
        if ext_case_mark_rels == [] and val_prepositions == []:
            return True
        for ext_case_mark_rel in ext_case_mark_rels:
            ext_preposition = ext_case_mark_rel.split( '-')[ 0 ]
            for val_preposition in val_prepositions:
                if val_preposition in self.prepositions and \
                        val_preposition == ext_preposition:
                    return True

        return False
