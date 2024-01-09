from linker import *

class Base_linker( Linker):

    def build_score_table( self, a_items, b_items, a_b_ali_dict, b_a_ali_dict,
                           compute_method):
        score_table = []
        for ai, a_item in enumerate( a_items):
            table_row = []
            for bi, b_item in enumerate( b_items):
                score = int( ai == bi)
                table_row.append( score)
            score_table.append( table_row)
        return score_table

    def get_params( self):
        return "BASE"
