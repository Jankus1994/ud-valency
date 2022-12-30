"""
child class of udapi block
processes connlu file with parallel senteces in 2 languages
and simultanously reads word alignment
produces vallency dictionary and saves it into a pickle file
"""
import logging
import pickle
import sys
#import os

from udapi.core.block import Block
from frame_extractor import Frame_extractor
from link_structures import Frame_type_link
from linker import Linker
from extraction_finalizer import Extraction_finalizer
#from obl_examiner import Obl_examiner
from modal_examiner import Modal_examiner
from ud_linker import Ud_linker
from fa_linker import Fa_linker
from faud_linker import FaUd_linker
from sim_linker import Sim_linker
from dist_measurer import Dist_measurer

class Frame_aligner( Block):
    #def __init__( self, align_file_name="", output_folder="", output_name="",
    #              obl_ratio_limit="0.5", min_obl_inst_num=2, **kwargs):
    def __init__( self, run_num=0, align_file_name="", output_folder="", output_name="", **kwargs):
        """ overriden block method """
        super().__init__( **kwargs)

        self.run_num = run_num
        self.align_file = None
        self.output_folder = output_folder
        self.output_name = output_name
        #self.obl_ratio_limit = float( obl_ratio_limit)
        #self.min_obl_inst_num = int( min_obl_inst_num)

        self.linker = Linker()  # !!!

        sim_treshold = 5

        # run_dict = { 0: Fa_linker( incl_onedir=True),
        #              1: Fa_linker( incl_onedir=False),
        #              2: Ud_linker(),
        #              3: FaUd_linker( incl_onedir=True),
        #              4: FaUd_linker( incl_onedir=False),
        #              5: Sim_linker( Dist_measurer( allow_substitution=True), sim_treshold),
        #              6: Sim_linker( Dist_measurer( allow_substitution=False), sim_treshold)}
        # self.linker = run_dict[ self.run_num ]

        if align_file_name != "":
            try:
                self.align_file = open( align_file_name, 'r')
            except FileNotFoundError:
                #print( "Cesta: " + os.path.dirname(os.path.realpath(__file__)))
                print( "ERROR: Alignment file " + align_file_name + " not found.")
                exit()

        #self.a_and_b = 0
        #self.a_only = 0
        #self.b_only = 0
        #self.direction = 0 # 0 .. both, 1 .. a -> b, 2 .. b -> a

        # to be overloaded
        self.a_frame_extractor = Frame_extractor()
        self.b_frame_extractor = Frame_extractor()
        self.a_lang_mark = ""
        self.b_lang_mark = ""
        self.examiner = Modal_examiner()

    def process_document( self, document):
        #bundles_num = len( document.bundles)
        #print( bundles_num)
        super().process_document( document)

    def process_bundle( self, bundle):  # void
        """ overriden Block method """
        #logging.info( "bundle id: " + str( bundle.bundle_id))
        a_frame_insts = []
        b_frame_insts = []
        for tree_root in bundle.trees:
            if tree_root.zone == self.a_lang_mark:
                a_frame_insts = \
                        self.a_frame_extractor.process_tree( tree_root)
                self.examiner.examine_sentence( tree_root, self.a_lang_mark)
            elif tree_root.zone == self.b_lang_mark:
                b_frame_insts = \
                        self.b_frame_extractor.process_tree( tree_root)
                self.examiner.examine_sentence( tree_root, self.b_lang_mark)
        word_alignments = self.align_file.readline().split()
        #word_alignments = []

        frame_pairs = self.linker.find_frame_pairs( a_frame_insts, b_frame_insts,
                                                    word_alignments)
        a_verbs = ','.join( [ inst.type.verb_lemma for inst in a_frame_insts ])
        b_verbs = ','.join( [ inst.type.verb_lemma for inst in b_frame_insts ])
        #verb_pairs = '|'.join( [ frame_pair[0].a_frame_type.verb_lemma+'-'+frame_pair[0].b_frame_type.verb_lemma+'-'+str(frame_pair[1])
        #               for frame_pair in frame_pairs ])
        verb_pairs = '|'.join( [ frame_pair.a_frame_type.verb_lemma+'-'+frame_pair.b_frame_type.verb_lemma
                       for frame_pair in frame_pairs ])
        print( len( a_frame_insts), len( b_frame_insts), len( frame_pairs),
               a_verbs, b_verbs, verb_pairs, bundle.bundle_id, word_alignments, sep='\t')
        #return [], [], []

        for frame_pair in frame_pairs:
            # linking frame types
            # if the frame type link does not exist yet, create one
            a_frame_type = frame_pair.a_frame_type
            b_frame_type = frame_pair.b_frame_type
            a_b_frame_type_link = a_frame_type.find_link_with( b_frame_type)
                    # could be done the other way around: b_frame.find( frst_frame)
            if a_b_frame_type_link is None:
                a_b_frame_type_link = Frame_type_link( a_frame_type, b_frame_type)
            # linking frame instances
            a_frame_inst = frame_pair.a_frame_inst
            b_frame_inst = frame_pair.b_frame_inst
            a_b_frame_type_link.link_frame_insts( a_frame_inst, b_frame_inst)

        # ADDED FOR MODALS, DELETE
        return a_frame_insts, b_frame_insts, frame_pairs

    def after_process_document( self, doc):  # void
        """ overriden block method """
        #self.examiner.print_stats()
        a_dict_of_verbs = self.a_frame_extractor.get_dict_of_verbs()
        b_dict_of_verbs = self.b_frame_extractor.get_dict_of_verbs()
        #self.end_obl( a_dict_of_verbs)
        #self.end_obl( b_dict_of_verbs)
        #self._finalize_dictionary( a_dict_of_verbs, self.a_lang_mark)
        #self._finalize_dictionary( b_dict_of_verbs, self.b_lang_mark)
        #self._output_control()
        self._pickle_dict( a_dict_of_verbs, b_dict_of_verbs)
        #return
        #print( "=== pocty slovies ===")
        #print( self.a_lang_mark, len( self._a_dict_of_verbs))
        #print( self.b_lang_mark, len( self._b_dict_of_verbs))
        #print( self.a_and_b, self.a_only, self.b_only)
        super().after_process_document( doc)

    def end_obl(self, dict_of_verbs):
        suma = 0
        for vr in dict_of_verbs.values():
            for ft in vr.frame_types:
                for fta in ft.args:
                    if fta.deprel == "obl":
                        suma += len( fta.insts)
        print( suma)

    def _finalize_dictionary( self, dict_of_verbs, lang_mark):
        #obl_ratio_limit = 0#.5
        extraction_finalizer = \
            Extraction_finalizer( dict_of_verbs, self.obl_ratio_limit,
                                  self.min_obl_inst_num, lang_mark)
        for verb_record in dict_of_verbs.values():
            verb_record.finalize_extraction( extraction_finalizer)
        extraction_finalizer.finalize_extraction()


    def _pickle_dict( self, a_dict_of_verbs, b_dict_of_verbs):  # void
        """ called from after_process_document """
        a_b_dicts_of_verbs = a_dict_of_verbs, b_dict_of_verbs
        logging.info( sys.getrecursionlimit())
        logging.info( sys.getsizeof( a_b_dicts_of_verbs))
        sys.setrecursionlimit( 50000)
        logging.info( sys.getrecursionlimit())
        #a_output_name = self.output_folder + self.a_lang_mark + \
        #        "_" + self.b_lang_mark + "_" + self.output_name
        #b_output_name = self.output_folder + self.b_lang_mark + \
        #        "_" + self.a_lang_mark + "_" + self.output_name
        a_b_output_name = self.output_folder + "_" + self.output_name
        pickle.dump( a_b_dicts_of_verbs, open( a_b_output_name, 'wb'))
        #pickle.dump( a_dict_of_verbs, open( a_output_name, 'wb'))
        #pickle.dump( b_dict_of_verbs, open( b_output_name, 'wb'))

    def _output_control( self):  # void
        """ called from after_process_document """
        a_dict_of_verbs = self.a_frame_extractor.dict_of_verbs
        for verb_record in list( a_dict_of_verbs.values()):
            for ft in verb_record.frame_types:
                for fi in ft.insts:
                    for fia in fi.args:
                        fial = fia.frame_inst_arg_link
                        print( fia.node.form, fial)
