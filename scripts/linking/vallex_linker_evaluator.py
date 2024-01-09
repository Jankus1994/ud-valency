import sys
import pickle
from collections import defaultdict
import xml.etree.ElementTree as et
from linker_evaluator import Linker_evaluator
from vallex.e_vallex_matcher import E_vallex_matcher
from vallex.cc_vallex_matcher import Cc_vallex_matcher

class Vallex_linker_evaluator( Linker_evaluator):
    result_value_num = 6

    def prepare_data( self, cs_val_name, en_val_name, val_align_name):
        with open( self.tolink_name, 'rb') as tolink_file:
            frames_aligns_tuples, a_b_dicts_of_verbs = pickle.load( tolink_file)
            self.a_dict_of_verbs, self.b_dict_of_verbs = a_b_dicts_of_verbs


        with open( cs_val_name, 'rb') as cs_val_file, \
                open( en_val_name, 'rb') as en_val_file:
            cs_val_dict = pickle.load( cs_val_file)
            en_val_dict = pickle.load( en_val_file)

            cs_vallex_matcher = Cc_vallex_matcher( self.a_dict_of_verbs, cs_val_dict)
            cs_vallex_matcher.match_frames()
            _, cs_id_val_dict = cs_vallex_matcher.get_matched()

            en_vallex_matcher = E_vallex_matcher( self.b_dict_of_verbs, en_val_dict)
            en_vallex_matcher.match_frames()
            _, en_id_val_dict = en_vallex_matcher.get_matched()

            self.cs_en_val_frame_pairs = \
                    self.get_val_frame_pairs( cs_id_val_dict, en_id_val_dict,
                                              val_align_name)

            tolink_data = frames_aligns_tuples, set( self.cs_en_val_frame_pairs)
            sys.setrecursionlimit( 50000)
            with open( self.tolink_name + '_val1', 'wb') as tolink_val1_file:
                pickle.dump( tolink_data, tolink_val1_file)


    def get_val_frame_pairs( self, cs_id_val_frame_dict, en_id_val_frame_dict, align_filename):
        cs_en_val_frame_pairs = []

        tree = et.ElementTree( file=align_filename)
        root = tree.getroot()
        en_frame_elems = root.findall( ".//en_frame")
        for en_frame_elem in en_frame_elems:
            en_frame_id = en_frame_elem.attrib[ "en_id" ]
            en_frame = en_id_val_frame_dict[ en_frame_id ]
            frame_pairs = en_frame_elem.findall( "frame_pair")
            for frame_pair_elem in frame_pairs:
                cs_frame_id = frame_pair_elem.attrib[ "cs_id" ]
                cs_frame = cs_id_val_frame_dict[ cs_frame_id ]
                frame_pair = ( cs_frame, en_frame )
                cs_en_val_frame_pairs.append( frame_pair)
                self.link_val_args( en_frame, cs_frame, frame_pair_elem)

        return cs_en_val_frame_pairs

    @staticmethod
    def link_val_args( en_frame, cs_frame, frame_pair_elem):
        en_args = { arg.functor: arg for arg in en_frame.arguments }
        cs_args = { arg.functor: arg for arg in cs_frame.arguments }

        slots = frame_pair_elem.findall( ".//slot")
        for slot in slots:
            en_functor = slot.attrib[ "en_functor" ]
            cs_functor = slot.attrib[ "cs_functor" ]

            en_arg = en_args[ en_functor ] if en_functor in en_args else None
            cs_arg = cs_args[ cs_functor ] if cs_functor in cs_args else None

            if en_arg is not None and cs_arg is not None and \
                    en_functor != "---" and cs_functor != "---":
                en_arg.align_val_arg( cs_arg)
                cs_arg.align_val_arg( en_arg)

    def load_frames_aligns_tuples( self):
        with open( self.tolink_name + '_val1', 'rb') as tolink_val1_file:
            frames_aligns_tuples, self.cs_en_val_frame_pairs = pickle.load( tolink_val1_file)
            return frames_aligns_tuples

    def save_sent_args_aligns_tuples( self, sent_args_aligns_tuples):
        sys.setrecursionlimit( 50000)
        with open( self.tolink_name + '_val2', 'wb') as tolink_val2_file:
            data_to_save = sent_args_aligns_tuples, self.cs_en_val_frame_pairs
            pickle.dump( data_to_save, tolink_val2_file)

    def load_sent_args_aligns_tuples( self):
        with open( self.tolink_name + '_val2', 'rb') as tolink_val2_file:
            loaded_data = pickle.load( tolink_val2_file)
            sent_args_aligns_tuples, self.cs_en_val_frame_pairs = loaded_data
            return sent_args_aligns_tuples

    def evaluate_frame_pairs( self, frame_pairs, a_frame_insts, b_frame_insts, _):
        sel, rel, com = 0, 0, 0
        true_frame_pairs = [ ( fp.a_frame_inst, fp.b_frame_inst ) for
                             fp in frame_pairs ]
        for a_frame_inst in a_frame_insts:
            for b_frame_inst in b_frame_insts:
                frame_pair = ( a_frame_inst, b_frame_inst )
                is_selected = frame_pair in true_frame_pairs
                sel += int( is_selected)

                a_frame_type = a_frame_inst.type
                b_frame_type = b_frame_inst.type
                a_val_frames = set( a_frame_type.matched_frames)
                b_val_frames = set( b_frame_type.matched_frames)
                is_relevant = False
                for a_val_frame in a_val_frames:
                    for b_val_frame in b_val_frames:
                        val_pair = ( a_val_frame, b_val_frame )
                        if val_pair in self.cs_en_val_frame_pairs: # TODO u argov to nepotrebujes?
                            is_relevant = True
                            break
                    if is_relevant:
                        break
                rel += int( is_relevant)

                is_common = is_selected and is_relevant
                com += int( is_common)
        prc, rec, fsc = self.compute_prf( sel, rel, com)
        return sel, rel, com, prc, rec, fsc

    def evaluate_arg_pairs( self, arg_pairs, a_frame_inst, b_frame_inst, _):
        a_arg_insts = a_frame_inst.args
        b_arg_insts = b_frame_inst.args
        sel, rel, com = 0, 0, 0
        for a_arg_inst in a_arg_insts:
            for b_arg_inst in b_arg_insts:
                arg_pair = ( a_arg_inst, b_arg_inst )
                is_selected = arg_pair in arg_pairs
                sel += int( is_selected)

                a_arg_type = a_arg_inst.type
                b_arg_type = b_arg_inst.type
                a_val_args = set( a_arg_type.matched_args)
                b_val_args = set( b_arg_type.matched_args)
                is_relevant = False
                for a_val_arg in a_val_args:
                    for b_val_arg in b_val_args:
                        a_b_linked = b_val_arg in a_val_arg.aligned_val_args
                        b_a_linked = a_val_arg in b_val_arg.aligned_val_args
                        if a_b_linked and b_a_linked:
                            is_relevant = True
                            break
                    if is_relevant:
                        break
                rel += int( is_relevant)

                is_common = is_selected and is_relevant
                com += int( is_common)
        prc, rec, fsc = self.compute_prf( sel, rel, com)
        return sel, rel, com, prc, rec, fsc

    def choose_best_linker( self, linkers, use_count, linker_scores):
        best_fsc = 0
        best_linker = linkers[ 0 ]
        best_vals = ( 0,) * 6
        for linker in linkers:
            sel_sum, rel_sum, com_sum, prc_sum, rec_sum, fsc_sum = linker_scores[ linker ]
            prc_tot, rec_tot, fsc_tot = self.compute_prf( sel_sum, rel_sum, com_sum)
            # prc_avg = prc_sum / use_count
            # rec_avg = rec_sum / use_count
            # fsc_avg = fsc_sum / use_count

            # act_fsc = ( fsc_tot + fsc_avg ) / 2
            if fsc_tot > best_fsc:
                # best_fsc = act_fsc
                best_fsc = fsc_tot
                best_linker = linker
                best_vals = ( prc_tot, rec_tot, fsc_tot )
        print( linker_scores[ best_linker ])

        return best_linker, best_vals

    @staticmethod
    def compute_prf( sel, rel, com):
        if sel == 0 and rel == 0:
            prc, rec, fsc = 1, 1, 1
        else:
            prc = com / sel if sel != 0 else 0
            rec = com / rel if rel != 0 else 0
            fsc = 2 * prc * rec / ( prc + rec ) if com != 0 else 0
        return prc, rec, fsc



if __name__ == "__main__":
    tolink_name = sys.argv[ 1 ]
    cs_val_name = sys.argv[ 2 ]
    en_val_name = sys.argv[ 3 ]
    val_align_name = sys.argv[ 4 ]
    eval_run = sys.argv[ 5 ]
    # eval_type = sys.argv[ 6 ]
    #
    # linker_evaluator_class = None
    # if eval_type == "vallex":
    linker_evaluator_class = Vallex_linker_evaluator
    # elif eval_type == "gold":
    #     linker_evaluator_class = Gold_linker_evaluator
    # else:
    #     print( "Incorrect evaluator specified (vallex/gold)", file=sys.stderr)
    #     exit()

    linker_evaluator = linker_evaluator_class( tolink_name=tolink_name)
    if eval_run == "prep":
        linker_evaluator.prepare_data( cs_val_name=cs_val_name, en_val_name=en_val_name,
                                       val_align_name=val_align_name)
    elif eval_run == "feval":
        linker_evaluator.evaluate_frame_linking()
    elif eval_run == "aeval":
        linker_evaluator.evaluate_arg_linking()