import sys
import pickle
from collections import defaultdict
from linker_evaluator import Linker_evaluator


class Gold_verb_record:
    def __init__( self, verb_str):
        token_ord, rest_str = verb_str.split( '-', 1)
        _, lemma = rest_str.split( ':')
        self.ord = token_ord
        self.lemma = lemma
        self.frame = None
        self.link = None


class Gold_arg_record:
    def __init__( self, arg_str):
        token_ord, func, form = arg_str.split( '-')
        self.ord = token_ord
        self.func = func
        self.form = form
        self.frame = None
        self.link = None


class Gold_frame_record:
    def __init__( self, verb_rec, arg_recs):
        self.verb_rec = verb_rec
        self.verb_rec.frame = self
        self.arg_recs = arg_recs
        for arg_rec in self.arg_recs:
            if arg_rec:
                arg_rec.frame = self
        self.link = None


# class Gold_verb_pair:
#     def __init__( self, a_verb_rec, b_verb_rec):
#         self.a_verb_rec = a_verb_rec
#         self.b_verb_rec = b_verb_rec
#
#         self.a_verb_rec.link = self
#         self.b_verb_rec.link = self
#
#
# class Gold_arg_pair:
#     def __init__( self, a_arg_rec, b_arg_rec):
#         self.a_arg_rec = a_arg_rec
#         self.b_arg_rec = b_arg_rec
#
#         self.a_arg_rec.link = self
#         self.b_arg_rec.link = self

class Gold_arg_pair:
    def __init__( self, a_arg_rec, b_arg_rec):
        self.a_arg_rec = a_arg_rec
        self.b_arg_rec = b_arg_rec

class Gold_frame_pair:
    def __init__( self, a_frame_rec, b_frame_rec, arg_pairs):
        self.a_frame_rec = a_frame_rec
        self.b_frame_rec = b_frame_rec
        self.arg_pairs = arg_pairs

        if self.a_frame_rec:
            self.a_frame_rec.link = self
        if self.b_frame_rec:
            self.b_frame_rec.link = self


class Gold_linker_evaluator( Linker_evaluator):
    result_value_num = 3

    def __init__( self, *args):
        super().__init__( *args)
        self.all_gold_frame_pairs = {}
        self.all_a_gold_frame_recs = {}
        self.all_b_gold_frame_recs = {}

    def prepare_data( self, gold_name):
        with open( gold_name, 'r') as gold_file:
            for i, line in enumerate( gold_file):
                sent_num = (i + 1) * 10
                gold_frame_pairs = []
                a_gold_frame_recs = []
                b_gold_frame_recs = []
                str_frame_links = line.rstrip( '\n').split( ';')
                for str_frame_link in str_frame_links:
                    if not str_frame_link:
                        continue
                    str_items_links = str_frame_link.split()
                    was_verb = False
                    a_verb_rec, b_verb_rec = None, None
                    a_args, b_args = [], []
                    gold_arg_pairs = []
                    for str_item_link in str_items_links:
                        assert '=' in str_item_link
                        a_item_str, b_item_str = str_item_link.split( '=')

                        if "-V:" in a_item_str and not was_verb:
                            a_verb_rec = Gold_verb_record( a_item_str)
                        if "-V:" in b_item_str and not was_verb:
                            b_verb_rec = Gold_verb_record( b_item_str)

                        if a_verb_rec or b_verb_rec and not was_verb:
                            was_verb = True
                            self.link_items( a_verb_rec, b_verb_rec)
                        else:
                            a_arg_rec = None if a_item_str == "X" else \
                                    Gold_arg_record( a_item_str)
                            a_args.append( a_arg_rec)
                            b_arg_rec = None if b_item_str == "X" else \
                                    Gold_arg_record( b_item_str)
                            b_args.append( b_arg_rec)
                            self.link_items( a_arg_rec, b_arg_rec)
                            gold_arg_pairs.append(
                                    Gold_arg_pair( a_arg_rec, b_arg_rec))
                    assert was_verb
                    a_frame_rec = None if not a_verb_rec else \
                            Gold_frame_record( a_verb_rec, a_args)
                    b_frame_rec = None if not b_verb_rec else \
                            Gold_frame_record( b_verb_rec, b_args)
                    self.link_items( a_frame_rec, b_frame_rec)
                    frame_pair = Gold_frame_pair(
                            a_frame_rec, b_frame_rec, gold_arg_pairs)

                    a_gold_frame_recs.append( a_frame_rec)
                    b_gold_frame_recs.append( b_frame_rec)
                    gold_frame_pairs.append( frame_pair)

                self.all_gold_frame_pairs[ sent_num ] = gold_frame_pairs
                self.all_a_gold_frame_recs[ sent_num ] = a_gold_frame_recs
                self.all_b_gold_frame_recs[ sent_num ] = b_gold_frame_recs

    @staticmethod
    def link_items( a_item, b_item):
        if a_item:
            a_item.link = b_item
        if b_item:
            b_item.link = a_item

    def load_frames_aligns_tuples( self):
        with open( self.tolink_name, 'rb') as tolink_file:
            frames_aligns_tuples, _ = pickle.load( tolink_file)
            return frames_aligns_tuples

    def save_sent_args_aligns_tuples( self, sent_args_aligns_tuples):
        sys.setrecursionlimit( 50000)
        with open( self.tolink_name + '_gold', 'wb') as tolink_gold_file:
            pickle.dump( sent_args_aligns_tuples, tolink_gold_file)

    def load_sent_args_aligns_tuples( self):
        with open( self.tolink_name + '_gold', 'rb') as tolink_gold_file:
            sent_args_aligns_tuples = pickle.load( tolink_gold_file)
            return sent_args_aligns_tuples


    # def find_best_linker( self, linkers, items_aligns_tuples, type="frames"):
    #     crossval_fold_num = 5
    #     fold_size = len( items_aligns_tuples) / crossval_fold_num
    #     for i in range( crossval_fold_num):
    #         # choosing best linker ~ tuning parameters
    #         linker_scores = defaultdict( lambda : [ 0 ] * self.result_value_num)
    #         sent_num = 0
    #         for items_aligns_tuple in items_aligns_tuples:
    #             sent_num += 1
    #             if sent_num % 10 != 0:
    #                 continue
    #             if i * 10 < sent_num <= i * 10 + fold_size:
    #                 continue
    #             print( "line", sent_num)
    #             a_items, b_items, a_b_ali_dict, b_a_ali_dict = items_aligns_tuple
    #             for linker in linkers:
    #
    #                 find_pairs = linker.find_frame_pairs
    #                 evaluate_pairs = self.evaluate_frame_pairs
    #                 if type == "args":
    #                     find_pairs = linker.find_arg_pairs
    #                     evaluate_pairs = self.evaluate_arg_pairs
    #
    #                 pairs = find_pairs( a_items, b_items, a_b_ali_dict, b_a_ali_dict)
    #                 result_vec = evaluate_pairs( pairs, a_items, b_items, sent_num)
    #                 sum_list = [ sum + result for result, sum
    #                              in zip( result_vec, linker_scores[ linker ]) ]
    #                 linker_scores[ linker ] = sum_list
    #
    #         best_linker, best_vals = self.choose_best_linker( linkers, items_aligns_tuples,
    #                                                           linker_scores)
    #
    #         # testing the chosen, best linker
    #         linker_scores = [ 0 ] * self.result_value_num
    #         sent_num = 0
    #         for items_aligns_tuple in items_aligns_tuples:
    #             if sent_num % 10 == 0 and i * 10 < sent_num <= i * 10 + fold_size:
    #                 a_items, b_items, a_b_ali_dict, b_a_ali_dict = items_aligns_tuple
    #                 find_pairs = best_linker.find_frame_pairs
    #                 evaluate_pairs = self.evaluate_frame_pairs
    #                 if type == "args":
    #                     find_pairs = best_linker.find_arg_pairs
    #                     evaluate_pairs = self.evaluate_arg_pairs
    #
    #                 pairs = find_pairs( a_items, b_items, a_b_ali_dict, b_a_ali_dict)
    #                 result_vec = evaluate_pairs( pairs, a_items, b_items, sent_num)
    #                 sum_list = [ sum + result for result, sum
    #                              in zip( result_vec, linker_scores) ]
    #                 linker_scores = sum_list
    #
    #         return best_linker, best_vals

    def choose_best_linker( self, linkers, use_count, linker_scores):
        best_score_avg = 0
        best_linker = linkers[ 0 ]
        best_vals = ( 0,) * 3
        for linker in linkers:
            plus_points, minus_points, score = linker_scores[ linker ]
            plus_points_avg = plus_points / use_count
            minus_points_avg = minus_points / use_count
            score_avg = score / use_count

            if score_avg > best_score_avg:
                best_score_avg = score_avg
                best_linker = linker
                best_vals = ( plus_points_avg, minus_points_avg, score_avg )

        return best_linker, best_vals

    def evaluate_frame_pairs( self, auto_frame_pairs, a_frame_insts, b_frame_insts, sent_num):
        if sent_num % 10 != 0:
            return
        plus_points, minus_points = 0, 0
        gold_frame_pairs = self.all_gold_frame_pairs[ sent_num ]
        a_gold_frame_recs = self.all_a_gold_frame_recs[ sent_num ]
        b_gold_frame_recs = self.all_b_gold_frame_recs[ sent_num ]

        for a_frame_inst in a_frame_insts:
            b_frame_inst = self.get_other_auto_frame( a_frame_inst, auto_frame_pairs)
            for a_gold_frame_rec in a_gold_frame_recs:
                if self.check_verb_agreement( a_frame_inst, a_gold_frame_rec):
                    b_gold_frame_rec = self.get_other_gold_frame( a_gold_frame_rec,
                                                                  gold_frame_pairs)
                    if self.check_verb_agreement( b_frame_inst, b_gold_frame_rec):
                        # both, None agreement and non-None agreement
                        plus_points += 1
                    else:
                        minus_points += 1
        for b_frame_inst in b_frame_insts:
            a_frame_inst = self.get_other_auto_frame( b_frame_inst, auto_frame_pairs)
            for b_gold_frame_rec in b_gold_frame_recs:
                if self.check_verb_agreement( b_frame_inst, b_gold_frame_rec):
                    a_gold_frame_rec = self.get_other_gold_frame( b_gold_frame_rec,
                                                                  gold_frame_pairs)
                    if a_frame_inst is None and a_gold_frame_rec is None:
                        plus_points += 1
                    elif not self.check_verb_agreement( a_frame_inst, a_gold_frame_rec):
                        minus_points += 1
                    # plus point for non-None agreement already counted
        if plus_points == 0 and minus_points == 0:
            score = 1
        else:
            score = plus_points / (plus_points + minus_points)
        return plus_points, minus_points, score


    def evaluate_arg_pairs( self, auto_arg_pairs, a_frame_inst, b_frame_inst, sent_num):
        if sent_num % 10 != 0:
            return
        plus_points, minus_points = 0, 0

        a_verb_ord = a_frame_inst.verb_node_ord
        b_verb_ord = b_frame_inst.verb_node_ord

        gold_frame_pairs = self.all_gold_frame_pairs[ sent_num ]
        gold_frame_pair = self.get_gold_frame_pair_by_ords(
                gold_frame_pairs, a_verb_ord, b_verb_ord)
        if gold_frame_pair:
            gold_arg_pairs = gold_frame_pair.arg_pairs
            a_gold_args = gold_frame_pair.a_frame_rec.arg_recs
            b_gold_args = gold_frame_pair.b_frame_rec.arg_recs

            for a_auto_arg in a_frame_inst.args:
                b_auto_arg = self.get_other_auto_arg( a_auto_arg, auto_arg_pairs)
                for a_gold_arg in a_gold_args:
                    if self.check_arg_agreement( a_auto_arg, a_gold_arg):
                        b_gold_arg = self.get_other_gold_arg(
                                a_gold_arg, gold_arg_pairs)
                        if self.check_arg_agreement( b_auto_arg, b_gold_arg):
                            # both, None agreement and non-None agreement
                            plus_points += 1
                        else:
                            minus_points += 1
            for b_auto_arg in b_frame_inst.args:
                a_auto_arg = self.get_other_auto_arg( b_auto_arg, auto_arg_pairs)
                for b_gold_arg in b_gold_args:
                    if self.check_arg_agreement( b_auto_arg, b_gold_arg):
                        a_gold_arg = self.get_other_gold_arg(
                                b_gold_arg, gold_arg_pairs)
                        if a_auto_arg is None and a_gold_arg is None:
                            plus_points += 1
                        elif not self.check_arg_agreement( a_auto_arg, a_gold_arg):
                            minus_points += 1
                        # plus point for non-None agreement already counted

        if plus_points == 0 and minus_points == 0:
            score = 1
        else:
            score = plus_points / (plus_points + minus_points)

        return plus_points, minus_points, score

    @staticmethod
    def get_gold_frame_pair_by_ords( gold_frame_pairs, auto_a_ord, auto_b_ord):
        for gold_frame_pair in gold_frame_pairs:
            a_frame_rec = gold_frame_pair.a_frame_rec
            b_frame_rec = gold_frame_pair.b_frame_rec
            if a_frame_rec and b_frame_rec:
                gold_a_ord = int( a_frame_rec.verb_rec.ord)
                gold_b_ord = int( b_frame_rec.verb_rec.ord)
                if auto_a_ord == gold_a_ord and auto_b_ord == gold_b_ord:
                    return gold_frame_pair
        return None

    @staticmethod
    def get_other_auto_frame( frame_inst, frame_pairs):
        for frame_pair in frame_pairs:
            if frame_inst is frame_pair.a_frame_inst:
                return frame_pair.b_frame_inst
            if frame_inst is frame_pair.b_frame_inst:
                return frame_pair.a_frame_inst
        return None

    @staticmethod
    def get_other_gold_frame( frame_rec, frame_pairs):
        for frame_pair in frame_pairs:
            if frame_rec is frame_pair.a_frame_rec:
                return frame_pair.b_frame_rec
            if frame_rec is frame_pair.b_frame_rec:
                return frame_pair.a_frame_rec
        assert False

    @staticmethod
    def check_verb_agreement( auto_frame_inst, gold_frame_rec):
        if auto_frame_inst is None and gold_frame_rec is None:
            return True
        if auto_frame_inst is None or gold_frame_rec is None:
            return False
        auto_ord = auto_frame_inst.verb_node_ord
        gold_ord = int( gold_frame_rec.verb_rec.ord)
        return auto_ord == gold_ord

    @staticmethod
    def get_other_auto_arg( auto_arg, arg_pairs):
        for arg_pair in arg_pairs:
            if auto_arg is arg_pair[ 0 ]:
                return arg_pair[ 1 ]
            if auto_arg is arg_pair[ 1 ]:
                return arg_pair[ 0 ]
        return None

    @staticmethod
    def get_other_gold_arg( gold_arg, arg_pairs):
        for arg_pair in arg_pairs:
            if gold_arg is arg_pair.a_arg_rec:
                return arg_pair.b_arg_rec
            if gold_arg is arg_pair.b_arg_rec:
                return arg_pair.a_arg_rec
        return None

    @staticmethod
    def check_arg_agreement( auto_arg, gold_arg):
        if auto_arg is None and gold_arg is None:
            return True
        if auto_arg is None or gold_arg is None:
            return False
        if auto_arg.token.is_elided() and gold_arg.ord == "_":
            return True
        if auto_arg.token.is_elided() or gold_arg.ord == "_":
            return False
        auto_ord = auto_arg.token.ord
        gold_ord = int( gold_arg.ord)
        return auto_ord == gold_ord

    def print_results( self, linker_vals_tuples, frams_args):
        print( "=====")
        print( "RESULT OF EVALUATION: ", frams_args)
        _, base_results = linker_vals_tuples[ 0 ]
        print( "BASE")
        print( "", "PLS avg", round( base_results[ 0 ], 2))
        print( "", "MNS avg", round( base_results[ 1 ], 2))
        print( "", "SCR avg", round( base_results[ 2 ] * 100, 2), "%")
        for linker, vals in linker_vals_tuples:
            params = linker.get_params()
            print( params)
            improve = self.compute_improvement( base_results[ 0 ] * 100, vals[ 0 ] * 100)
            print( "", "PLS avg", round( vals[ 0 ], 2), "impr", improve)
            improve = self.compute_improvement( base_results[ 1 ] * 100, vals[ 1 ] * 100)
            print( "", "MNS avg", round( vals[ 1 ], 2), "impr", improve)
            improve = self.compute_improvement( base_results[ 2 ] * 100, vals[ 2 ] * 100)
            print( "", "SCR avg", round( vals[ 2 ] * 100, 2), "%", "impr", improve)

if __name__ == "__main__":
    tolink_name = sys.argv[ 1 ]
    gold_links_name = sys.argv[ 2 ]
    eval_run = sys.argv[ 3 ]

    linker_evaluator = Gold_linker_evaluator( tolink_name)
    linker_evaluator.prepare_data( gold_links_name)
    if eval_run == "feval":
        linker_evaluator.evaluate_frame_linking()
    elif eval_run == "aeval":
        linker_evaluator.evaluate_arg_linking()