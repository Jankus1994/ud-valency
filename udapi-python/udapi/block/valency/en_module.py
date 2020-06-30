"""
overriden methods of general classes, specific for English
"""

from udapi.block.valency.frame_extractor import *

class En_verb_record( Verb_record):
    def __init__( self, lemma):
        super().__init__( lemma)
        #self.frame_type_class = En_frame_type

class En_frame_extractor( Frame_extractor):
    def __init__( self, pickle_output=None):
        super().__init__( pickle_output)
        self.verb_record_class = En_verb_record
        #self.en_dict_of_verbs = {}


