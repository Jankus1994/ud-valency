from ud_linker import *
from fa_linker import *

class FaUd_linker( Fa_linker, Ud_linker):
    def get_score( self, ali_dict, ali_dict_key, a_frame_inst, b_frame_inst):
        points = 4 * super().get_score( ali_dict, ali_dict_key,
                                        a_frame_inst, b_frame_inst)
        points += self.compute_pair_score( a_frame_inst, b_frame_inst)
        return points

