from csk_frame_extractor import Csk_frame_extractor
from sent_token import Sent_token

class Cs_frame_extractor( Csk_frame_extractor):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)

        self.lang_mark = "cs"

        self.pron_sg1 = "já"
        self.verb_be = "být"

        self.modal_lemmas = [ "muset", "moci", "mít", "smět", "chtít",
                              "hodlat", "umět", "dovést" ]

    @staticmethod
    def try_getting_person_3( verb_node):
        person = ""
        number = ""
        pronoun = ""
        if verb_node.feats[ "VerbForm" ] == "Part":
            person = "3"
            number = ""
            pronoun = "on"
            form_ending = verb_node.form[ -1]
            if form_ending in "aioy":
                pronoun += form_ending
            if form_ending in "iy":
                number = "pl"
            elif form_ending != 'a':
                number = "sg"
        token_form = person + number + ':' + pronoun

        return token_form