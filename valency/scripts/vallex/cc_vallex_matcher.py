from vallex_matcher import Vallex_matcher

class Cc_vallex_matcher( Vallex_matcher):
    #def function_agreement( self, ext_arg_deprel, val_arg_functor):
    #    pass

    def form_agreement( self, ext_case_feat, ext_case_mark_rels, val_form):
        if len( ext_case_mark_rels) > 1:
            print( "WARNING! TOO MUCH CASE MARK RELS OF EXT ARGUMENT")
        val_case = val_form
        if val_case == "None":
            val_case = "0"

        ext_case = self.cases[ ext_case_feat ]

        # ext_case_mark_rels cannot be compared to anything -
        """ CHECK """
        if val_case == ext_case:
            return True
        return False
