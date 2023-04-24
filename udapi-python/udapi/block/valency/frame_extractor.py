import sys

from udapi.core.block import Block
import pickle
import inspect
from verb_record import Verb_record
from frame_type import Frame_type
from frame_inst_arg import Frame_inst_arg
from frame_type_arg import Frame_type_arg
from frame_inst import Frame_inst
from sent_token import Sent_token
from dict_printer import Dict_printer
from collections import defaultdict, Counter
from random import seed, sample

class Frame_extractor( Block):
    """ object for monolingual frame extraction
    extracts frames from each verb node

    may be overloaded with language-specific extractors
        redefining appropropriate (u)deprels and genereal classes in __init__
        the rest of extractor is designed language-independent to remain untouched

    2 use cases:
    monolingual - used as separate block
    output: pickle or text

    bilingual - used as tool of frame_aligner
    output: frame_insts from each sentece, dict
    """

    config_codes = []  # overloaded

    def __init__( self, output_form="text", output_name="", modals="",
                  config_name="", **kwargs):
        """ called from Frame_aligner.__init__ """
        super().__init__( **kwargs)
        self.appropriate_udeprels = \
                [ "nsubj", "csubj", "obj", "iobj", "obl", "ccomp", "xcomp", "expl" ]
        #self.appropriate_deprels = [ "obl:arg", "obl:agent" ]  # !! move to Czech module
        #self.possible_udeprels = [ "obl" ]
        self.appropriate_child_rels = [ "case", "mark" ]

        self.lang_mark = ""

        self.verb_record_class = Verb_record
        self.frame_type_class = Frame_type
        self.frame_inst_class = Frame_inst
        self.frame_type_arg_class = Frame_type_arg
        self.frame_inst_arg_class = Frame_inst_arg


        self.dict_of_verbs = {}

        self.verb_records = []
        self.frame_types = []
        self.frame_insts = []
        self.frame_type_args = []
        self.frame_inst_args = []
        self.sent_and_elid_tokens = []

        # output form - used in after_process_document
        self.output_form = output_form
        self.output_name = output_name

        self.config_dict = defaultdict( bool)
        for config_code in self.config_codes:
            self.config_dict[ config_code ] = True
        if config_name:
            self.process_config_file( config_name)

        if modals == "1":
            self.modals_inclusion = True
        elif modals == "0":
            self.modals_inclusion = False
        # othrewise it is left on language-specific decision
        self.modal_lemmas = []

        self.coord_args_num = 0
        self.frame_examples_counter = Counter()
        self.arg_examples_counter = Counter()

    def process_config_file( self, config_name):
        with open( config_name, 'r') as config_file:
            for line in config_file:
                if line.rstrip( '\n') == "" or line.startswith( '#'):
                    continue
                value, precode, _ = line.split( '\t')
                code = precode
                if ':' in precode:
                    _, code = precode.split( ':', 1)
                self.config_dict[ code ] = bool( int( value))

    def process_tree( self, tree):  # -> list of Frame_inst
        """ called as a Block method (monolingual use case)
        or from Frame_aligner.process_bundle
        """
        frame_insts = []
        for node in tree.descendants:
            frame_inst = self._process_node( node)
            if frame_inst is not None:
                frame_insts.append( frame_inst)
        bundle_id = tree.bundle.bundle_id
        for index, frame_inst in enumerate( frame_insts):
            frame_inst.bundle_id = bundle_id
            frame_inst.index = index
        #self._check_coherence()
        return frame_insts

    def _process_node( self, node):  # -> Frame_inst
        """ called from process_tree
        searching verbs and calling create_frame for them
        """
        if self._node_is_appropriate( node):
            if node.lemma in self.dict_of_verbs:
                verb_record = self.dict_of_verbs[ node.lemma ]
            else:
                verb_record = self.verb_record_class( node.lemma)
                self.dict_of_verbs[ node.lemma ] = verb_record
            frame_type, frame_inst = self._process_frame( node)

            # adding the frame to the verb_record
            verb_record.consider_new_frame_type( frame_type)

            return frame_inst
        #elif node.upos == "AUX":
        #    parent_node == node.parent
        #    if parent_node.upos in [ "NOUN", "PRON", "I
        return None

    def _node_is_appropriate( self, node):
        return node.upos == "VERB"

    def _process_frame( self, verb_node):  # -> Frame_inst
        """ called from process_node """
        # new frame
        frame_type = self.frame_type_class( self.appropriate_udeprels)
        frame_type.set_verb_features( verb_node)
        frame_inst = self.frame_inst_class()

        # creating and adding args to the frame type/inst
        # creating tokens for example sentence and adding them to frame_inst
        frame_type, frame_inst = self._process_sentence( frame_type, frame_inst, verb_node)

        frame_type, frame_inst = \
                self.adding_missng_subjects( frame_type, frame_inst, verb_node)

        frame_type.sort_args()
        frame_type.add_inst( frame_inst)  # connection between frame type and inst

        return frame_type, frame_inst

    def _process_sentence( self, frame_type, frame_inst, verb_node):
        """ called from _process_frame
        has several aims:
        - create tokens for being able to reconstruct the example sentcence
        when the dictionary with examples is displayed
        - choose frame arguments according to given requirements
        and connect them with frame objects (both type and inst)
        - create connection between tokens and arguments, so these tokens can be
        marked as arguments when displayed
        """
        sent_nodes = verb_node.root.descendants
        sent_tokens = []
        for sent_node in sent_nodes:
            # sentence tokens
            token = self._create_token( sent_node)
            if sent_node is verb_node:
                token.mark_frame_predicate()
            sent_tokens.append( token)

            # frame arguments
            if self._node_is_good_arg( sent_node, verb_node):
                #if sent_node.udeprel in self.appropriate_udeprels or \
                #        sent_node.deprel in self.appropriate_deprels:
                frame_type_arg, frame_inst_arg = \
                        self._process_arg( sent_node, verb_node)
                # if sent_node.udeprel == "obl":
                #     # oblique args may or may not be a part of the frame
                #     # will be decided later -> not definitive
                #     frame_inst_arg.definitive = False
                if self._could_be_coord_arg( sent_node, verb_node):
                    frame_inst_arg.is_coord_arg = True
                    self.coord_args_num += 1
                    self.arg_examples_counter[ "coord_possib"] += 1
                self._connect_arg_with_frame( frame_type, frame_inst,
                                              frame_type_arg, frame_inst_arg,
                                              token)

        frame_inst.sent_tokens = sent_tokens
        frame_inst.verb_node_ord = verb_node.ord
        verb_parent_node = verb_node.parent
        if verb_parent_node is not None:
            frame_inst.verb_parent_ord = verb_parent_node.ord
            frame_inst.verb_parent_upos = verb_parent_node.upos
        frame_inst.verb_deprel = verb_node.deprel
        frame_inst.verb_depth = int( verb_node.get_attrs( [ "depth" ])[ 0 ])
        frame_inst.verb_child_num = int( verb_node.get_attrs( [ "children" ])[ 0 ])

        return frame_type, frame_inst

    def _node_is_good_arg( self, sent_node, verb_node):
        is_arg = sent_node.parent is verb_node or \
                self._could_be_coord_arg(sent_node, verb_node)
        #is_arg = sent_node.parent is verb_node
        ok_deprel = sent_node.udeprel in self.appropriate_udeprels

        result = is_arg and ok_deprel
        return result

    def _could_be_coord_arg( self, sent_node, verb_node):
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
                return  before_coord or after_coord
        return False

    def _process_arg( self, arg_node, verb_node):
        deprel, form, child_rels, upostag = self._get_arg_features( arg_node)
        frame_type_arg = self.frame_type_arg_class(
                            deprel, form, child_rels)
        frame_inst_arg = self.frame_inst_arg_class( upostag)
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
                self.arg_examples_counter["aux_form_0"] += 1
                if frame_type_arg.form != "Fin":
                    for aux_child_node in aux_child_nodes:
                        if aux_child_node.feats[ "VerbForm" ] == "Fin":
                            frame_type_arg.form = "Fin"
                            self.arg_examples_counter["aux_form_non_0"] += 1
                            break
                    else:
                        self.arg_examples_counter["aux_form_0_nonfin"] += 1

        return frame_type_arg

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

    @staticmethod
    def _connect_arg_with_frame( frame_type, frame_inst,
                                 frame_type_arg, frame_inst_arg, token):
        token.arg = frame_inst_arg
        frame_inst.add_arg( frame_inst_arg)
        frame_type_arg.add_inst( frame_inst_arg)
        frame_type.add_arg( frame_type_arg)

    @staticmethod
    def _delete_arg( frame_type_arg):
        frame_type = frame_type_arg.frame_type
        verb_record = frame_type.verb_record
        frame_type_arg.delete()
        if verb_record is not None:
            verb_record.consider_merging( frame_type)

        # frame_type = frame_type_arg.frame_type
        #
        # #assert frame_type is not None
        # #assert frame_type_arg in frame_type.args
        # frame_type.remove_arg( frame_type_arg)
        #
        # for frame_inst_arg in frame_type_arg.insts:
        #     #assert frame_inst_arg.type is frame_type_arg
        #     frame_inst = frame_inst_arg.frame_inst
        #     #assert frame_inst is not None
        #     #assert frame_inst.type is frame_type
        #     #assert frame_inst_arg in frame_inst.args
        #     frame_inst.remove_arg( frame_inst_arg)
        #
        #     sent_token = frame_inst_arg.token
        #     #assert sent_token is not None
        #     #assert sent_token in frame_inst.sent_tokens + frame_inst.elided_tokens
        #     #assert sent_token.arg is frame_inst_arg
        #     sent_token.arg = None
        #
        # frame_type_arg.deleted = True

    # @staticmethod
    # def _disconnect_arg_from_frame( frame_type, frame_type_arg):
    #     Frame_extractor._delete_arg(frame_type_arg)
    #     return frame_type_arg
    #
    #     removed_arg = frame_type.pop_arg( frame_type_arg)
    #
    #     for frame_inst_arg in removed_arg.insts:
    #         frame_inst_arg.token.arg = None
    #         try:
    #             frame_inst_arg.frame_inst.remove_arg( frame_inst_arg)
    #             frame_type_arg.removed = True
    #         except AttributeError:
    #             print( frame_inst_arg.used, frame_type_arg.removed)
    #             exit()
    #     return removed_arg

    @staticmethod
    def _substitute_arg( old_frame_arg, new_frame_arg):
        frame_type = old_frame_arg.frame_type
        #assert frame_type is not None
        #assert old_frame_arg in frame_type.args
        frame_type.remove_arg( old_frame_arg)

        for frame_inst_arg in old_frame_arg.insts:
            #assert frame_inst_arg.type is old_frame_arg
            new_frame_arg.add_inst( frame_inst_arg)  # incl reversed link

        frame_type.add_arg( new_frame_arg)  # incl reversed link

        verb_record = frame_type.verb_record
        if verb_record is not None:
            verb_record.consider_merging( frame_type)

        old_frame_arg.deleted = True

    def _create_token( self, token_node):  # -> Token
        """ called from _process_sentence
        creation and basic initialization of token
        """
        token = Sent_token( token_node.ord, token_node.form)

        no_space_after = token_node.no_space_after #or node is sentence_nodes[ -1 ]
        if no_space_after:
            token.unmark_space()  # space is default otherwise
        return token

    def _udeprel_is_appropriate( self, udeprel):  # -> bool
        if udeprel in self.appropriate_udeprels:
            return

    def _get_arg_features( self, node):  # -> tuple ( string, string, list of strings )
        """ called from _process_sentence """
        deprel = node.deprel

        form = node.feats[ "Case" ]
        if form in [ "", "0" ]:
            form = node.feats[ "VerbForm"]
        if form == "0":
            form = ""

        child_rels = []
        for child in node.children:
            if child.deprel in self.appropriate_child_rels:
                child_rel = child.deprel + '-' + child.lemma
                child_rels.append( child_rel)

        upostag = node.upos

        return deprel, form, child_rels, upostag

    def get_dict_of_verbs( self):  # -> dict
        """ called from Frame_aligner._pickle_dict """
        return self.dict_of_verbs



    def after_process_document( self, doc):  # void
        """ overriden block method - monolingual use case"""
        if self.config_dict[ "coord" ]:
            self._coord_handling()
        self._check_coherence()
        self._postprocessing()
        self._check_coherence()
        if self.config_dict[ "obliq" ]:
            self._oblique_handling()
        self._check_coherence()

        for verb_record in self.dict_of_verbs.values():
            #verb_record.sort_frames()
            verb_record.build_frame_dag()
        #self._frame_reduction()
        self._check_coherence()
        self._final_control()
        self._print_example_counts()

        Dict_printer.print_dict( self.output_form, self.dict_of_verbs, self.output_name)
        #Dict_printer.print_verbs_by_arg_form( self.dict_of_verbs, "Dat")

    def _check_coherence( self):
        for verb_lemma in self.dict_of_verbs.keys():
            verb_record = self.dict_of_verbs[ verb_lemma ]
            verb_record.check_coherence()

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
                    self.arg_examples_counter[ "obl_???"] += 1
                else:  #if this_verb_portion > avg_this and all_verbs_portion < avg_all:
                    #self._delete_arg( arg)
                    results[ "+" ] += 1
                    self.arg_examples_counter[ "obl_arg"] += 1
            print( results)
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

#    def _decide_obl_inclusion( self, this_verb_portion, all_verbs_portion):

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

    def _final_control( self):
        formless_args_num = 0
        frame_num = 0
        for verb_record in self.dict_of_verbs.values():
            frame_num += len( verb_record.frame_types)
            for frame_type in verb_record.frame_types:
                for arg in frame_type.args:
                    if arg.form == "":
                        formless_args_num += 1
        print( formless_args_num, frame_num)

        #
        # # superframe counter
        # frame_num = 0
        # supernum_counter = Counter()
        # for verb_record in self.dict_of_verbs.values():
        #     frame_num += len( verb_record.frame_types)
        #     for frame_type in verb_record.frame_types:
        #         supernum_counter[ len( frame_type.superframes) ] += 1
        # print( frame_num)
        # print( supernum_counter)


        # insts = []
        # for verb_record in self.dict_of_verbs.values():
        #     for frame_type in verb_record.frame_types:
        #         for frame_inst in frame_type.insts:
        #             insts.append( frame_inst)
        # new_dict = {}
        # chosen_insts = sample( insts, 100)
        # dict_copy = self.dict_of_verbs.copy()
        # for verb_record in dict_copy.values():
        #     frames_copy = verb_record.frame_types.copy()
        #     for frame_type in frames_copy:
        #         insts_copy = frame_type.insts.copy()
        #         for inst in insts_copy:
        #             if inst not in chosen_insts:
        #                 frame_type._insts.remove( inst)
        #         if frame_type.insts == []:
        #             verb_record.remove_frame( frame_type)
        #     if verb_record.frame_types == []:
        #         self.dict_of_verbs.pop( verb_record.lemma)
        # instsnum = 0
        # for verb_record in new_dict.values():
        #     for frame_type in verb_record.frame_types:
        #         for frame_inst in frame_type.insts:
        #             instsnum += 1
        # print( instsnum, len( chosen_insts))
        Dict_printer.print_dict( self.output_form, self.dict_of_verbs, self.output_name)



        # multisubj = Counter()
        # dict_copy = self.dict_of_verbs.copy()
        # for verb_record in dict_copy.values():
        #     frames_copy = verb_record.frame_types.copy()
        #     for frame_type in frames_copy:
        #         subj_num = 0
        #         for arg in frame_type.args:
        #             if "csubj:pass" in arg.deprel:
        #                 pass #print("tu")
        #                 #subj_num += 1
        #         #if subj_num <= 1:
        #         #    verb_record._frame_types.remove( frame_type)
        #             #multisubj[ subj_num ] += len( frame_type.insts)
        #     #if verb_record.frame_types == []:
        #     #    self.dict_of_verbs.pop( verb_record.lemma)
        #for item in multisubj.most_common():
        #    print( item)
        # formless_args = Counter()
        # dict_copy = self.dict_of_verbs.copy()
        # for verb_record in dict_copy.values():
        #     frames_copy = verb_record.frame_types.copy()
        #     for frame_type in frames_copy:
        #         for frame_type_arg in frame_type.args:
        #             if frame_type_arg.form == "":
        #                 #print( frame_type_arg.deprel, frame_type_arg.case_mark_rels)
        #                 formless_args[ frame_type_arg.to_str() ] += \
        #                         len( frame_type_arg.insts)
        #                 break
        #         else:
        #             verb_record._frame_types.remove( frame_type)
        #     if verb_record.frame_types == []:
        #         self.dict_of_verbs.pop( verb_record.lemma)
        # for item in formless_args.most_common():
        #     print( item)

    def _print_example_counts( self):
        frame_inst_count = 0
        arg_inst_count = 0
        for verb_record in self.dict_of_verbs.values():
            for frame_type in verb_record.frame_types:
                insts_count = len( frame_type.insts)
                frame_inst_count += insts_count
                arg_inst_count += len( frame_type.args) * insts_count

        print( "\nframe insts:", frame_inst_count)
        for key, val in self.frame_examples_counter.items():
            print( key, val, round( val / frame_inst_count * 100, 1))

        print( "\narg insts:", arg_inst_count)
        for key, val in self.arg_examples_counter.items():
            print( key, val, round( val / arg_inst_count * 100, 1))


    # def delete_subframes( self):
    #     """ called from after_process_document on each verb record
    #     delete all frames that are a
    #     TODO rozmysli si, co vlastne chces, ci mazat subframy ci superframy
    #     """
    #     frame_types = sorted( self.frame_types, key = \
    #             lambda type:type.args_to_one_string())
    #     reduced_frame_types = []
    #     # comparing frames and marking those to delete
    #     for frame_type in frame_types:
    #         # a frame should be deleted if it has a superframe
    #         best_superframe = frame_type
    #         for potential_superframe in frame_types:
    #             if potential_superframe.superframe is not None:
    #                 continue
    #             if best_superframe.is_subframe_of( potential_superframe) \
    #                     and self.freq_ratio_is_sufficient(
    #                             best_superframe, potential_superframe):
    #                 best_superframe = potential_superframe
    #         if best_superframe is not frame_type:
    #             frame_type.superframe = best_superframe
    #
    #     reduced_frame_types = []
    #     for frame_type in frame_types:
    #         if frame_type.superframe is None:
    #             for subframe in frame_type.subframes:
    #                 for inst in subframe.insts:
    #                     frame_type.add_inst( inst)
    #             reduced_frame_types.append( frame_type)
    #             frame_type.subframes = []  # the subframes will be deleted
    #
    #     self.frame_types = reduced_frame_types
    #
    # @staticmethod
    # def freq_ratio_is_sufficient( subframe, superframe): # -> bool
    #     """ comparing number of instances of a subframe and a superframe
    #     returns if the superframe is sufficiently more frequent than the subframe
    #     """
    #     coef = 2 # !!!
    #     if coef * len( subframe.insts) < len( superframe.insts):
    #         return True
    #     return False

    def duplicate_frame_type( self, frame_type):
        new_frame_type = self.frame_type_class( self.appropriate_udeprels)
        for arg in frame_type:
            deprel, form, child_rels = arg.get_description()
            new_arg = frame_type_arg = \
                    self.frame_type_arg_class( deprel, form, child_rels)
            new_frame_type.add_arg( new_arg)