"""
overriden methods of general classes, specific for Czech
"""

from frame_extractor import *
from frame_type import *


class Cs_frame_inst( Frame_inst):
    def __init__( self):
        super().__init__()
        self._elided_tokens = []

    @property
    def elided_tokens( self):
        return self._elided_tokens
    @elided_tokens.setter
    def elided_tokens( self, elided_tokens):
        self._elided_tokens = elided_tokens
    def add_elided_token( self, elided_token):
        self._elided_tokens.append( elided_token)


class Cs_frame_type( Frame_type):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.elided_tokens = []

class Cs_verb_record( Verb_record):
    def __init__( self, lemma):
        super().__init__( lemma)
        self.frame_type_class = Cs_frame_type


