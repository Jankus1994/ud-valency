from vallex.vallex_matcher import Vallex_matcher

class C_vallex_matcher( Vallex_matcher):
    #def function_agreement( self, ext_arg_deprel, val_arg_functor):
    #    pass

    def form_agreement( self, ext_form, ext_case_mark_rels, val_form):
        if len( ext_case_mark_rels) > 1:
            print( "WARNING! TOO MUCH CASE MARK RELS OF EXT ARGUMENT")
        val_form_list = val_form.split( '-')
        if len( val_form_list) == 3:
            val_conj = val_form_list[ 0 ]
            val_prep = val_form_list[ 1 ]
            val_case = val_form_list[ 2 ]
            if val_case == "":
                val_case = "0"

            ext_case = self.cases[ ext_form ]
            if ext_case_mark_rels == [] and val_prep == "" and val_conj == "":
                if val_case == ext_case:
                    return True

            for ext_case_mark_rel in ext_case_mark_rels:
                try:
                    relation, lemma = ext_case_mark_rel.split( '-')
                except ValueError:
                    #raise ValueError
                    return False
                if relation == "case":
                    ext_prep = lemma
                    if val_case == ext_case and val_prep == ext_prep:
                        return True

                elif relation == "mark":
                    ext_conj = lemma
                    if val_case == ext_case and val_conj == ext_conj:
                        return True
        else:
            print( "WARNING! RARE FORM OF VAL ARGUMENT")
        return False
