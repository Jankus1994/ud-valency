from base_frame_extractor import Base_frame_extractor
from sent_token import Sent_token

class Frame_extractor( Base_frame_extractor):
    def __init__( self, modals="", **kwargs):
        """ called from Frame_aligner.__init__ """
        super().__init__( **kwargs)
        if self.config_dict[ "oblq" ]:
            self.appropriate_udeprels = [ "nsubj", "csubj", "obj", "iobj",
                                          "obl", "ccomp", "xcomp", "expl" ]

        if modals == "1":
            self.modals_inclusion = True
        elif modals == "0":
            self.modals_inclusion = False
        # othrewise it is left on language-specific decision
        self.modal_lemmas = []

        self.coord_args_num = 0

    def _after_sent( self, frame_type, frame_inst, verb_node):
        """ called from process_frame """
        if self.config_dict[ "subj" ]:
            frame_type, frame_inst = \
                    self.adding_missng_subjects( frame_type, frame_inst, verb_node)
        return frame_type, frame_inst

    def adding_missng_subjects( self, frame_type, frame_inst, verb_node):
        if not frame_type.has_subject():
            subj_token = Sent_token( None, "")
            subj_token.mark_elision()  # TODO rewrite with property
            elided_type_arg = self.frame_type_arg_class( "nsubj", "", [])
            elided_inst_arg = self.frame_inst_arg_class( "PRON")
            self.frame_examples_counter[ "subj_add" ] += 1

            elided_type_arg, elided_inst_arg, subj_token = \
                    self.process_subj_elision( frame_type, frame_inst,
                                               elided_type_arg, elided_inst_arg,
                                               subj_token, verb_node)

            frame_inst.add_elided_token( subj_token)
            self._connect_arg_with_frame( frame_type, frame_inst,
                                          elided_type_arg, elided_inst_arg,
                                          subj_token)

            assert frame_type.verb_record is None

        return frame_type, frame_inst

    def process_subj_elision( self, frame_type, frame_inst, elided_type_arg,
                              elided_inst_arg, subj_token, verb_node):
        """ for overloading """
        return elided_type_arg, elided_inst_arg, subj_token

    def _after_arg( self, frame_type_arg, frame_inst_arg, sent_node, verb_node):
        """ called from _process_sentence """
        if self.config_dict[ "coor" ]:
            if self._could_be_coord_arg( sent_node, verb_node):
                frame_inst_arg.is_coord_arg = True
                self.coord_args_num += 1
                self.arg_examples_counter[ "coord_possib" ] += 1
        return frame_type_arg, frame_inst_arg

    def _compl_conditions( self, sent_node, verb_node):
        """ called from _node_is_good_arg """
        return self._could_be_coord_arg(sent_node, verb_node)

    def _could_be_coord_arg( self, sent_node, verb_node):
        if self.config_dict[ "coor" ]:
            if verb_node.deprel == "conj":
                self.frame_examples_counter[ "conj" ] += 1
                coord_head_node = verb_node.parent
                if sent_node.parent is coord_head_node:
                    for child_node in verb_node.children:
                        if "subj" in child_node.deprel and "subj" in sent_node.deprel:
                            return False
                        if "obj" in child_node.deprel and "obj" in sent_node.deprel:
                            return False
                    before_coord = sent_node.ord < coord_head_node.ord and \
                                   sent_node.ord < verb_node.ord
                    after_coord = sent_node.ord > coord_head_node.ord and \
                                   sent_node.ord > verb_node.ord
                    return before_coord or after_coord
        return False

    def _process_arg( self, arg_node, verb_node):
        frame_type_arg, frame_inst_arg = \
                super()._process_arg( arg_node, verb_node)

        if self.config_dict[ "auxf" ]:
            frame_type_arg = self._consider_aux_form( frame_type_arg, arg_node)

        return frame_type_arg, frame_inst_arg

    def _consider_aux_form( self, frame_type_arg, arg_node):
        """ used in language specific modules """
        if "comp" in frame_type_arg.deprel or "csubj" in frame_type_arg.deprel:
                # and frame_type_arg.form == "Inf":
            aux_child_nodes = [ child_node for child_node in arg_node.children
                                if child_node.upos == "AUX" ]
            if aux_child_nodes != []:
                frame_type_arg.form = aux_child_nodes[ 0 ].feats[ "VerbForm" ]
                self.arg_examples_counter[ "aux_form_0" ] += 1
                if frame_type_arg.form != "Fin":
                    for aux_child_node in aux_child_nodes:
                        if aux_child_node.feats[ "VerbForm" ] == "Fin":
                            frame_type_arg.form = "Fin"
                            self.arg_examples_counter[ "aux_form_non_0" ] += 1
                            break
                    else:
                        self.arg_examples_counter[ "aux_form_0_nonfin" ] += 1

        return frame_type_arg

    def after_process_document( self, doc):  # void
        """ overriden block method - monolingual use case """
        if self.config_dict[ "coor" ]:
            self._coord_handling()
        #self._check_coherence()
        self._postprocessing()
        #self._check_coherence()
        if self.config_dict[ "oblq" ]:
            self._oblique_handling()

        for verb_record in self.dict_of_verbs.values():
            verb_record.build_frame_dag()

        if self.config_dict[ "frdc" ]:
            self._frame_reduction()

        #self._final_control()  # development method
        if self.config_dict[ "coun" ]:
            self._print_example_counts()
        if self.config_dict[ "outp" ]:
            self._output_result_dict()

    def _oblique_handling( self):
        value_triplets = []
        obl_dict = {}
        for verb_lemma in self.dict_of_verbs.keys():
            verb_record = self.dict_of_verbs[ verb_lemma ]
            for frame_type in verb_record.frame_types:
                for arg in frame_type.args:
                    if "obl" in arg.deprel:
                        if arg.deprel in [ "obl:arg", "obl:agent" ]:
                            continue
                        this_verb_portion = round( 100 *
                                self._arg_in_this_verb( verb_record, arg), 2)
                        all_verbs_portion = round( 100 *
                                self._arg_in_all_verbs( obl_dict, arg), 2)
                        value_triplets.append( ( arg, this_verb_portion, all_verbs_portion))
                        assert arg.frame_type.verb_record is not None
                        str_arg = str( arg).split( '-')[1]

                        #print( str_arg, this_verb_portion, all_verbs_portion, sep='\t')

        try:
            this_verb_portions = [ value for _, value, _ in value_triplets ]
            all_verbs_portions = [ value for _, _, value in value_triplets ]
            frame_type_args = [ arg for arg, _, _ in value_triplets ]
            avg_this = sum( this_verb_portions) / len( this_verb_portions)
            #print( median( this_values))
            avg_all = sum( all_verbs_portions) / len( all_verbs_portions)

            #print( median( all_values))
            results = { "-": 0, "?": 0, "+": 0 }
            for arg, this_verb_portion, all_verbs_portion in value_triplets:
                #assert arg.frame_type.verb_record is not None or arg.deleted
                if arg.deleted:
                    continue
                if this_verb_portion < avg_this and all_verbs_portion > avg_all:
                    #arg.definitive = 2
                    self._delete_arg( arg)
                    results[ "-" ] += 1
                    self.arg_examples_counter[ "obl_adj"] += 1
                elif this_verb_portion < avg_this or all_verbs_portion > avg_all:
                    arg.definitive = False
                    self._delete_arg( arg)
                    results[ "?" ] += 1
                    self.arg_examples_counter[ "obl_unk"] += 1
                else:  #if this_verb_portion > avg_this and all_verbs_portion < avg_all:
                    #self._delete_arg( arg)
                    results[ "+" ] += 1
                    self.arg_examples_counter[ "obl_arg"] += 1
            #print( results)
        except ZeroDivisionError:
            pass

    def _arg_in_all_verbs( self, deprel_dict, arg):
        arg_str = arg.to_str()
        if arg_str in deprel_dict:
            avg_occur_portion = deprel_dict[ arg_str ]
        else:
            sum_occur_portion = 0
            for verb_lemma in self.dict_of_verbs.keys():
                verb_record = self.dict_of_verbs[ verb_lemma ]
                occur_portion = self._arg_in_this_verb( verb_record, arg)
                sum_occur_portion += occur_portion
            verbs_num = len( self.dict_of_verbs)
            avg_occur_portion = sum_occur_portion / verbs_num
            deprel_dict[ arg_str ] = avg_occur_portion
            #print( arg_str, round( 100 * avg_occur_portion, 3), sep='\t')
        return avg_occur_portion

    def _arg_in_this_verb( self, verb_record, arg):
        all_occurences = 0
        arg_occurences = 0
        for frame_type in verb_record.frame_types:
            insts_num = len( frame_type.insts)
            all_occurences += insts_num
            deprel, form, case_mark_rels = arg.get_description()
            found_args = frame_type.get_arg( deprel, form, case_mark_rels)
            if found_args != []:
                arg_occurences += insts_num
        occurences_portion = arg_occurences / all_occurences
        return occurences_portion

    def _coord_handling( self):
        num_of_successes = 0
        for verb_record in self.dict_of_verbs.values():
            frames_by_arg_num = sorted( verb_record.frame_types,
                    key=lambda frame_type : len( frame_type.args), reverse=True)
            for frame_type in frames_by_arg_num:
                success = frame_type.try_delete_coord_args()
                if success:
                    self.arg_examples_counter[ "coord_del" ] += 1
                    num_of_successes += 1
                    verb_record.consider_merging( frame_type)

    def _postprocessing( self):
        for verb_record in self.dict_of_verbs.values():
            for frame_type in verb_record.frame_types:
                self.specific_postprocessing( frame_type)

    def specific_postprocessing( self, frame_type):
        pass

    def _frame_reduction( self, only_obl=True):
        for verb_record in self.dict_of_verbs.values():
            verb_record.frame_reduction( only_obl)  # reducing number of frames before outputting
            #verb_record.frame_reduction( False)