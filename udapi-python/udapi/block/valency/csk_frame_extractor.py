from frame_extractor import Frame_extractor
from sent_token import Sent_token
from collections import Counter

# config dict codes used
#	mdin	inclusion of modal verbs
#	elis	further processing of added (previously elided) subjects
#	subj	adding missing nominative to subjects
#	vadj	creating valency frames also for verbal adjectives, including their head as argument
#	pfin	replacing "Part" VerbFrom with "Fin"
#	pass	depassivization (both proper and reflexive)
#	numr	replacing numerative genitives with nominatives or accusatives
#	auxf	replacing form of clausal arguments with "Fin" if they have an auxiliary with "Fin"

class Csk_frame_extractor( Frame_extractor):

    config_codes = [ "elis", "subj", "vadj", "pfin", "pass", "numr", "auxf", "mdin" ]

    def __init__( self, **kwargs):
        self.modals_inclusion = True

        super().__init__( **kwargs)

        if not self.modals_inclusion:
            self.config_dict[ "mdin" ] = False
        self.elid_pron_counter = Counter()

        self.pron_sg1 = ""
        self.pron_sg2 = "ty"
        self.pron_pl1 = "my"
        self.pron_pl2 = "vy"
        self.verb_be = ""

        self.filling_cases = [ "Acc", "Gen", "Dat", "Loc", "Ins" ]



    def _node_is_appropriate( self, node):
        result = super()._node_is_appropriate( node)
        if self.config_dict[ "vadj" ]:
            if node.upos == "ADJ" and node.feats[ "VerbForm" ] == "Part":
                self.frame_examples_counter["part_incl"] += 1
                return True
        if node.upos == "VERB" and node.lemma in self.modal_lemmas:
            for child_node in node.children:
                if "comp" in child_node.deprel:
                    self.frame_examples_counter["modals"] += 1
                    if not self.config_dict[ "mdin" ]:
                        return False
                    break
        return result

    def _node_is_good_arg( self, sent_node, verb_node):
        result = super()._node_is_good_arg( sent_node, verb_node)
        if self.config_dict[ "vadj" ]:
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
                    return True
        return result


    def _process_arg( self, arg_node, verb_node):
        frame_type_arg, frame_inst_arg = super()._process_arg( arg_node, verb_node)
        if self.config_dict[ "numr" ]:
            if arg_node.feats[ "Case" ] == "Gen":
                for child in arg_node.children:
                    if child.deprel in [ "nummod:gov", "det:numgov" ]:
                        self.arg_examples_counter["numerative"] += 1
                        frame_type_arg.form = "Num"
        # if self.spec_allowed[ "copula_comps" ]:
        #     if "comp" in frame_type_arg.deprel:
        #         if frame_type_arg.form == "":
        #             for child_node in arg_node.children:
        #                 if child_node.lemma == self.verb_be:
        #                     frame_type_arg.form = child_node.feats[ "VerbForm" ]
        if self.config_dict[ "auxf" ]:
            frame_type_arg = self._consider_aux_form( frame_type_arg, arg_node)
        if self.config_dict[ "pfin" ]:
            if frame_type_arg.form == "Part":
                self.arg_examples_counter["part_fin"] += 1
                frame_type_arg.form = "Fin"
        if self.config_dict[ "vadj" ]:
            if verb_node.upos == "ADJ" \
                    and verb_node.feats[ "VerbForm" ] == "Part" \
                    and verb_node.udeprel in [ "acl", "amod" ] \
                    and arg_node is verb_node.parent:
                if verb_node.feats[ "Voice" ] == "Pass":
                    frame_type_arg.deprel = "nsubj:pass"
                    self.arg_examples_counter[ "pass_adj" ] += 1
                elif verb_node.feats[ "Voice" ] == "Act":
                    frame_type_arg.deprel = "nsubj"
                    self.arg_examples_counter[ "act_adj" ] += 1
                frame_type_arg.form = "Nom"
                frame_type_arg.case_mark_rels = []

        return frame_type_arg, frame_inst_arg

    def _process_frame( self, verb_node):
        frame_type, frame_inst = super()._process_frame( verb_node)
        if self.config_dict[ "subj" ]:
            frame_type = self.add_subj_nom(frame_type)

        if self.config_dict[ "numr" ]:
            frame_type = self._finalize_numerative( frame_type)

        if self.config_dict[ "vadj" ]:
            self.participles_parents( frame_type, frame_inst, verb_node)

        if self.config_dict[ "pass" ]:
            frame_type = self.transform_proper_passive( frame_type, verb_node)
            frame_type = self.transform_reflex_passive( frame_type)

        # if self.spec_allowed[ "infin" ]:
        #     arg_deprels = [ arg.deprel for arg in frame_type.args ]
        #     if verb_node.feats[ "VerbForm" ] == "Inf" and not "nsubj" in arg_deprels:
        #         frame_type, frame_inst = self._handle_subjectless_infinitive(
        #                     frame_type, frame_inst, verb_node)

        # if self.config_dict[ "elis" ]:
        #     frame_type, frame_inst = self.process_elided_args(
        #             frame_type, frame_inst, verb_node)

        frame_type, frame_inst = \
                self.adding_missng_subjects( frame_type, frame_inst, verb_node)

        if self.config_dict[ "subj" ]:
            frame_type = self.add_subj_nom(frame_type)

        return frame_type, frame_inst

    # def _verb_is_modal(self, verb_node):
    #     # modal verb with a child in infinitive -> not creating a frame
    #     if verb_node.lemma in self.modal_lemmas:
    #         for child in verb_node.children:
    #             if child.feats[ "VerbForm" ] == "Inf":
    #                 #print( "*** ", verb_node.lemma, child.lemma)
    #                 return True  # modal verb -> frame should not be created
    #     return False  # verb is not modal

    # def _verb_is_child_of_modal(self, frame_type, verb_node):
    #     # infinitive without subject and with a modal head with subject ->
    #     # -> adding the subject into this node's frame
    #     arg_deprels = [ arg.deprel for arg in frame_type.args ]
    #     if verb_node.feats[ "VerbForm" ] == "Inf" and not "nsubj" in arg_deprels:
    #         parent_node = verb_node.parent
    #         if parent_node.lemma in self.modal_lemmas:
    #             return True  # verb is infinitive child of modal verb
    #     return False

    # def _handle_subjectless_infinitive( self, frame_type, frame_inst, verb_node): # -> bool
    #     """ adds the subject of the modal is added to this verb's frame
    #     returs bool if this verb is modal
    #     """
    #     parent_node = verb_node.parent
    #     if parent_node.upos == "VERB":
    #         parent_frame_type, parent_frame_inst = \
    #                 super()._process_frame( parent_node)
    #         for parent_arg in parent_frame_type.args:
    #             if parent_arg.deprel == "nsubj":
    #                 subject_arg_type = parent_arg
    #                 subject_arg_inst = parent_arg.insts[ 0 ]
    #
    #                 # TODO maybe move to inst arg?
    #                 subject_ord = subject_arg_inst.token.ord
    #                 subject_token = [ token for token in frame_inst.sent_tokens
    #                                   if token.ord == subject_ord ][ 0 ]
    #                 self._connect_arg_with_frame(frame_type, frame_inst,
    #                                              subject_arg_type, subject_arg_inst, subject_token)
    #                 #print( ">>> ", verb_node.lemma, parent_node.lemma)
    #                 frame_inst.has_modal = True
    #                 break
    #     return frame_type, frame_inst

    def participles_parents( self, frame_type, frame_inst, verb_node):
        if verb_node.upos == "ADJ" and verb_node.feats[ "VerbForm" ] == "Part" \
                and not frame_type.has_subject and verb_node.deprel.startswith( "acl"):
            parent_node = verb_node.parent
            nsubj_type_arg, nsubj_inst_arg = \
                    self._process_arg( parent_node, verb_node)
            nsubj_arg = self.frame_type_arg_class( "nsubj", "Nom", [])

    def process_subj_elision( self, frame_type, frame_inst, elided_type_arg,
                              elided_inst_arg, subj_token, verb_node):
        if self.config_dict[ "elis" ]:
            self.arg_examples_counter["elid_nom"] += 1
            elided_type_arg.form = "Nom"

            # DOPLNENIE PODMETOV ASI ZRUSENE
            # subj_token.form = self.try_getting_person_1_2( verb_node)
            # if subj_token.form == "":
            #     # looking for an auxiliary verb, which would confirm the 1./2. person
            #     for child_node in verb_node.children:
            #         if child_node.upos == "AUX":
            #             subj_token.form = self.try_getting_person_1_2( child_node)
            #             break
            # if subj_token.form == "":
            #     subj_token.form = self.try_getting_person_3( verb_node)

            # this should be already handled by modal verbs
            # if subj_token is None:
            #     # the node can be a complement of a parent verb, which could confirm the 1./2. person
            #     if verb_node.deprel == "xcomp" and verb_node.parent.upos == "VERB":
            #         token_person_1_2 = self.try_getting_person_1_2( verb_node.parent)
            self.elid_pron_counter[ subj_token.form ] += 1

        return elided_type_arg, elided_inst_arg, subj_token

    def try_getting_person_1_2( self, verb_node):
        token_form = ""
        if verb_node.feats[ "Person" ] == "1":
            if verb_node.feats[ "Number" ] == "Sing":
                token_form = "1sg:" + self.pron_sg1
            elif verb_node.feats[ "Number" ] == "Plur":
                token_form = "1pl:" + self.pron_pl1
        elif verb_node.feats[ "Person" ] == "2":
            if verb_node.feats[ "Number" ] == "Sing":
                token_form = "2sg:" + self.pron_sg2
            elif verb_node.feats[ "Number" ] == "Plur":
                token_form = "2pl:" + self.pron_pl2
        return token_form

    @staticmethod
    def try_getting_person_3( verb_node):
        """ overloaded in cs/sk module"""
        token_form = "3prs"
        return token_form

    def transform_proper_passive( self, frame_type, verb_node):
        has_aux = False
        for child_node in verb_node.children:
            if child_node.lemma == self.verb_be and child_node.upos == "AUX":
                has_aux = True
                break
        if has_aux and frame_type.verb_form == "Part" and frame_type.voice == "Pass":
            nsubj_args = frame_type.get_arg( "nsubj:pass", "Nom", [])
            nsubj_args += frame_type.get_arg( "nsubj", "Nom", [])
            if nsubj_args != []:
                old_nsubj_arg = nsubj_args[ 0 ]
                obj_arg = self.frame_type_arg_class( "obj", "Acc", [])
                self._substitute_arg( old_nsubj_arg, obj_arg)
                self.frame_examples_counter[ "passive-nsubj-obj" ] += 1

            csubj_args = frame_type.get_arg( "csubj:pass", None, None)
            csubj_args += frame_type.get_arg( "csubj", None, None)
            if csubj_args != []:
                old_csubj_arg = csubj_args[ 0 ]
                form = old_csubj_arg.form
                comp_arg = self.frame_type_arg_class( "ccomp", form, [])
                self._substitute_arg( old_csubj_arg, comp_arg)
                self.frame_examples_counter[ "passive-csubj-ccomp" ] += 1

            obl_args = frame_type.get_arg( "obl:arg", "Ins", [])
            obl_args += frame_type.get_arg( "obl:agent", "Ins", [])
            obl_args += frame_type.get_arg( "obl", "Ins", [])
            nsubj_arg = self.frame_type_arg_class( "nsubj", "Nom", [])
            if obl_args != []:
                obl_arg = obl_args[ 0 ]
                self._substitute_arg( obl_arg, nsubj_arg)
                self.frame_examples_counter["passive-obl-nsubj"] += 1
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
            if nsubj_args != []:
                nsubj_arg = nsubj_args[ 0 ]
                obj_arg = self.frame_type_arg_class( "obj", "Acc", [])
                self._delete_arg( expl_arg)
                self._substitute_arg( nsubj_arg, obj_arg)
                self.frame_examples_counter["passive-reflex-n"] += 1
            elif csubj_args != []:
                old_csubj_arg = csubj_args[ 0 ]
                form = old_csubj_arg.form
                comp_arg = self.frame_type_arg_class( "ccomp", form, [])
                self._delete_arg( expl_arg)
                self._substitute_arg( old_csubj_arg, comp_arg)
                self.frame_examples_counter["passive-reflex-c"] += 1


        return frame_type

    def add_subj_nom(self, frame_type):
        for arg in frame_type.args:
            if arg.form == "":
                if "nsubj" in arg.deprel:
                    arg.form = "Nom"
                    self.arg_examples_counter["cases-nom"] += 1
                #elif "obj" in arg.deprel:
                #    # this includes "iobj" too
                #    arg.form = "Acc"
        return frame_type

    def _finalize_numerative( self, frame_type):
        for arg in frame_type.args:
            if arg.form == "Num":
                if frame_type.has_subject() and "nsubj" not in arg.deprel:
                    arg.form = "Acc"
                    self.arg_examples_counter["numer-acc"] += 1
                else:
                    arg.form = "Nom"
                    self.arg_examples_counter["numer-nom"] += 1
        return frame_type

    def after_process_document( self, doc):  # void
        super().after_process_document( doc)

    def specific_postprocessing( self, frame_type):
        if self.config_dict["cases"]:
            self.resolve_missing_cases( frame_type)


    def resolve_missing_cases( self, frame_type):
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
                        self.arg_examples_counter["cases2-" + form] += 1
                        break
                else:
                    if free_indices[ index ] and \
                            b_arg.agrees_with_desc( deprel, form, case_mark_rels):
                        free_indices[ index ] = False
                        break
        return frame_type_b

    def _print_example_counts( self):
        super()._print_example_counts()
        print( self.elid_pron_counter)