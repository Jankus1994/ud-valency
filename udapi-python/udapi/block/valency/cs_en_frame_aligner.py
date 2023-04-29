import logging
import sys

from frame_aligner import Frame_aligner
from cs_frame_extractor import Cs_frame_extractor
from en_frame_extractor import En_frame_extractor


class Cs_En_frame_aligner( Frame_aligner):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        
        #self.a_frame_extractor = En_frame_extractor()#Cs_frame_extractor()
        self.a_frame_extractor = Cs_frame_extractor()
        self.b_frame_extractor = En_frame_extractor()
        self.a_lang_mark = "cs"
        self.b_lang_mark = "en"
        self.examiner.set_lang_marks( self.a_lang_mark, self.b_lang_mark)
        self.cs_with_modals = []
        self.en_with_modals = []
        self.modal_pairs = []


    # def process_bundle( self, bundle):
    #     cs_frame_insts, en_frame_insts, frame_pairs = super().process_bundle( bundle)
    #     cs_with_modals = [ frame_inst for frame_inst in cs_frame_insts
    #                        if frame_inst is not None and frame_inst.has_modal ]
    #     self.cs_with_modals += cs_with_modals
    #     cs_lemmas = [ cs_frame_inst.type.verb_lemma for cs_frame_inst in cs_frame_insts ]
    #
    #     en_with_modals = [ frame_inst for frame_inst in en_frame_insts
    #                        if frame_inst is not None and frame_inst.has_modal ]
    #     self.en_with_modals += en_with_modals
    #     en_lemmas = [ en_frame_inst.type.verb_lemma for en_frame_inst in en_frame_insts ]
    #
    #     #print( cs_lemmas, en_lemmas)
    #     #print( len( cs_with_modals), len( en_with_modals))
    #     return
    #     for frame_pair in frame_pairs:
    #         a_frame_inst = frame_pair.a_frame_inst
    #         b_frame_inst = frame_pair.b_frame_inst
    #         if a_frame_inst.has_modal and b_frame_inst.has_modal:
    #             self.modal_pairs.append( frame_pair)
    #
    #
    #
    #
    # def after_process_document( self, doc):  # void
    #     """ overriden block method """
    #     print( "cs modals", len( self.cs_with_modals))
    #     print( "en modals", len( self.en_with_modals))
    #     print( "modal pairs", len( self.modal_pairs))
    #     super().after_process_document( doc)