from linker import Linker

class Comb_linker( Linker):
    def __init__( self, linkers, weights, ignore_nest_thresh=False, **kwargs):
        super().__init__( **kwargs)
        self.linkers = linkers
        self.weights = weights

        self.ignore_nest_thresh = ignore_nest_thresh

    def compute_frame_pair_score( self, a_frame_inst, b_frame_inst,
                                  a_b_ali_dict, b_a_ali_dict):
        score = 0
        for linker, weight in zip( self.linkers, self.weights):
            if weight == 0:
                continue

            compute_score_method = linker.compute_frame_pair_score_thresh
            if self.ignore_nest_thresh:
                compute_score_method = linker.compute_frame_pair_score

            score += weight * compute_score_method(
                    a_frame_inst, b_frame_inst, a_b_ali_dict, b_a_ali_dict)

        return score

    def compute_arg_pair_score( self, a_arg_inst, b_arg_inst,
                                 a_b_ali_dict, b_a_ali_dict):
        score = 0
        for linker, weight in zip( self.linkers, self.weights):
            if weight == 0:
                continue

            compute_score_method = linker.compute_arg_pair_score_thresh
            if self.ignore_nest_thresh:
                compute_score_method = linker.compute_arg_pair_score

            score += weight * compute_score_method(
                    a_arg_inst, b_arg_inst, a_b_ali_dict, b_a_ali_dict)

        return score  # TODO DIFFERENT WEIGHTS

    def get_params( self):
        return "Comb params:  fa_weight="  + str( self.weights[ 0 ]) + \
                ", ud_weight=" + str( self.weights[ 1 ]) + \
                ", sim_weight="  + str( self.weights[ 2 ]) + \
                ", threshold=" + str( self.threshold)