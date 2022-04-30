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
from udapi.block.valency.frame_extractor import Frame_extractor
from udapi.block.valency.link_structures import Frame_type_link

class Frame_aligner( Block):
    def __init__( self, align_file_name="", output_folder="", output_name="", **kwargs):
        """ overriden block method """
        super().__init__( **kwargs)
        
        self.align_file = None
        self.output_folder = output_folder
        self.output_name = output_name
        self.linker = Linker()  # !!!
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


    def process_bundle( self, bundle):  # void
        """ overriden block method """
        #logging.info( "bundle id: " + str( bundle.bundle_id))
        a_frame_insts = []
        b_frame_insts = []
        for tree_root in bundle.trees:
            if tree_root.zone == self.a_lang_mark:
                a_frame_insts = \
                        self.a_frame_extractor.process_tree( tree_root)
            elif tree_root.zone == self.b_lang_mark:
                b_frame_insts = \
                        self.b_frame_extractor.process_tree( tree_root)
        
        word_alignments = self.align_file.readline().split()

        frame_pairs = linker.find_frame_pairs( a_frame_insts, b_frame_insts, word_alignments)

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



    def after_process_document( self, doc):  # void
        """ overriden block method """
        #self._output_control()
        self._pickle_dict()
        #return
        #print( "=== pocty slovies ===")
        #print( self.a_lang_mark, len( self._a_dict_of_verbs))
        #print( self.b_lang_mark, len( self._b_dict_of_verbs))
        #print( self.a_and_b, self.a_only, self.b_only)
        super().after_process_document( doc)

    def _pickle_dict( self):  # void
        """ called from after_process_document """
        a_dict_of_verbs = self.a_frame_extractor.get_dict_of_verbs()
        b_dict_of_verbs = self.b_frame_extractor.get_dict_of_verbs()
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
