"""
overriden methods of general classes, specific for English
"""
from verb_record import Verb_record
from frame_extractor import Frame_extractor


class En_verb_record( Verb_record):
    def __init__( self, lemma):
        super().__init__( lemma)
        #self.frame_type_class = En_frame_type


class En_frame_extractor( Frame_extractor):
    def __init__( self, pickle_output=None):
        super().__init__( pickle_output)
        self.verb_record_class = En_verb_record
        #self.en_dict_of_verbs = {}
        self.modal_lemmas = [ "can", "could", "may", "might", "shall", "should",
                                 "will", "would", "must" ]



    def _process_frame( self, verb_record, verb_node):  # -> Frame_inst
        """ called from process_node """
        frame_type, frame_inst = self._process_frame_phase_1( verb_node)

        # newly inserted !!
        self._check_modal_verbs( frame_inst, frame_type, verb_node)

        # adding the frame to the verb_record
        verb_record.consider_new_frame_type( frame_type) #, frame_inst)

        return frame_inst

    def _process_frame_phase_1( self, verb_node):
            # -> pair ( Frame_type, Frame_inst )
        # new frame
        frame_type = self.frame_type_class()
        frame_type.set_verb_features( verb_node)
        frame_inst = self.frame_inst_class()

        # creating and adding args to the frame type/inst
        # creating tokens for example sentence and adding them to frame_inst
        self._process_sentence( frame_type, frame_inst, verb_node)

        frame_type.sort_args()  # important for later frame comparision
        frame_type.add_inst( frame_inst)  # connection between frame type and inst

        return frame_type, frame_inst


    def _check_modal_verbs( self, frame_inst, frame_type, verb_node):
        arg_deprels = [ arg.deprel for arg in frame_type.args ]
        if not "nsubj" in arg_deprels:
            for child_node in verb_node.children:
                if child_node.upos == "AUX":
                    lemma_is_modal = child_node.lemma in self.modal_lemmas
                    #lemma_is_have_to = False
                    #if child_node.lemma == "have":
                    #    for other_child_node in verb_node.children:
                    #        if other_child_node.lemma == "to":
                    #            lemma_is_have_to = True
                    if lemma_is_modal:# or lemma_is_have_to:
                        frame_inst.has_modal = True