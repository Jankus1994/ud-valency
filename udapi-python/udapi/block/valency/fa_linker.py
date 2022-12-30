from linker import *
from collections import defaultdict


class Fa_linker( Linker):
    def __init__( self, onedir_weight=1, **kwargs):
        super().__init__( **kwargs)
        self.onedir_weight = onedir_weight

    def create_ali_dict( self, word_alignments):
        ali_dict = defaultdict( int)
        for word_alignment in word_alignments:
            if '=' in word_alignment:
                a_index_str, b_index_str = word_alignment.split( '=')
                points = 2
            else: #if '<' in word_alignment or '>' in word_alignment:
                word_alignment = word_alignment.replace( '>', '<')
                a_index_str, b_index_str = word_alignment.split( '<')
                points = self.onedir_weight
            a_index = int( a_index_str) + 1
            b_index = int( b_index_str) + 1
            ali_dict_key = ( a_index, b_index )
            ali_dict[ ali_dict_key ] = points
        return ali_dict

    def get_score( self, ali_dict, ali_dict_key, _, __):
        """ separated for overloading in FaUd_linker """
        return ali_dict[ ali_dict_key ]

    def build_score_table( self, a_frame_insts, b_frame_insts, word_alignments):
        ali_dict = self.create_ali_dict( word_alignments)

        score_table = []
        for a_frame_inst in a_frame_insts:
            table_row = []
            a_verb_index = a_frame_inst.verb_node_ord
            for b_frame_inst in b_frame_insts:
                b_verb_index = b_frame_inst.verb_node_ord
                ali_dict_key = ( a_verb_index, b_verb_index )
                score = self.get_score( ali_dict, ali_dict_key,
                                        a_frame_inst, b_frame_inst)
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
    def find_arg_pairs(a_frame_inst, b_frame_inst, word_alignments):
        tok_index_pairs = []
        for word_alignment in word_alignments:
            a_index_str, b_index_str = word_alignment.split('-')
            a_index = int(a_index_str)
            b_index = int(b_index_str)
            tok_index_pair = (a_index + 1, b_index + 1)
            tok_index_pairs.append(tok_index_pair)

        arg_pairs = []
        for a_index, a_token in enumerate(a_frame_inst.sent_tokens):
            for b_index, b_token in enumerate(b_frame_inst.sent_tokens):
                if a_token.is_frame_arg() and b_token.is_frame_arg() and \
                        (a_index, b_index) in tok_index_pairs:
                    a_frame_inst_arg = a_token.arg
                    b_frame_inst_arg = b_token.arg
                    frame_inst_arg_pair = (a_frame_inst_arg, b_frame_inst_arg)
                    arg_pairs.append(frame_inst_arg_pair)
        return arg_pairs
