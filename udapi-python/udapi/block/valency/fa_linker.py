import sys

from linker import *
from collections import defaultdict

class Fa_linker( Linker):
    def __init__( self, onedir_weight=1, **kwargs):
        super().__init__( **kwargs)
        self.onedir_weight = onedir_weight

    def create_ali_dicts( self, word_alignments):
        #start = datetime.now()
        a_b_ali_dict = {}
        b_a_ali_dict = {}
        for word_alignment in word_alignments:
            if '<' in word_alignment:
                sign = '<'
            elif '>' in word_alignment:
                sign = '>'
            else: #if '=' in word_alignment:
                sign = '='
            a_index_str, b_index_str = word_alignment.split( sign)
            a_index = int( a_index_str) + 1
            b_index = int( b_index_str) + 1
            if sign in [ '>', '=']:  # TODO skontrolovat spravny smer
                a_b_ali_dict[ a_index ] = b_index
            if sign in [ '<', '=']:
                b_a_ali_dict[ b_index ] = a_index
        #self.cad_time_counter += datetime.now() - start
        return a_b_ali_dict, b_a_ali_dict

    def process_verb_index( self, x_verb_index, y_verb_index, y_verb_indices,
                            xy_ali_dict, yx_ali_dict):
        alis_to_x = [ y_index for y_index in yx_ali_dict.keys()
                      if yx_ali_dict[ y_index ] == x_verb_index ]

        if y_verb_index in alis_to_x:
            yx_points = 3  # the considered counterpart points to x
        elif set( alis_to_x) & set( y_verb_indices):
            yx_points = 2  # (at least one) another verb points to x
        elif alis_to_x:
            yx_points = 1  # (at least one) non-verb points to x
        else:
            yx_points = 0  # nothing points to x


        y_index = xy_ali_dict[ x_verb_index ]
        if y_index == y_verb_index:
            xy_points = 3  # x points to the considered counterpart
        elif y_index in y_verb_indices:
            xy_points = 2  # x points to another verb
        else:
            xy_points = 1  # x points to a non-verb

        reciproc = 0
        if yx_ali_dict[ y_index ] == x_verb_index:
            reciproc = 1  # the pointic of x is reciprocated

        return [ yx_points, xy_points, reciproc ]

    #def get_score( self, ali_dict, ali_dict_key, _, __):
    #    """ separated for overloading in FaUd_linker """
    #    return ali_dict[ ali_dict_key ]
    def compute_pair_score( self, xa_verb_index, xb_verb_index, a_verb_indices,
                            b_verb_indices, a_b_ali_dict, b_a_ali_dict):
        feats = self.get_feats( xa_verb_index, xb_verb_index, a_verb_indices,
                b_verb_indices, a_b_ali_dict, b_a_ali_dict)
        score = 0
        if feats[ 0 ] == 3 and feats[ 3 ] == 3:
            score = 2
        elif feats[ 0 ] == 3 or feats[ 3 ] == 3:
            score = 1
        return score

    def get_feats( self, a_frame_inst, b_frame_inst, a_verb_indices,
                            b_verb_indices, a_b_ali_dict, b_a_ali_dict):
        xa_verb_index = a_frame_inst.verb_node_ord
        xb_verb_index = b_frame_inst.verb_node_ord

        # TODO stara verzia
        ab = xa_verb_index in a_b_ali_dict and \
                a_b_ali_dict[ xa_verb_index ] == xb_verb_index
        ba = xb_verb_index in b_a_ali_dict and \
                b_a_ali_dict[ xb_verb_index ] == xa_verb_index
        if ab and ba:
            return [ 2 ]
        elif ab or ba:
            return [ 1 ]
        else:
            return [ 0 ]

        xa_feats = self.process_verb_index( xa_verb_index, xb_verb_index,
                b_verb_indices, a_b_ali_dict, b_a_ali_dict)
        xb_feats = self.process_verb_index( xb_verb_index, xa_verb_index,
                a_verb_indices, b_a_ali_dict, a_b_ali_dict)
        return xa_feats + xb_feats

    def build_score_table( self, a_frame_insts, b_frame_insts, word_alignments):
        a_b_ali_dict, b_a_ali_dict = self.create_ali_dicts( word_alignments)
        a_verb_indices = [ a_frame_inst.verb_node_ord
                           for a_frame_inst in a_frame_insts ]
        b_verb_indices = [ b_frame_inst.verb_node_ord
                           for b_frame_inst in b_frame_insts ]

        #start = datetime.now()
        score_table = []
        for a_frame_inst in a_frame_insts:
            table_row = []

            for b_frame_inst in b_frame_insts:
                #ali_dict_key = ( a_verb_index, b_verb_index )
                score = self.compute_pair_score( a_frame_inst, b_frame_inst,
                        a_verb_indices, b_verb_indices, a_b_ali_dict, b_a_ali_dict)
                #score = self.get_score( ali_dict, ali_dict_key,
                #                        a_frame_inst, b_frame_inst)
                table_row.append( score)
            score_table.append( table_row)
        return score_table

    # @staticmethod
    # def _frame_alignment( frst_frame_insts, scnd_frame_insts,
    #                       frst_scnd_ali_dict):  # void
    #     """ called from find_frame_pairs
    #     aligns frame types and frame instances of two languages
    #     the alignment depends on a given word alignment dictionary
    #     which is either a->b or b->a
    #     so here are labels "frst" and "scnd" used instead
    #     """
    #     frame_inst_pairs = []
    #     # aligning frame instances
    #     for frst_frame_inst in frst_frame_insts:
    #         frst_frame_type = frst_frame_inst.type
    #         frst_verb_index = frst_frame_inst.verb_node_ord
    #         # print( frst_verb_index, frst_frame_inst.verb_node.form)
    #         try:
    #             scnd_verb_index = frst_scnd_ali_dict[frst_verb_index]
    #         except KeyError:  # this token was not aligned
    #             # print( "    OOOO")
    #             continue
    #         for scnd_frame_inst in scnd_frame_insts:
    #             if scnd_frame_inst.verb_node_ord == scnd_verb_index:
    #                 chosen_scnd_frame_inst = scnd_frame_inst
    #                 break
    #         else:  # the token was not aligned to any verb token
    #             # print( "    XXXX")
    #             continue
    #
    #         # unmatched instances will have "frame_type_link" attribute still None
    #         scnd_frame_type = chosen_scnd_frame_inst.type
    #
    #         # frame_pair = Frame_pair( frst_frame_type, scnd_frame_type, \
    #         #                        frst_frame_inst, chosen_scnd_frame_inst)
    #         frame_inst_pair = Frame_pair(frst_frame_inst, chosen_scnd_frame_inst)
    #         frame_inst_pairs.append(frame_inst_pair)
    #     return frame_inst_pairs

    @staticmethod
    def find_arg_pairs( a_frame_inst, b_frame_inst, word_alignments):
        tok_index_pairs = []
        for word_alignment in word_alignments:
            a_index_str, b_index_str = word_alignment.split('-')
            a_index = int( a_index_str)
            b_index = int( b_index_str)
            tok_index_pair = ( a_index + 1, b_index + 1 )
            tok_index_pairs.append( tok_index_pair)

        arg_pairs = []
        for a_index, a_token in enumerate( a_frame_inst.sent_tokens):
            for b_index, b_token in enumerate( b_frame_inst.sent_tokens):
                if a_token.is_frame_arg() and b_token.is_frame_arg() and \
                        ( a_index, b_index ) in tok_index_pairs:
                    a_frame_inst_arg = a_token.arg
                    b_frame_inst_arg = b_token.arg
                    frame_inst_arg_pair = ( a_frame_inst_arg, b_frame_inst_arg )
                    arg_pairs.append( frame_inst_arg_pair)
        return arg_pairs

    #def print_stats( self):
    #    print( round( self.cad_time_counter, 3), round( self.bst_time_counter, 3),
    #            file=sys.stderr)