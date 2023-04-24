from fral_feats_examiner import Fral_feats_examiner
from cs_frame_extractor import Cs_frame_extractor
#from sk_frame_extractor import Sk_frame_extractor
from cs_sk_dist_measurer import Cs_Sk_dist_measurer

class Cs_Sk_fral_feats_examiner( Fral_feats_examiner):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.a_frame_extractor = Cs_frame_extractor()
        self.b_frame_extractor = Cs_frame_extractor()
        self.a_lang_mark = "cs"
        self.b_lang_mark = "sk"
        self.dist_measurer = Cs_Sk_dist_measurer( allow_substitution=True)