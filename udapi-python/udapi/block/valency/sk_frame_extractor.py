from csk_frame_extractor import Csk_frame_extractor
from sent_token import Sent_token

class Sk_frame_extractor( Csk_frame_extractor):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.lang_mark = "sk"

        #self.pron_sg1 = "ja"
        self.verb_be = "byť"

        #self.pron_sg3m = "3sg:on"
        #self.pron_sg3f = "3sg:ona"
        #self.pron_sg3f = "3sg:ono"
        #self.pron_pl3ma = "3pl:oni"
        #self.pron_pl3mifn = "3pl:ony"

        self.modal_lemmas = [ "musieť", "môcť", "mať", "smieť", "chcieť",
                              "hodlať", "vedieť" ] # dať sa?

    # @staticmethod
    # def try_getting_person_3( verb_node):
    #     token_form = "3"
    #     if verb_node.feats[ "VerbForm" ] == "Part":
    #         if verb_node.feats[ "Number" ] == "Sing":
    #             token_form += "sg:"
    #             if verb_node.feats[ "Gender" ] == "Masc":
    #                 token_form += "on"
    #             elif verb_node.feats[ "Gender" ] == "Fem":
    #                 token_form += "ona"
    #             elif verb_node.feats[ "Gender" ] == "Neut":
    #                 token_form += "ono"
    #         elif verb_node.feats[ "Number" ] == "Plur":
    #             token_form += "pl:"
    #             if verb_node.feats[ "Gender" ] == "Masc" and \
    #                     verb_node.feats[ "Animacy" ] == "Anim":
    #                 token_form += "oni"
    #             else:
    #                 token_form = "ony"
    #         else:
    #             token_form += "prs"
    #     else:
    #         token_form += "prs"
    #     return token_form