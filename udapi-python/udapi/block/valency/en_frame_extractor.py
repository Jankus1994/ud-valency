from frame_extractor import Frame_extractor, Main_subj_unit
from extraction_unit import Extraction_unit
from sent_token import Sent_token
from collections import Counter

# config dict codes used
#	mdin	inclusion of modal verbs
#	case	adding cases when missing (Nom to subjects, Acc elsewhere - objects and obliques)
#	pass	depassivization (both proper and reflexive)
#	ptgr	for participles and gerunds, including their head as argument (obj / subj)
#	auxf	replacing form of clausal arguments with "Fin" if they have an auxiliary with "Fin"
#	that	adding "(that)" to ccomps without conjunction or bracketing it, if present
#	cvex	excluding verbs acting like prepositions

class En_frame_extractor( Frame_extractor):

    proper_unit_codes = [ "that", "cvex", "cprt", "pass", "ptgr", "case", "mdin" ]

    def __init__( self, **kwargs):
        # self.modals_inclusion = False

        super().__init__( **kwargs)

        # self.fill_unit_class_names( "En", proper_unit_codes)

        self.unit_classes[ "that" ] = En_that_unit
        self.unit_classes[ "cvex" ] = En_cvex_unit
        self.unit_classes[ "cprt" ] = En_cprt_unit
        self.unit_classes[ "pass" ] = En_pass_unit
        self.unit_classes[ "ptgr" ] = En_ptgr_unit
        self.unit_classes[ "case" ] = En_case_unit
        self.unit_classes[ "mdin" ] = En_mdin_unit

        self.appropriate_udeprels.append( "compound") # !!! tot je zle, ma to byt v unite

        self.lang_mark = "en"

        self.modal_lemmas = [ "can", "may", "shall", "must", "will" ]
        self.modal_lemmas += [ "could", "might", "should", "would" ]

    def node_is_appropriate(self, node):
        result = super().node_is_appropriate(node)
        cvex_active = self.unit_dict[ "cvex" ].active
        cvex_result = self.unit_dict[ "cvex" ].node_is_appropriate( node, result)
        mdin_result = self.unit_dict[ "mdin" ].node_is_appropriate( node, result)
        return ( result or mdin_result ) and ( not cvex_active or cvex_result )

    def _process_frame( self, verb_node):
        frame_type, frame_inst = super()._process_frame( verb_node)

        frame_type = self.unit_dict[ "pass" ].process_frame( frame_type, verb_node)
        frame_type = self.unit_dict[ "that" ].process_frame( frame_type, verb_node)

        frame_type, frame_inst = \
                self.adding_missing_subjects( frame_type, frame_inst, verb_node)

        frame_type = self.unit_dict[ "case" ].process_frame( frame_type, verb_node)

        return frame_type, frame_inst

    def _node_is_good_arg( self, sent_node, verb_node):
        result = super()._node_is_good_arg( sent_node, verb_node)

        mdin_result = self.unit_dict[ "mdin" ].node_is_good_arg( sent_node, verb_node,
                                                                 result)
        ptgr_result = self.unit_dict[ "ptgr" ].node_is_good_arg( sent_node, verb_node,
                                                                 result)
        cprt_result = self.unit_dict[ "cprt" ].node_is_good_arg( sent_node, verb_node,
                                                                 result)

        return result or mdin_result or ptgr_result or cprt_result

    def process_arg(self, arg_node, verb_node):
        frame_type_arg, frame_inst_arg = super().process_arg(arg_node, verb_node)

        frame_type_arg = self.unit_dict[ "mdin" ].process_arg( frame_type_arg,
                                                       arg_node, verb_node)
        frame_type_arg = self.unit_dict[ "ptgr" ].process_arg( frame_type_arg,
                                                       arg_node, verb_node)
        return frame_type_arg, frame_inst_arg

class En_that_unit( Extraction_unit):
    """ ARG level unit
    adding or bracketing that in dependent clauses
    """
    def process_frame( self, frame_type, _):
        that_comps = frame_type.get_arg( "ccomp", "", ["that"])
        that_comps += frame_type.get_arg( "ccomp", "Fin", ["that"])
        that_comps_len_1 = len( that_comps)
        self.frm_example_counter[ "present" ] += that_comps_len_1
        that_comps += frame_type.get_arg( "ccomp", "", [])
        that_comps += frame_type.get_arg( "ccomp", "Fin", [])
        self.frm_example_counter[ "absent" ] += len( that_comps) - that_comps_len_1
        if that_comps != []:
            that_comp_arg = that_comps[ 0 ]
            that_comp_arg.case_mark_rels = ["(that)"]
        return frame_type

class En_pass_unit( Extraction_unit):
    """ ARG level unit """

    def process_frame( self, frame_type, verb_node):
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
                obj_arg = self.extractor.frame_type_arg_class( "obj", "Acc", [])
                self.extractor.substitute_arg(old_nsubj_arg, obj_arg)
                self.frm_example_counter[ "nsubj-obj" ] += 1

            csubj_args = frame_type.get_arg( "csubj", None, None)
            csubj_args += frame_type.get_arg( "csubj:pass", None, None)
            if csubj_args != []:
                old_csubj_arg = csubj_args[ 0 ]
                form = old_csubj_arg.form
                comp_arg = self.extractor.frame_type_arg_class( "ccomp", form, [])
                self.extractor.substitute_arg(old_csubj_arg, comp_arg)
                self.frm_example_counter[ "csubj-ccomp" ] += 1
            if not frame_type.has_subject():
                obl_args = frame_type.get_arg( "obl", "", ["by"])
                new_nsubj_arg = self.extractor.frame_type_arg_class( "nsubj", "Nom", [])
                if obl_args != []:
                    obl_arg = obl_args[ 0 ]
                    self.extractor.substitute_arg(obl_arg, new_nsubj_arg)
                    self.frm_example_counter[ "obl-nsubj" ] += 1

        return frame_type

class En_case_unit( Extraction_unit):
    """ ARG level unit """
    def process_frame( self, frame_type, _):
        for arg in frame_type.args:
            if arg.form == "":
                if "nsubj" in arg.deprel:
                    arg.form = "Nom"
                    self.arg_example_counter[ "nom" ] += 1
                elif "obj" in arg.deprel or "obl" in arg.deprel:
                    # this includes "iobj" too
                    arg.form = "Acc"
                    self.arg_example_counter[ "acc" ] += 1
        return frame_type

class En_ptgr_unit( Extraction_unit):
    """ ARG level unit """
    def node_is_good_arg( self, sent_node, verb_node, _):
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

    def process_arg( self, frame_type_arg, arg_node, verb_node):
        if verb_node.feats[ "VerbForm" ] in [ "Part", "Ger" ] and \
                verb_node.udeprel in [ "acl", "amod" ] and \
                arg_node is verb_node.parent:
            if verb_node.feats[ "VerbForm" ] == "Part":
                frame_type_arg.deprel = "nsubj:pass"
                self.arg_example_counter[ "part" ] += 1
            elif verb_node.feats[ "VerbForm" ] == "Ger":
                frame_type_arg.deprel = "nsubj"
                self.arg_example_counter[ "ger" ] += 1
            frame_type_arg.form = "Nom"
            frame_type_arg.case_mark_rels = []
        return frame_type_arg

class En_cprt_unit( Extraction_unit):
    """ ARG level unit """
    def node_is_good_arg( self, sent_node, verb_node, _):
        if sent_node.parent is verb_node and sent_node.deprel == "compound:prt":
            self.arg_example_counter[ "" ] += 1
            result = True
            return result

class En_mdin_unit( Extraction_unit):
    def node_is_appropriate( self, node, result):
        if self._verb_is_modal( node):
            self.frm_example_counter[ "" ] += 1
            self.frm_example_counter[ node.lemma ] += 1
            return True
        return False

    def node_is_good_arg( self, sent_node, verb_node, _):
        if self._verb_is_modal( verb_node):
            parent_node = verb_node.parent
            result = False
            if sent_node is parent_node:
                result = True
            elif sent_node.parent is parent_node and "subj" in sent_node.deprel:
                result = True
            return result
        return False

    def _verb_is_modal( self, verb_node):
        return verb_node.upos == "AUX" and verb_node.lemma in self.extractor.modal_lemmas

    def process_arg( self, frame_type_arg, arg_node, verb_node):
        if self._verb_is_modal( verb_node):
            if verb_node.parent is arg_node:
                frame_type_arg.deprel = "xcomp"
        return frame_type_arg

class En_cvex_unit( Extraction_unit):
    """ FRM level unit """
    def node_is_appropriate( self, node, result):
        my_result = True
        if result and node.udeprel == "case":
            self.frm_example_counter[ "" ] += 1
            self.frm_example_counter[ node.form ] += 1
            my_result = False
        return my_result