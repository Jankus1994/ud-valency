from cs_sk_frame_aligner import Cs_Sk_frame_aligner
from fral_testing import get_test_linker

class Cs_Sk_fral_tester( Cs_Sk_frame_aligner):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.linker = get_test_linker( self.run_num, self.a_lang_mark, self.b_lang_mark)