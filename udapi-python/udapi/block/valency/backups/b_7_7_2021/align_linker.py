from udapi.block.valency.linker import *
from udapi.block.valency.frame_pair import Frame_pair

class Align_linker( Linker):
    #def __init__( self, a_lang_mark, b_lang_mark):

    def find_frame_pairs( self, a_frame_insts, b_frame_insts, word_alignments):
        a_b_ali_dict = {}
        b_a_ali_dict = {}
        for word_alignment in word_alignments:
            a_index_str, b_index_str = word_alignment.split( '-')
            #try:
            a_index = int( a_index_str)
            b_index = int( b_index_str)
            #except:
            #    print( "conv ERROR")
            #    exit()
            a_b_ali_dict[ a_index + 1 ] = b_index + 1
            #b_a_ali_dict[ b_index + 1 ] = a_index + 1

        # the frame alignment procedure is in itself dependent on a dictionary
        # direction, but as we suppose the world alignment is done by a symmetric
        # combination (intersection or union) of both one-direction alignments
        # both runs of the framec alignment procedure would lead to the same result
        frame_pairs = self._frame_alignment( a_frame_insts, b_frame_insts, a_b_ali_dict)
        return frame_pairs
    
    def _frame_alignment( self, frst_frame_insts, scnd_frame_insts, \
                            frst_scnd_ali_dict):  # void
        """ called from find_frame_pairs
        aligns frame types and frame instances of two languages
        the alignment depends on a given word alignment dictionary
        which is either a->b or b->a
        so here are labels "frst" and "scnd" used instead
        """
        frame_inst_pairs = []
        # aligning frame instances
        for frst_frame_inst in frst_frame_insts:
            frst_frame_type = frst_frame_inst.get_type()
            frst_verb_index = frst_frame_inst.get_verb_node_ord()
            #print( frst_verb_index, frst_frame_inst.verb_node.form)
            try:
                scnd_verb_index = frst_scnd_ali_dict[ frst_verb_index ]
            except KeyError:  # this token was not aligned
                #print( "    OOOO")
                continue
            for scnd_frame_inst in scnd_frame_insts:
                if scnd_frame_inst.get_verb_node_ord() == scnd_verb_index:
                    chosen_scnd_frame_inst = scnd_frame_inst
                    break
            else:  # the token was not aligned to any verb token
                #print( "    XXXX")
                continue

            # unmatched instances will have "frame_type_link" attribute still None
            scnd_frame_type = chosen_scnd_frame_inst.get_type()

            #frame_pair = Frame_pair( frst_frame_type, scnd_frame_type, \
            #                        frst_frame_inst, chosen_scnd_frame_inst)
            frame_inst_pair = Frame_pair( frst_frame_inst, chosen_scnd_frame_inst)
            frame_inst_pairs.append( frame_inst_pair)
        return frame_inst_pairs

    def find_arg_pairs( self, a_frame_inst, b_frame_inst, word_alignments):
        tok_index_pairs = []
        for word_alignment in word_alignments:
            a_index_str, b_index_str = word_alignment.split( '-')
            a_index = int( a_index_str)
            b_index = int( b_index_str)
            tok_index_pair = ( a_index + 1, b_index + 1 )
            tok_index_pairs.append( tok_index_pair)

        arg_pairs = []
        for a_index, a_token in enumerate( a_frame_inst.sent_tokens):
            for b_index, b_token in enumerate( b_frame_inst.sent_tokens):
                if a_token.is_frame_arg() and b_token.is_frame_arg() and \
                        ( a_index, b_index ) in tok_index_pairs:
                    a_frame_inst_arg = a_token.get_arg()
                    b_frame_inst_arg = b_token.get_arg()
                    frame_inst_arg_pair = ( a_frame_inst_arg, b_frame_inst_arg )
                    arg_pairs.append( frame_inst_arg_pair)
        return arg_pairs

