"""
child class of udapi block
processes connlu file with parallel senteces in 2 languages
and simultanously reads word alignment
produces vallency dictionary and saves it into a pickle file
"""
import logging
import pickle
import sys

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
        if align_file_name != "":
            try:
                self.align_file = open( align_file_name, 'r')
            except FileNotFoundError:
                print( "ERROR")
                exit()

        self.a_and_b = 0
        self.a_only = 0
        self.b_only = 0
        self.direction = 0 # 0 .. both, 1 .. a -> b, 2 .. b -> a

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
        
        # reading alignment line
        alignments = self.align_file.readline().split()
        a_b_ali_dict = {}
        b_a_ali_dict = {}
        for alignment in alignments:
            a_index_str, b_index_str = alignment.split( '-')
            try:
                a_index = int( a_index_str)
                b_index = int( b_index_str)
            except:
                print( "conv ERROR")
                exit()
            a_b_ali_dict[ a_index + 1 ] = b_index + 1
            b_a_ali_dict[ b_index + 1 ] = a_index + 1

        # the frame alignment procedure is in itself dependent on a dictionary
        # direction, but as we suppose the world alignment is done by a symmetric
        # combination (intersection or union) of both one-direction alignments
        # both runs of the framec alignment procedure would lead to the same result
        self._frame_alignment( self.a_lang_mark, a_frame_insts, b_frame_insts, \
                                a_b_ali_dict)
    
    def _frame_alignment( self, frst_lang_code, frst_frame_insts, scnd_frame_insts, \
                            frst_scnd_ali_dict):  # void
        """ called from process_bundle
        aligns frame types and frame instances of two languages
        the alignment depends on a given word alignment dictionary
        which is either a->b or b->a
        so here are labels "frst" and "scnd" used instead
        """
        # aligning frame instances
        for frst_frame_inst in frst_frame_insts:
            frst_frame_type = frst_frame_inst.get_type()
            frst_verb_index = frst_frame_inst.verb_node.ord
            #print( frst_verb_index, frst_frame_inst.verb_node.form)
            try:
                scnd_verb_index = frst_scnd_ali_dict[ frst_verb_index ]
            except KeyError:  # this token was not aligned
                #print( "    OOOO")
                continue
            for scnd_frame_inst in scnd_frame_insts:
                if scnd_frame_inst.verb_node.ord == scnd_verb_index:
                    chosen_scnd_frame_inst = scnd_frame_inst
                    break
            else:  # the token was not aligned to any verb token
                #print( "    XXXX")
                continue
            #frst_lemma = frst_frame_inst.verb_node.lemma
            #scnd_lemma = scnd_frame_inst.verb_node.lemma

            # unmatched instances will have "frame_type_link" attribute still None
            scnd_frame_type = chosen_scnd_frame_inst.get_type()

            # linking frame types
            # if the frame type link does not exist yet, create one
            frst_scnd_frame_type_link = frst_frame_type.find_link_with( scnd_frame_type)
                    # could be done the other way around: b_frame.find( frst_frame)
            if frst_scnd_frame_type_link is None:
                frst_scnd_frame_type_link = \
                        Frame_type_link( frst_frame_type, scnd_frame_type)
            # linking frame instances
            frst_scnd_frame_type_link.link_frame_insts( frst_frame_inst, scnd_frame_inst)


        #self.pickle_dict()


    def after_process_document( self, doc):  # void
        """ overriden block method """
        #self._output_control()
        self._pickle_dict()
        return
        print( "=== pocty slovies ===")
        print( self.a_lang_mark, len( self._a_dict_of_verbs))
        print( self.b_lang_mark, len( self._b_dict_of_verbs))
        print( self.a_and_b, self.a_only, self.b_only)
        #super().after_process_document( doc)

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
        a_b_output_name = self.output_folder + self.a_lang_mark + \
                "_" + self.b_lang_mark + "_" + self.output_name
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
