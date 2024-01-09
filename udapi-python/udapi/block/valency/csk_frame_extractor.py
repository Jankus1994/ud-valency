from frame_extractor import Frame_extractor, Main_subj_unit
from extraction_unit import Extraction_unit
from sent_token import Sent_token
from collections import Counter

# config dict codes used
#	mdin	inclusion of modal verbs
#	nomi	adding missing nominative to subjects (also to elided ones)
#	vadj	creating valency frames also for verbal adjectives, including their head as argument
#	pfin	replacing "Part" VerbFrom with "Fin"
#	pass	depassivization (both proper and reflexive)
#	numr	replacing numerative genitives with nominatives or accusatives

class Csk_frame_extractor( Frame_extractor):

    proper_unit_codes = [ "nomi", "vadj", "pfin", "pass", "numr", "case", "mdex" ]

    def __init__( self, **kwargs):
        # self.modals_inclusion = True

        super().__init__( **kwargs)


        # self.fill_unit_class_names( "Csk", proper_unit_codes)

        self.unit_classes[ "nomi" ] = Csk_nomi_unit
        self.unit_classes[ "vadj" ] = Csk_vadj_unit
        self.unit_classes[ "pfin" ] = Csk_pfin_unit
        self.unit_classes[ "pass" ] = Csk_pass_unit
        self.unit_classes[ "numr" ] = Csk_numr_unit
        self.unit_classes[ "case" ] = Csk_case_unit
        self.unit_classes[ "mdex" ] = Csk_mdex_unit
        # self.units[ "mdex" ] = Csk_mdex_unit
        #
        # if not self.modals_inclusion:
        #     self.units[ "mdex" ] = Csk_mdex_unit

        self.verb_be = ""

    def node_is_appropriate(self, node):
        result = super().node_is_appropriate(node)
        vadj_result = self.unit_dict[ "vadj" ].node_is_appropriate( node, result)
        mdex_result = self.unit_dict[ "mdex" ].node_is_inappropriate( node, result)

        return ( result or vadj_result ) and not mdex_result

    def _node_is_good_arg( self, sent_node, verb_node):
        result = super()._node_is_good_arg( sent_node, verb_node)
        vadj_result = self.unit_dict[ "vadj" ].node_is_good_arg( sent_node, verb_node,
                                                                 result)
        return result or vadj_result

    def process_arg(self, arg_node, verb_node):
        frame_type_arg, frame_inst_arg = super().process_arg( arg_node, verb_node)

        frame_type_arg = self.unit_dict[ "numr" ].process_arg( frame_type_arg,
                                                               arg_node, verb_node)
        frame_type_arg = self.unit_dict[ "pfin" ].process_arg( frame_type_arg,
                                                               arg_node, verb_node)
        frame_type_arg = self.unit_dict[ "vadj" ].process_arg( frame_type_arg,
                                                               arg_node, verb_node)
        return frame_type_arg, frame_inst_arg

    def _process_frame( self, verb_node):
        frame_type, frame_inst = super()._process_frame( verb_node)

        frame_type = self.unit_dict[ "vadj" ].process_frame( frame_type, verb_node)
        frame_type = self.unit_dict[ "nomi" ].process_frame( frame_type, verb_node)
        frame_type = self.unit_dict[ "numr" ].process_frame( frame_type, verb_node)
        frame_type = self.unit_dict[ "pass" ].process_frame( frame_type, verb_node)

        frame_type, frame_inst = \
                self.adding_missing_subjects( frame_type, frame_inst, verb_node)

        frame_type = self.unit_dict[ "nomi" ].process_frame( frame_type, verb_node)

        return frame_type, frame_inst

    def specific_postprocessing( self, frame_type):
        self.unit_dict[ "case" ].specific_postprocessing( frame_type)

class Csk_mdex_unit( Extraction_unit):
    """ FRM level unit """
    def node_is_inappropriate( self, node, _):
        if node.upos == "VERB" and node.lemma in self.extractor.modal_lemmas:
            for child_node in node.children:
                if "comp" in child_node.deprel:
                    self.frm_example_counter[ "" ] += 1
                    self.frm_example_counter[ node.lemma ] += 1
                    return True
        return False

class Csk_nomi_unit( Main_subj_unit):
    """ ARG level unit
    adds nominative to formless and elided subjects
    """
    def process_frame( self, frame_type, _):
        for arg in frame_type.args:
            if arg.form == "" and "nsubj" in arg.deprel:
                    arg.form = "Nom"
                    self.arg_example_counter[ "" ] += 1
                #elif "obj" in arg.deprel:
                #    # this includes "iobj" too
                #    arg.form = "Acc"
        return frame_type

    # def process_subj_elision( self, frame_type, frame_inst, elided_type_arg,
    #                           elided_inst_arg, subj_token, verb_node):
    #     """ """
    #     print("TU")
    #     self.arg_example_counter[ "elid_nom" ] += 1
    #     elided_type_arg.form = "Nom"
    #     return elided_type_arg, elided_inst_arg, subj_token

class Csk_numr_unit( Extraction_unit):
    """ ARG level unit
    resolves numerative genitives to nominatives or accusatives
    """
    def process_arg( self, frame_type_arg, arg_node, _):
        """ marks numerative """
        if arg_node.feats[ "Case" ] == "Gen":
            for child in arg_node.children:
                if child.deprel in [ "nummod:gov", "det:numgov" ]:
                    self.arg_example_counter[ "num" ] += 1
                    frame_type_arg.form = "Num"
        return frame_type_arg

    def process_frame( self, frame_type, _):
        """ resolves numerative """
        for arg in frame_type.args:
            if arg.form == "Num":
                self.arg_example_counter[ "total" ] += 1
                if frame_type.has_subject() and "nsubj" not in arg.deprel:
                    arg.form = "Acc"
                    self.arg_example_counter[ "acc" ] += 1
                else:
                    arg.form = "Nom"
                    self.arg_example_counter[ "nom" ] += 1
        return frame_type

class Csk_vadj_unit( Extraction_unit):
    """ FRM level unit
    inclusion of verbal adjectives
    """
    def node_is_appropriate( self, node, _):
        if node.upos == "ADJ" and node.feats[ "VerbForm" ] == "Part":
            self.frm_example_counter[ "total" ] += 1
            return True
        # for child_node in node.children:
        #     if "subj" in child_node.deprel or "aux" in child_node.deprel:
        #         subj_or_aux = True
        # if node.upos == "ADJ" and node.feats[ "VerbForm" ] == "Part":# and node.udeprel in [ "acl", "amod" ]:
        #     return True

    def node_is_good_arg( self, sent_node, verb_node, _):
        parent_node = verb_node.parent
        if sent_node is parent_node:
            subj_or_aux = False
            for child_node in verb_node.children:
                if "subj" in child_node.deprel or "aux" in child_node.deprel:
                    subj_or_aux = True
            if verb_node.upos == "ADJ" \
                    and verb_node.feats[ "VerbForm" ] == "Part" \
                    and verb_node.udeprel in [ "acl", "amod" ] \
                    and not subj_or_aux:
                self.frm_example_counter[ "attr_total" ] += 1
                return True

    def process_frame( self, frame_type, verb_node):
        if verb_node.upos == "ADJ" and verb_node.feats[ "VerbForm" ] == "Part":
            if verb_node.feats[ "Voice" ] == "Pass":
                self.frm_example_counter[ "pass_adj" ] += 1
            elif verb_node.feats[ "Voice" ] == "Act":
                self.frm_example_counter[ "act_adj" ] += 1
        return frame_type

    def process_arg( self, frame_type_arg, arg_node, verb_node):
        if verb_node.upos == "ADJ" \
                and verb_node.feats[ "VerbForm" ] == "Part" \
                and verb_node.udeprel in [ "acl", "amod" ] \
                and arg_node is verb_node.parent:
            if verb_node.feats[ "Voice" ] == "Pass":
                frame_type_arg.deprel = "nsubj:pass"
                self.frm_example_counter[ "attr_pass" ] += 1
            elif verb_node.feats[ "Voice" ] == "Act":
                frame_type_arg.deprel = "nsubj"
                #print( verb_node.form)
                self.frm_example_counter[ "attr_act" ] += 1
            frame_type_arg.form = "Nom"
            frame_type_arg.case_mark_rels = []
        return frame_type_arg

class Csk_pfin_unit( Extraction_unit):
    """ ARG level unit"""
    def process_arg( self, frame_type_arg, _, __):
        if frame_type_arg.form == "Part":
            self.arg_example_counter[ "" ] += 1
            frame_type_arg.form = "Fin"
        return frame_type_arg

class Csk_pass_unit( Extraction_unit):
    """ ARG level unit """
    def process_frame( self, frame_type, verb_node):
        frame_type = self.transform_proper_passive( frame_type, verb_node)
        frame_type = self.transform_reflex_passive( frame_type)
        return frame_type

    def transform_proper_passive( self, frame_type, verb_node):
        # has_aux = False
        # for child_node in verb_node.children:
        #     if child_node.lemma == self.extractor.verb_be and child_node.upos == "AUX":
        #         has_aux = True
        #         break
        # if has_aux and frame_type.verb_form == "Part" and frame_type.voice == "Pass":
        if frame_type.verb_form == "Part" and frame_type.voice == "Pass":
            self.frm_example_counter[ "proper-total" ] += 1
            nsubj_args = frame_type.get_arg( "nsubj:pass", "Nom", [])
            nsubj_args += frame_type.get_arg( "nsubj", "Nom", [])
            if nsubj_args != []:
                old_nsubj_arg = nsubj_args[ 0 ]
                obj_arg = self.extractor.frame_type_arg_class( "obj", "Acc", [])
                self.extractor.substitute_arg( old_nsubj_arg, obj_arg)
                self.frm_example_counter[ "proper-nsubj-obj" ] += 1

            csubj_args = frame_type.get_arg( "csubj:pass", None, None)
            csubj_args += frame_type.get_arg( "csubj", None, None)
            if csubj_args != []:
                old_csubj_arg = csubj_args[ 0 ]
                form = old_csubj_arg.form
                comp_arg = self.extractor.frame_type_arg_class( "ccomp", form, [])
                self.extractor.substitute_arg( old_csubj_arg, comp_arg)
                self.frm_example_counter[ "proper-csubj-ccomp" ] += 1

            obl_args = frame_type.get_arg( "obl:arg", "Ins", [])
            obl_args += frame_type.get_arg( "obl:agent", "Ins", [])
            obl_args += frame_type.get_arg( "obl", "Ins", [])
            nsubj_arg = self.extractor.frame_type_arg_class( "nsubj", "Nom", [])
            if obl_args != []:
                obl_arg = obl_args[ 0 ]
                self.extractor.substitute_arg( obl_arg, nsubj_arg)
                self.frm_example_counter[ "proper-obl-nsubj" ] += 1
        return frame_type

    def transform_reflex_passive( self, frame_type):
        """ transforming frames with reflexive passive construction to their active equivalent
        zahrada se kosi -> kosi zahradu
        expl:pass-Acc -> 0, nsubj:pass-Nom -> obj-Acc
        """
        expl_args = frame_type.get_arg( "expl:pass", "Acc", [])

        nsubj_args = frame_type.get_arg( "nsubj:pass", "Nom", [])
        nsubj_args += frame_type.get_arg( "nsubj", "Nom", [])
        csubj_args = frame_type.get_arg( "csubj:pass", None, [])
        csubj_args += frame_type.get_arg( "csubj", None, [])

        if expl_args != []:
            expl_arg = expl_args[ 0 ]
            self.frm_example_counter[ "reflex-total" ] += 1
            if nsubj_args != []:
                nsubj_arg = nsubj_args[ 0 ]
                obj_arg = self.extractor.frame_type_arg_class( "obj", "Acc", [])
                self.extractor.delete_arg( expl_arg)
                self.extractor.substitute_arg( nsubj_arg, obj_arg)
                self.frm_example_counter[ "reflex-nsubj-obj" ] += 1
            elif csubj_args != []:
                old_csubj_arg = csubj_args[ 0 ]
                form = old_csubj_arg.form
                comp_arg = self.extractor.frame_type_arg_class( "ccomp", form, [])
                self.extractor.delete_arg( expl_arg)
                self.extractor.substitute_arg( old_csubj_arg, comp_arg)
                self.frm_example_counter[ "reflex-csubj-ccomp" ] += 1

            obl_args = frame_type.get_arg( "obl:arg", "Ins", [])
            obl_args += frame_type.get_arg( "obl:agent", "Ins", [])
            obl_args += frame_type.get_arg( "obl", "Ins", [])
            nsubj_arg = self.extractor.frame_type_arg_class( "nsubj", "Nom", [])
            if obl_args != []:
                obl_arg = obl_args[ 0 ]
                self.extractor.substitute_arg( obl_arg, nsubj_arg)
                self.frm_example_counter[ "reflex-obl-nsubj" ] += 1

        return frame_type

class Csk_case_unit(Extraction_unit):
    """ ARG level unit """
    def specific_postprocessing( self, frame_type):
        """ resolving missing cases """
        if any( arg.form == "" for arg in frame_type.args):
            formless_args = [ arg for arg in frame_type.args if arg.form == "" ]
            verb_record = frame_type.verb_record
            best_inst_num = 0
            best_similar_frame = None
            for other_frame in verb_record.frame_types:
                if other_frame is not frame_type and \
                        self.frame_agr_except_args(
                                other_frame, frame_type, formless_args):
                    if len( other_frame.insts) > best_inst_num:
                        best_inst_num = len( other_frame.insts)
                        best_similar_frame = other_frame
            if best_similar_frame is not None:
                changed_frame_type = self.add_arg_forms( best_similar_frame,
                                                         frame_type, formless_args)
                verb_record.consider_merging( changed_frame_type)


    def frame_agr_except_args( self, frame_type_a, frame_type_b, formless_b_args):
        if len( frame_type_a.args) != len( frame_type_b.args):
            return False

        free_indices = [ True ] * len( frame_type_b.args)
        for arg_a in frame_type_a.args:
            for index, b_arg in enumerate( frame_type_b.args):
                deprel, form, case_mark_rels = arg_a.get_description()
                if b_arg in formless_b_args:
                    if free_indices[ index ] and \
                            b_arg.agrees_except_form( deprel, case_mark_rels):
                        free_indices[ index ] = False
                        break
                else:
                    if free_indices[ index ] and \
                            b_arg.agrees_with_desc( deprel, form, case_mark_rels):
                        free_indices[ index ] = False
                        break
            else:
                return False
        return True

    def add_arg_forms( self, frame_type_a, frame_type_b, formless_b_args):
        free_indices = [ True ] * len( frame_type_b.args)
        for arg_a in frame_type_a.args:
            for index, b_arg in enumerate( frame_type_b.args):
                deprel, form, case_mark_rels = arg_a.get_description()
                if b_arg in formless_b_args:
                    if free_indices[ index ] and \
                            b_arg.agrees_except_form( deprel, case_mark_rels):
                        free_indices[ index ] = False
                        b_arg.form = form
                        self.arg_example_counter[ form ] += 1
                        self.arg_example_counter[ "total" ] += 1
                        break
                else:
                    if free_indices[ index ] and \
                            b_arg.agrees_with_desc( deprel, form, case_mark_rels):
                        free_indices[ index ] = False
                        break
        return frame_type_b