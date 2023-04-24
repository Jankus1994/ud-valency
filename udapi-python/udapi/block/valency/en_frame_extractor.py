from frame_extractor import Frame_extractor
from cs_module import *
from sent_token import Sent_token
from collections import Counter

# config dict codes used
#	mdex	exclusion of modal verbs
#	case	adding cases when missing (Nom to subjects, Acc elsewhere - objects and obliques)
#	pass	depassivization (both proper and reflexive)
#	ptgr	for participles and gerunds, including their head as argument (obj / subj)
#	auxf	replacing form of clausal arguments with "Fin" if they have an auxiliary with "Fin"
#	that	adding "(that)" to ccomps without conjunction or bracketing it, if present
#	cvex	excluding verbs acting like prepositions

class En_frame_extractor( Frame_extractor):

    config_codes = [ "pass", "cvex", "case", "that", "auxf", "ptgr", "mdex" ]

    def __init__( self, **kwargs):
        self.modals_inclusion = False

        super().__init__( **kwargs)

        self.lang_mark = "en"

        if self.modals_inclusion:
            self.config_dict[ "mdex" ] = False

        self.modal_lemmas = [ "can", "may", "shall", "must", "will" ]
        self.modal_lemmas += [ "could", "might", "should", "would" ]
        self.case_verbs_ex = Counter()


    def _node_is_appropriate( self, node):
        result = super()._node_is_appropriate( node)
        if self.config_dict[ "cvex" ]:
            if result and node.udeprel == "case":
                self.frame_examples_counter[ "case_verbs" ] += 1
                self.case_verbs_ex[ node.form ] += 1
                return False

        if self._verb_is_modal( node):
            self.frame_examples_counter[ "modals" ] += 1
            if self.config_dict["modals_inc"]:
                return True
        return result

    def _process_frame( self, verb_node):
        frame_type, frame_inst = super()._process_frame( verb_node)

        # if self.spec_allowed[ "modals" ]:
        #     self._check_modal_verbs( frame_inst, frame_type, verb_node)
        #     # ALEBO
        #     if self._verb_is_modal( verb_node):
        #         return None, None
        #     elif self._verb_has_modal_child( frame_type, verb_node):
        #         frame_type, frame_inst = self._handle_parent_of_modal(
        #                     frame_type, frame_inst, verb_node)

        if self.config_dict[ "pass" ]:
            frame_type = self.transform_proper_passive( frame_type, verb_node)

        if self.config_dict[ "that" ]:
            frame_type = self.facultative_that( frame_type)

        #if self.spec_allowed[ "elision" ]:
        #    frame_type, frame_inst = self.process_elided_args( frame_type, frame_inst)

        frame_type, frame_inst = \
                self.adding_missng_subjects( frame_type, frame_inst, verb_node)

        if self.config_dict[ "case" ]:
            frame_type = self.add_cases( frame_type)

        return frame_type, frame_inst

    def _node_is_good_arg( self, sent_node, verb_node):
        result = super()._node_is_good_arg( sent_node, verb_node)
        if self.config_dict["modals_inc"]:
            if self._verb_is_modal( verb_node):
                parent_node = verb_node.parent
                if sent_node is parent_node:
                    result = True
                elif sent_node.parent is parent_node and "subj" in sent_node.deprel:
                    result = True
        if self.config_dict[ "ptgr" ]:
            parent_node = verb_node.parent
            if sent_node is parent_node:
                has_subj = False
                for child_node in verb_node.children:
                    if "subj" in child_node.deprel:
                        has_subj = True
                if verb_node.feats[ "VerbForm" ] in [ "Part", "Ger" ] and \
                        verb_node.udeprel in [ "acl", "amod" ] and not has_subj:
                    result = True
        return result

    def _process_arg( self, arg_node, verb_node):
        frame_type_arg, frame_inst_arg = super()._process_arg( arg_node, verb_node)
        if self.config_dict["modals_inc"]:
            if self._verb_is_modal( verb_node):
                if verb_node.parent is arg_node:
                    frame_type_arg.deprel = "xcomp"
        if self.config_dict[ "auxf" ]:
            frame_type_arg = self._consider_aux_form( frame_type_arg, arg_node)
        if self.config_dict[ "ptgr" ]:
            if verb_node.feats[ "VerbForm" ] in [ "Part", "Ger" ] and \
                    verb_node.udeprel in [ "acl", "amod" ] and \
                    arg_node is verb_node.parent:
                if verb_node.feats[ "VerbForm" ] == "Part":
                    frame_type_arg.deprel = "nsubj:pass"
                    self.arg_examples_counter[ "attr_part" ] += 1
                elif verb_node.feats[ "VerbForm" ] == "Ger":
                    frame_type_arg.deprel = "nsubj"
                    self.arg_examples_counter[ "attr_ger" ] += 1
                frame_type_arg.form = "Nom"
                frame_type_arg.case_mark_rels = []
        return frame_type_arg, frame_inst_arg

    def _verb_is_modal( self, verb_node):
        return verb_node.upos == "AUX" and verb_node.lemma in self.modal_lemmas

    # def _verb_has_modal_child( self, frame_type, verb_node):
    #     # infinitive without subject and with a modal head with subject ->
    #     # -> adding the subject into this node's frame
    #     arg_deprels = [ arg.deprel for arg in frame_type.args ]
    #     if verb_node.feats[ "VerbForm" ] == "Inf" and not "nsubj" in arg_deprels:
    #         for child in verb_node.children:
    #             if child.lemma in self.modal_lemmas:
    #                 return True  # verb is infinitive child of modal verb
    #     return False
    #
    # def _handle_parent_of_modal( self, frame_type, frame_inst, verb_node): # -> bool
    #     """ adds the subject of the modal is added to this verb's frame
    #     returs bool if this verb is modal
    #     """
    #     modal_verb_node = verb_node.parent
    #     parent_frame_type, parent_frame_inst = \
    #             super()._process_frame( modal_verb_node)
    #     for parent_arg in parent_frame_type.args:
    #         if parent_arg.deprel == "nsubj":
    #             subject_arg_type = parent_arg
    #             subject_arg_inst = parent_arg.insts[ 0 ]
    #
    #             # TODO maybe move to inst arg?
    #             subject_ord = subject_arg_inst.token.ord
    #             subject_token = [ token for token in frame_inst.sent_tokens
    #                               if token.ord == subject_ord ][ 0 ]
    #             self._connect_arg_with_frame(frame_type, frame_inst,
    #                                          subject_arg_type, subject_arg_inst, subject_token)
    #             #print( ">>> ", verb_node.lemma, parent_node.lemma)
    #             frame_inst.has_modal = True
    #             break
    #     return frame_type, frame_inst

    def add_cases( self, frame_type):
        for arg in frame_type.args:
            if arg.form == "":
                if "nsubj" in arg.deprel:
                    arg.form = "Nom"
                    self.arg_examples_counter[ "cases-nom" ] += 1
                elif "obj" in arg.deprel or "obl" in arg.deprel:
                    # this includes "iobj" too
                    arg.form = "Acc"
                    self.arg_examples_counter[ "cases-acc" ] += 1
        return frame_type

    def transform_proper_passive( self, frame_type, verb_node):
        has_aux = False
        for child_node in verb_node.children:
            if child_node.lemma == "be" and child_node.upos == "AUX" and \
                    child_node.deprel == "aux:pass":
                has_aux = True
                break
        if frame_type.verb_form == "Part":

            nsubj_args = frame_type.get_arg( "nsubj:pass", "", [])
            nsubj_args += frame_type.get_arg( "nsubj:pass", "Nom", [])
            if has_aux:
                nsubj_args += frame_type.get_arg( "nsubj", "", [])
                nsubj_args += frame_type.get_arg( "nsubj", "Nom", [])

            if nsubj_args != []:
                old_nsubj_arg = nsubj_args[ 0 ]
                obj_arg = self.frame_type_arg_class( "obj", "Acc", [])
                self._substitute_arg( old_nsubj_arg, obj_arg)
                self.frame_examples_counter[ "passive-nsubj-obj" ] += 1

            csubj_args = frame_type.get_arg( "csubj", None, None)
            csubj_args += frame_type.get_arg( "csubj:pass", None, None)
            if csubj_args != []:
                old_csubj_arg = csubj_args[ 0 ]
                form = old_csubj_arg.form
                comp_arg = self.frame_type_arg_class( "ccomp", form, [])
                self._substitute_arg( old_csubj_arg, comp_arg)
                self.frame_examples_counter[ "passive-csubj-ccomp" ] += 1

            if not frame_type.has_subject():
                obl_args = frame_type.get_arg( "obl", "", ["by"])
                new_nsubj_arg = self.frame_type_arg_class( "nsubj", "Nom", [])
                if obl_args != []:
                    obl_arg = obl_args[ 0 ]
                    self._substitute_arg( obl_arg, new_nsubj_arg)
                    self.frame_examples_counter[ "passive-obl-nsubj" ] += 1

        return frame_type

    def facultative_that( self, frame_type):
        that_comps = frame_type.get_arg( "ccomp", "", ["that"])
        that_comps += frame_type.get_arg( "ccomp", "Fin", ["that"])
        that_comps_len_1 = len( that_comps)
        self.frame_examples_counter[ "that-yes" ] += that_comps_len_1
        that_comps += frame_type.get_arg( "ccomp", "", [])
        that_comps += frame_type.get_arg( "ccomp", "Fin", [])
        self.frame_examples_counter[ "that-no" ] += len( that_comps) - that_comps_len_1
        if that_comps != []:
            that_comp_arg = that_comps[ 0 ]
            that_comp_arg.case_mark_rels = ["(that)"]
        return frame_type

    # def consider_aux_arg(self, frame_type_arg, frame_inst_arg, arg_node, verb_node):
    #     if "comp" in frame_type_arg.deprel:# and frame_type_arg.form == "Inf":
    #         for child_node in arg_node.children:
    #             if child_node.upos == "AUX" and \
    #                     child_node.feats[ "VerbForm" ] == "Fin":
    #                 frame_type_arg, frame_inst_arg = \
    #                         self._process_arg( child_node, verb_node)
    #     return frame_type_arg, frame_inst_arg

    def _print_example_counts( self):
        super()._print_example_counts()
        print( self.case_verbs_ex)