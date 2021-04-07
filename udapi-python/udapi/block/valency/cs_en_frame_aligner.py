import logging

from udapi.block.valency.frame_aligner import Frame_aligner
from udapi.block.valency.cs_module import Cs_frame_extractor
from udapi.block.valency.en_module import En_frame_extractor

class Cs_En_frame_aligner( Frame_aligner):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        
        self.a_frame_extractor = En_frame_extractor()#Cs_frame_extractor()
        self.b_frame_extractor = En_frame_extractor()
        self.a_lang_mark = "cs"
        self.b_lang_mark = "en"
