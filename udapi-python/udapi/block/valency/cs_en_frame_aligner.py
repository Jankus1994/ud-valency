"""
child class of udapi block
processes connlu file with parallel senteces in 2 languages
and simultanously reads word alignment
produces vallency dictionary and saves it into a pickle file
"""

import pickle

from udapi.core.block import Block
from udapi.block.valency.cs_module import Cs_frame_extractor
from udapi.block.valency.en_module import En_frame_extractor
from udapi.block.valency.frame import Frame_link

class Cs_En_frame_aligner( Block):
    def __init__( self, align_file_name="", output = None, **kwargs):
        super().__init__( **kwargs)
        
        self.align_file = None
        self.output = output
        if align_file_name != "":
            try:
                self.align_file = open( align_file_name, 'r')
            except FileNotFoundError:
                print( "ERROR")
                exit()

        self.cs_and_en = 0
        self.cs_only = 0
        self.en_only = 0
        self.direction = 0 # 0 .. both, 1 .. cs->en, 2 .. en->cs

        # we do not specify pickle outputs for extractors seperately
        self.cs_frame_extractor = Cs_frame_extractor()
        self.en_frame_extractor = En_frame_extractor()

    def process_bundle( self, bundle):
        """ overriden block method """
        cs_frame_instances = []
        en_frame_instances = []
        for tree_root in bundle.trees:
            if tree_root.zone == "cs":
                cs_frame_instances = \
                        self.cs_frame_extractor.process_tree( tree_root)
            elif tree_root.zone == "en":
                en_frame_instances = \
                        self.en_frame_extractor.process_tree( tree_root)

        # reading alignment line
        alignments = self.align_file.readline().split()
        cs_en_ali_dict = {}
        en_cs_ali_dict = {}
        for alignment in alignments:
            cs_index_str, en_index_str = alignment.split( '-')
            try:
                cs_index = int( cs_index_str)
                en_index = int( en_index_str)
            except:
                print( "conv ERROR")
                exit()
            cs_en_ali_dict[ cs_index + 1 ] = en_index + 1
            en_cs_ali_dict[ en_index + 1 ] = cs_index + 1

        self.frame_alignment( "cs", cs_frame_instances, en_frame_instances, cs_en_ali_dict)
    
    def frame_alignment( self, lang_code, a_frame_instances, b_frame_instances, ab_ali_dict):
        # aligning frame instances
        for a_frame_instance in a_frame_instances:
            a_frame_type = a_frame_instance.get_type()
            a_verb_index = a_frame_instance.verb_node.ord
            #print( cs_verb_index, cs_frame_instance.verb_node.form)
            try:
                b_verb_index = ab_ali_dict[ a_verb_index ]
            except KeyError:  # this token was not aligned
                #print( "    OOOO")
                continue
            for b_frame_instance in b_frame_instances:
                if b_frame_instance.verb_node.ord == b_verb_index:
                    chosen_b_frame_instance = b_frame_instance
                    break
            else:  # the token was not aligned to any verb token
                #print( "    XXXX")
                continue
            #cs_lemma = cs_frame_instance.verb_node.lemma
            #en_lemma = en_frame_instance.verb_node.lemma

            # unmatched instances will have "frame_link" attribute still None
            b_frame_type = chosen_b_frame_instance.get_type()
            frame_link = a_frame_type.find_link_with( b_frame_type)
            if frame_link is None:
                frame_link = Frame_link( a_frame_type, b_frame_type)
                # assymetric linking
                a_frame_type.add_frame_link( frame_link)
                #b_frame_type.add_frame_link( frame_link)
            frame_link.add_frame_instance_pair( a_frame_instance, b_frame_instance)


        self.pickle_dict()


    def after_process_document( self, doc):
        return
        print( "=== pocty slovies ===")
        print( "CS", len( self._cs_dict_of_verbs))
        print( "EN", len( self._en_dict_of_verbs))
        print(self.cs_and_en, self.cs_only, self.en_only)
        #super().after_process_document( doc)

    def pickle_dict( self):
        cs_dict_of_verbs = self.cs_frame_extractor.dict_of_verbs
        en_dict_of_verbs = self.en_frame_extractor.dict_of_verbs
        cs_en_dicts_of_verbs = cs_dict_of_verbs, en_dict_of_verbs
        #cs_en_dicts_of_verbs = en_dict_of_verbs
        p = pickle.dump( cs_en_dicts_of_verbs, open( self.output, 'wb'))


