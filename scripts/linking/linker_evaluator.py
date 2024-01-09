import pickle, sys, itertools
from collections import defaultdict

sys.path.append( '../udapi-python/udapi/block/valency')
from base_linker import Base_linker
from fa_linker import Fa_linker
from ud_linker import Ud_linker
from sim_linker import Sim_linker
from comb_linker import Comb_linker
from dist_measurer import Dist_measurer
from cs_sk_dist_measurer import Cs_Sk_dist_measurer

class Linker_evaluator:
    result_value_num = 0

    def __init__( self, tolink_name):
        self.tolink_name = tolink_name

    def prepare_data( self, *args):
        return

    def generate_fa_linkers( self, weight_range):
        return [ Fa_linker( weight) for weight in weight_range ]

    def generate_ud_linkers( self, threshold_range, weight_range):
        param_ranges = [ weight_range ] * 6 + [ threshold_range ]
        param_permutations = list( itertools.product( *param_ranges))
        generated_linkers = []
        for params_permutation in param_permutations:
            param_weights = params_permutation[ :6 ]
            threshold = params_permutation[ 6 ]

            ud_linker = Ud_linker( params_weights=param_weights,
                                   threshold=threshold)
            generated_linkers.append( ud_linker)
        return generated_linkers

    def generate_sim_linkers( self, threshold_range, allow_substs, measurers):
        param_ranges = [ threshold_range ] + [ allow_substs ] + [ measurers ]
        params_permutations = list( itertools.product( *param_ranges))
        generated_linkers = []
        for params_permutation in params_permutations:
            threshold, allow_subst, measurer = params_permutation
            sim_linker = Sim_linker( measurer_features=( measurer,
                                                         { "allow_substitution": allow_subst }),
                                threshold=threshold)
            generated_linkers.append( sim_linker)
        return generated_linkers

    def generate_comb_linkers( self, base_linker, fa_linker, ud_linker, sim_linker):
        weight_range = [ 0, 1, 2 ]
        threshold_range = [ 0, 1, 2 ]
        ignore_nest_threshs = [ True, False ]
        param_ranges = [ weight_range ] * 4 + [ threshold_range ] + \
                       [ ignore_nest_threshs ]
        params_permutations = list( itertools.product( *param_ranges))

        generated_linkers = []
        for params_permutation in params_permutations:
            linker_weights = params_permutation[ :4 ]
            threshold = params_permutation[ 4 ]
            ignore_nest_thresh = params_permutation[ 5 ]

            comb_linker = Comb_linker( [ base_linker, fa_linker, ud_linker, sim_linker ],
                                       linker_weights, threshold=threshold,
                                       ignore_nest_thresh=ignore_nest_thresh)
            generated_linkers.append( comb_linker)
        return generated_linkers

    def print_results( self, linker_vals_tuples, frams_args): # TODO dat len do vallexoveho
        # TODO vymazat tie avg hodnoty, su na nic
        val_names = "PRC tot", "REC tot", "F1S tot"
        print( "=====")
        print( "RESULT OF EVALUATION: ", frams_args)
        _, base_results = linker_vals_tuples[ 0 ]
        print( "BASE")
        for val_name, val in zip( val_names, base_results):
            print( "", val_name, round( val * 100, 2))
        for linker, vals in linker_vals_tuples[ 1: ]:
            params = linker.get_params()
            print( params)
            for val_name, val, base_val in zip( val_names, vals, base_results):
                improve = self.compute_improvement( base_val * 100, val * 100)
                print( "", val_name, round( val * 100, 2), "impr", improve)

    @staticmethod
    def compute_improvement( base_val, test_val):
        resid = 100 - base_val
        over = test_val - base_val
        improve = 0
        if resid == 0 and over < 0:
            improve = "-INF"
        elif resid > 0:
            improve = round( 100 / resid * over, 2)
        return improve


    def load_frames_aligns_tuples( self):
        return []

    def save_sent_args_aligns_tuples( self, sent_args_aligns_tuples):
        return

    def load_sent_args_aligns_tuples( self):
        return []

    def evaluate_frame_linking( self):
        frames_aligns_tuples = self.load_frames_aligns_tuples()

        linker_vals_tuples = []

        base_linker = Base_linker()
        linker_vals_tuples.append(
                self.find_best_frame_linker( [ base_linker ], frames_aligns_tuples))

        # fa_weight_range = [ 0, 0.5, 1 ]
        # fa_linkers = self.generate_fa_linkers( fa_weight_range)
        # linker_vals_tuples.append(
        #         self.find_best_frame_linker( fa_linkers, frames_aligns_tuples))

        ud_threshold_range = [ 0.2, 0.35, 0.5 ]
        ud_weight_range = [ 0, 0.5, 1 ]
        ud_linkers = self.generate_ud_linkers( ud_threshold_range, ud_weight_range)
        linker_vals_tuples.append(
                self.find_best_frame_linker( ud_linkers, frames_aligns_tuples))

        # sim_threshold_range = [ 0.05, 0.1, 0.15 ]
        # sim_allow_substs = [ True, False ]
        # sim_measurers = [ Dist_measurer, Cs_Sk_dist_measurer ]
        # sim_linkers = self.generate_sim_linkers( sim_threshold_range,
        #                                          sim_allow_substs, sim_measurers)
        # linker_vals_tuples.append(
        #         self.find_best_frame_linker( sim_linkers, frames_aligns_tuples))
        #
        # best_linkers = [ best_linker for best_linker, _  in linker_vals_tuples ]
        # comb_linkers = self.generate_comb_linkers( *best_linkers)
        # best_comb_linker, best_comb_vals = \
        #         self.find_best_frame_linker( comb_linkers, frames_aligns_tuples)
        # linker_vals_tuples.append( ( best_comb_linker, best_comb_vals ))

        self.print_results( linker_vals_tuples, "FRAMES")
        # exit()
        best_comb_linker = linker_vals_tuples[ 0 ][ 0 ]

        # running the chosen linker on frames again
        sent_args_aligns_tuples = []
        count = 0
        sent_id = 0
        for frames_aligns_tuple in frames_aligns_tuples:

            args_aligns_tuples = []
            frame_pairs = best_comb_linker.find_frame_pairs( *frames_aligns_tuple)
            _, _, a_b_ali_dict, b_a_ali_dict = frames_aligns_tuple
            sent_id += 1
            if sent_id % 10 == 0:
                count += len( frame_pairs)
            for frame_pair in frame_pairs:
                a_frame_inst = frame_pair.a_frame_inst
                b_frame_inst = frame_pair.b_frame_inst
                args_aligns_tuple = a_frame_inst, b_frame_inst, \
                                    a_b_ali_dict, b_a_ali_dict
                args_aligns_tuples.append( args_aligns_tuple)
            sent_args_aligns_tuples.append( args_aligns_tuples)

        self.save_sent_args_aligns_tuples( sent_args_aligns_tuples)

    def evaluate_arg_linking( self):
        sent_args_aligns_tuples = self.load_sent_args_aligns_tuples()

        linker_vals_tuples = []

        fa_weight_range = [ 0, 0.5, 1 ]
        fa_linkers = self.generate_fa_linkers( fa_weight_range)
        linker_vals_tuples.append(
                self.find_best_arg_linker( fa_linkers, sent_args_aligns_tuples))

        # ud_threshold_range = [ 0.2, 0.35, 0.5 ]
        # ud_weight_range = [ 1.0 ]
        # ud_linkers = self.generate_ud_linkers( ud_threshold_range, ud_weight_range)
        # linker_vals_tuples.append(
        #         self.find_best_arg_linker( ud_linkers, sent_args_aligns_tuples))
        #
        # sim_threshold_range = [ 0.05, 0.1, 0.15 ]
        # sim_allow_substs = [ True, False ]
        # sim_measurers = [ Dist_measurer, Cs_Sk_dist_measurer ]
        # sim_linkers = self.generate_sim_linkers( sim_threshold_range,
        #                                          sim_allow_substs, sim_measurers)
        # linker_vals_tuples.append(
        #         self.find_best_arg_linker( sim_linkers, sent_args_aligns_tuples))
        #
        # best_linkers = [ best_linker for best_linker, _  in linker_vals_tuples ]
        # comb_linkers = self.generate_comb_linkers( *best_linkers)
        # linker_vals_tuples.append(
        #         self.find_best_arg_linker( comb_linkers, sent_args_aligns_tuples))

        self.print_results( linker_vals_tuples, "ARGUMENTS")

    def find_best_frame_linker( self, linkers, frames_aligns_tuples):
        linker_scores = defaultdict( lambda : [ 0 ] * self.result_value_num)
        sent_num = 0
        use_count = 0
        for frames_aligns_tuple in frames_aligns_tuples:
            sent_num += 1
            if sent_num % 10 != 0:  # toto len pre gold! TODO
                continue
            print( "line", sent_num)
            use_count += 1
            a_frames, b_frames, a_b_ali_dict, b_a_ali_dict = frames_aligns_tuple
            for linker in linkers:
                frame_pairs = linker.find_frame_pairs(
                        a_frames, b_frames, a_b_ali_dict, b_a_ali_dict)
                result_vec = self.evaluate_frame_pairs(
                        frame_pairs, a_frames, b_frames, sent_num)
                sum_list = [ sum + result for result, sum
                             in zip( result_vec, linker_scores[ linker ]) ]
                linker_scores[ linker ] = sum_list

        print( "***", use_count)
        best_linker, best_vals = self.choose_best_linker( linkers, use_count,
                                                          linker_scores)
        return best_linker, best_vals

    def find_best_arg_linker( self, linkers, sent_args_aligns_tuples):
        linker_scores = defaultdict( lambda : [ 0 ] * self.result_value_num)
        sent_num = 0
        use_count = 0
        for args_aligns_tuples in sent_args_aligns_tuples:
            sent_num += 1
            if sent_num % 10 != 0:  # toto len pre gold! TODO
                continue
            print( "line", sent_num)
            for args_aligns_tuple in args_aligns_tuples:
                use_count += 1
                a_frame_inst, b_frame_inst, a_b_ali_dict, b_a_ali_dict = args_aligns_tuple
                for linker in linkers:
                    arg_pairs = linker.find_arg_pairs(
                            a_frame_inst.args, b_frame_inst.args, a_b_ali_dict, b_a_ali_dict)
                    result_vec = self.evaluate_arg_pairs(
                            arg_pairs, a_frame_inst, b_frame_inst, sent_num)
                    sum_list = [ sum + result for result, sum
                                 in zip( result_vec, linker_scores[ linker ]) ]
                    linker_scores[ linker ] = sum_list

        print( "***", use_count)
        best_linker, best_vals = self.choose_best_linker( linkers, use_count,
                                                          linker_scores)
        return best_linker, best_vals

    def choose_best_linker( self, linkers, items_aligns_tuples, linker_scores):
        best_linker = linkers[ 0 ]
        best_values = ( 0, 0)
        return best_linker, best_values

    def evaluate_frame_pairs( self, frame_pairs, a_frame_insts, b_frame_insts, sent_num):
        return 0, 0, 0, 0, 0, 0

    def evaluate_arg_pairs( self, arg_pairs, a_arg_insts, b_arg_insts, sent_num):
        return 0, 0, 0, 0, 0, 0

