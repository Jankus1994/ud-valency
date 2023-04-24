from fral_feats_examiner import Fral_feats_examiner
from cs_frame_extractor import Cs_frame_extractor
from en_frame_extractor import En_frame_extractor

class Cs_En_fral_feats_examiner( Fral_feats_examiner):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.a_frame_extractor = Cs_frame_extractor()
        self.b_frame_extractor = En_frame_extractor()
        self.a_lang_mark = "cs"
        self.b_lang_mark = "en"