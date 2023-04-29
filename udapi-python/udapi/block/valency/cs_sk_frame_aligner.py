import logging

from frame_aligner import Frame_aligner
from frame_extractor import Frame_extractor
from cs_frame_extractor import Cs_frame_extractor

from ud_linker import Ud_linker
from fa_linker import Fa_linker
from faud_linker import FaUd_linker
from sim_linker import Sim_linker
from cs_sk_dist_measurer import Cs_Sk_dist_measurer
from dict_printer import Dict_printer

class Cs_Sk_frame_aligner( Frame_aligner):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)

        self.a_frame_extractor = Cs_frame_extractor()
        self.b_frame_extractor = Cs_frame_extractor()
        self.a_lang_mark = "cs"
        self.b_lang_mark = "sk"
        self.examiner.set_lang_marks( self.a_lang_mark, self.b_lang_mark)

        #sim_treshold = 20


        self.linker = None

    def after_process_document( self, doc):
        a_dict_of_verbs = self.a_frame_extractor.get_dict_of_verbs()
        #b_dict_of_verbs = self.b_frame_extractor.get_dict_of_verbs()
        #Dict_printer.print_verb_pairs( a_dict_of_verbs)
        super().after_process_document( doc)
