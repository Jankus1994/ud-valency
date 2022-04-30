from udapi.block.valency.fa_linker import Fa_linker
from udapi.block.valency.ud_linker import Ud_linker
from udapi.block.valency.frame_extractor import Frame_extractor
#from udapi.block.valency.frame_pair import Frame_pair
from udapi.block.valency.control.bundle_record import Bundle_record

from udapi.core.block import Block

class Main_link_control( Block):
    def __init__( self, align_file_name="", a_lang_mark="", b_lang_mark="", **kwargs):
        """ overriden block method """
        super().__init__( **kwargs)
        if align_file_name != "":
            try:
                self.align_file = open( align_file_name, 'r')
            except FileNotFoundError:
                #print( "Cesta: " + os.path.dirname(os.path.realpath(__file__)))
                print( "ERROR: Alignment file " + align_file_name + " not found.")
                exit()

        self.a_frame_extractor = Frame_extractor()
        self.b_frame_extractor = Frame_extractor()
        self.a_lang_mark = a_lang_mark
        self.b_lang_mark = b_lang_mark
        self.fa_linker = Fa_linker()
        self.ud_linker = Ud_linker()

    def process_bundle( self, bundle):  # void
        """ overriden block method """
        bundle_record = Bundle_record()
        for tree_root in bundle.trees:
            if tree_root.zone == self.a_lang_mark:
                bundle_record.process_a_root( self.a_frame_extractor, tree_root)
            elif tree_root.zone == self.b_lang_mark:
                bundle_record.process_b_root( self.b_frame_extractor, tree_root)

        word_alignments = self.align_file.readline().split()
        bundle_record.perform_pairing( self.fa_linker, self.ud_linker, word_alignments)

        return bundle_record

                                                                                                            

