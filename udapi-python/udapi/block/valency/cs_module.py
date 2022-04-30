"""
overriden methods of general classes, specific for Czech
"""

from frame_extractor import *
from frame_type import *
from sent_token import Sent_token

class Cs_frame_type_arg( Frame_type_arg):
    def __init__( self, node, deprel="", case_feat="", case_mark_rels=[]):
        is_numerative  = False
        if node is not None:
            is_numerative, original_case = self.consider_numerative( node)
        super().__init__( node, deprel, case_feat, case_mark_rels)
        if is_numerative:
            self.case_feat = original_case

    @staticmethod
    def consider_numerative( node):
        original_case = ""
        for child in node.children:
            if child.deprel in [ "nummod:gov", "det:numgov" ]:
                original_case = child.feats[ "Case" ]
                return True, original_case
        return False, original_case

#class Cs_frame_inst_arg( Cs_frame_type_arg):
#    def __init__( self, node):
#        self.node = node
#        #self.translations = []
#        super().__init__( node)


#class Cs_frame_inst( Frame_inst):
#    def __init__( self, frame_type, verb_node):
#        super().__init__( frame_type, verb_node):
#        self.arg_class = Cs_frame_inst_arg


class Cs_frame_type( Frame_type):
    def __init__( self, verb_node):
        super().__init__( verb_node)
        self.elided_tokens = []
        self.arg_class = Cs_frame_type_arg

    def process_first_verb_node( self, verb_node):
        self.verb_lemma = verb_node.lemma
        # not setting vf and voice - is it ok??
        self.verb_form = "0"
        self.voice = "0"
        self.first_frame_inst = self.process_args_and_first_inst( verb_node)

    def process_args_and_first_inst( self, verb_node):
        first_frame_inst = self.frame_inst_class( self)
        self.process_args( verb_node, first_frame_inst)
        self.args_transform_reflex_passive()
        self.sort_args()
        first_frame_inst.process_sentence( verb_node, elided_tokens)


    def process_args( self, verb_node):
        super().process_args( verb_node)
        old_args = self.args
        transformed_args = self.transform_reflex_passive( old_args)
        extended_args, elided_tokens = \
                self.process_elided_args( verb_node, transformed_args)
        self.args = extended_args

    def process_first_inst( self):
        # elided tokens filled in process_elided_args
        self.first_frame_inst.process_sentence( self.elided_tokens)
        self.insts.append( self.first_frame_inst)


    def transform_reflex_passive( self, frame_args): # -> list of transformed Frame_args
        """ tranforming frames with reflexive passive construction to their active equivalent
        zahrada se kosi -> kosi zahradu
        expl:pass-Acc -> 0, nsubj:pass-Nom -> obj-Acc
        """
        expl_arg = Cs_frame_type_arg( None, "expl:pass", "Acc", [])
        nsubj_arg = Cs_frame_type_arg( None, "nsubj:pass", "Nom", [])
        obj_arg = Cs_frame_type_arg( None, "obj", "Acc", [])
        if any( arg.is_identical_with( expl_arg) for arg in frame_args) and \
                any( arg.is_identical_with( nsubj_arg) for arg in frame_args):
            frame_args = self.remove_arg( frame_args, expl_arg)
            frame_args = self.subst_arg( frame_args, nsubj_arg, obj_arg)
        return frame_args

    @staticmethod
    def subst_arg( frame_args, old_arg, new_arg): # -> list of transformed Frame_args
        """ substitution of old_arg with new_arg """
        return [ new_arg if arg.is_identical_with( old_arg) \
                         else arg for arg in frame_args ]
    @staticmethod
    def remove_arg( frame_args, rem_arg): # -> list of transformed Frame_args
        """ removing rem_arg from list of frame arguments """
        return [ arg for arg in frame_args if not arg.is_identical_with( rem_arg) ]

    def process_elided_args( self, verb_node, frame_args):
        elided_tokens = []
        elided_arg, elided_token = \
                self.consider_elided_subject( verb_node, frame_args)
        if elided_arg is not None:
            frame_args.append( elided_arg)
            elided_tokens.append( elided_token)
        elif not self.args_include_subject( frame_args):
            subject_arg = Cs_frame_type_arg( None, "nsubj", "Nom", [])
            frame_args.append( subject_arg)
        return frame_args, elided_tokens

    def consider_elided_subject( self, node, frame_args):
        for frame_arg in frame_args:
            if frame_arg.deprel == "nsubj" or frame_arg.deprel == "csubj":
                return None, None

        # the verb (node) does not have a subject:
        token_person_1_2 = self.get_token_of_person_1_2( node)
        if token_person_1_2 is not None:
            token_person_1_2.mark_elision()
            elided_arg = Cs_frame_type_arg( None, "nsubj", "Nom", [])
            token_person_1_2.set_arg( elided_arg)
            return elided_arg, token_person_1_2

        # looking for an auxiliary verb, which would confirm the 1./2. person
        for child in node.children:
            if child.upos == "AUX":
                token_person_1_2 = self.get_token_of_person_1_2( child)
                if token_person_1_2 is not None:
                    token_person_1_2.mark_elision()
                    elided_arg = Cs_frame_type_arg( None, "nsubj", "Nom", [])
                    token_person_1_2.set_arg( elided_arg)
                    return elided_arg, token_person_1_2

        # the node can be a complement of a parant verb, which could confirm the 1./2. person
        if node.deprel == "xcomp" and node.parent.upos == "VERB":
            token_person_1_2 = self.get_token_of_person_1_2( node.parent)
            if token_person_1_2 is not None:
                token_person_1_2.mark_elision()
                elided_arg = Cs_frame_type_arg( None, "nsubj", "Nom", [])
                token_person_1_2.set_arg( elided_arg)
                return elided_arg, token_person_1_2

        return None, None

    @staticmethod
    def get_token_of_person_1_2( node):
        token = None
        if node.feats["Person"] == "1":
            if node.feats["Number"] == "Sing":
                token = Sent_token()
                token.set_form( "já")
            elif node.feats["Number"] == "Plur":
                token = Sent_token()
                token.set_form( "my")
        elif node.feats["Person"] == "2":
            if node.feats["Number"] == "Sing":
                token = Sent_token()
                token.set_form( "ty")
            elif node.feats["Number"] == "Plur":
                token = Sent_token()
                token.set_form( "vy")
        return token

    @staticmethod
    def args_include_subject( frame_args):
        for frame_arg in frame_args:
            if "nsubj" in frame_arg.deprel or "csubj" in frame_arg.deprel:
                return True
        return False


class Cs_verb_record( Verb_record):
    def __init__( self, lemma):
        super().__init__( lemma)
        self.frame_type_class = Cs_frame_type

    def delete_subframes( self):
        frame_types = sorted( self.frame_types, key = \
                lambda arg:len( arg.str_args))
        reduced_frame_types = []
        # comparing frames and marking those to delete
        for frame_type in frame_types:
            frame_type.args_to_one_string()
        for frame_type_1 in frame_types:
            # a frame should be deleted if it has a superframe
            frame_type_1_superframes = []
            for frame_type_2 in frame_types:
                frame_1_arg_len = len( frame_type_1.str_args)
                frame_2_arg_len = len( frame_type_2.str_args)
                frame_1_arg_set = set( frame_type_1.str_args)
                frame_2_arg_set = set( frame_type_2.str_args)
                if frame_1_arg_len < frame_2_arg_len and \
                        frame_1_arg_set.issubset( frame_2_arg_set):
                    frame_type_1_superframes.append( frame_type_2)

            if frame_type_1_superframes == []:
                reduced_frame_types.append( frame_type_1)
            else:                         
                # !!! we take the biggest (ie. last) superframe - IS IT CORRECT ??? !!!
                # !!! what about sorting the other way around -
                # - could stop after first superframe found with high freq !!!
                biggest_superframe = frame_type_1_superframes[ -1 ]
                # we mark the superframe only if the subframe has
                # a low frequency compared to the superframe                
                if self.compare_insts_number( frame_type_1, biggest_superframe):
                    biggest_superframe.insts += frame_type_1.insts
                else:
                    reduced_frame_types.append( frame_type_1)
        self.frame_types = reduced_frame_types

    @staticmethod
    def compare_insts_number( subframe, superframe): # -> bool
        """ comparing number of instances of a subframe and a superframe
        returns if the superframe is sufficiently more frequent than the subframe
        """
        coef = 2 # !!! 
        if coef * len( subframe.insts) < len( superframe.insts):
            return True
        return False

    
class Cs_frame_extractor( Frame_extractor):
    def __init__( self, pickle_output = None):
        super().__init__( pickle_output)
        self.verb_record_class = Cs_verb_record
        #self.cs_dict_of_verbs = {}
        self.modal_lemmas = [ "muset", "moci", "mít", "smět", "chtít",
                              "hodlat", "umět", "dovést" ]

    def _process_frame( self, verb_record, verb_node):  # -> Frame_inst
        """ called from process_node """
        frame_type, frame_inst = self._process_frame_phase_1( verb_node)

        # newly inserted !!
        is_modal_verb = self._check_handle_modal_verbs(
                                frame_inst, frame_type, verb_node)
        if is_modal_verb:
            return None

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


    def _check_handle_modal_verbs( self, frame_inst, frame_type, verb_node):
        if verb_node.lemma in self.modal_lemmas:
            for child in verb_node.children:
                if child.feats[ "VerbForm" ] == "Inf":
                    #print( "*** ", verb_node.lemma, child.lemma)
                    return True  # modal verb -> frame should not be created

        arg_deprels = [ arg.deprel for arg in frame_type.args ]
        if verb_node.feats[ "VerbForm" ] == "Inf" and not "nsubj" in arg_deprels:
            parent_node = verb_node.parent
            if parent_node.lemma in self.modal_lemmas:
                parent_frame_type, parent_frame_inst = \
                        self._process_frame_phase_1( parent_node)
                for parent_frame_type_arg in parent_frame_type.args:
                    if parent_frame_type_arg.deprel == "nsubj":
                        assert len( parent_frame_type_arg.insts) == 1
                        parent_frame_inst_arg = parent_frame_type_arg.insts[ 0 ]
                        parent_token_ord = parent_frame_inst_arg.token.ord
                        for token in frame_inst.sent_tokens:
                            if token.ord == parent_token_ord:
                                token.set_arg( parent_frame_inst_arg)
                        frame_inst.add_arg( parent_frame_inst_arg)
                        frame_type.add_arg( parent_frame_type_arg)
                        #print( ">>> ", verb_node.lemma, parent_node.lemma)
                        frame_inst.has_modal = True
                        break
        return False

    def after_process_document( self, doc): # void
        for verb_record in self.dict_of_verbs.values():
            verb_record.delete_subframes()  # reducing number of frames before outputting
        super().after_process_document( doc)

