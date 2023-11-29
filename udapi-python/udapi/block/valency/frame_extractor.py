import sys

from base_frame_extractor import Base_frame_extractor
from sent_token import Sent_token
from extraction_unit import Extraction_unit
from collections import defaultdict

class Frame_extractor( Base_frame_extractor):

    proper_unit_codes = [ "coor", "subj", "auxf", "oblq", "frdc" ]

    #def __init__( self, modals="", **kwargs):
    def __init__( self, **kwargs):
        """ called from Frame_aligner.__init__ """
        super().__init__( **kwargs)

        self.unit_classes[ "coor" ] = Main_coor_unit
        self.unit_classes[ "subj" ] = Main_subj_unit
        self.unit_classes[ "auxf" ] = Main_auxf_unit
        self.unit_classes[ "oblq" ] = Main_oblq_unit
        self.unit_classes[ "frdc" ] = Main_frdc_unit

        self.modal_lemmas = []

    def before_process_document( self, doc):
        super().before_process_document( doc)
        self.after_config()

    def after_config( self):
        self.appropriate_udeprels = self.unit_dict[ "oblq" ].change_udeprels(
                self.appropriate_udeprels)

    def node_is_appropriate(self, node):
        result = super().node_is_appropriate(node)
        return result

    def _after_sent( self, frame_type, frame_inst, verb_node):
        """ called from process_frame """
        frame_type, frame_inst = \
                    self.adding_missing_subjects( frame_type, frame_inst, verb_node)
        return frame_type, frame_inst

    def adding_missing_subjects( self, frame_type, frame_inst, verb_node):
        frame_type, frame_inst = self.unit_dict[ "subj" ].adding_missing_subjects(
                frame_type, frame_inst, verb_node)
        return frame_type, frame_inst

    def _compl_conditions( self, sent_node, verb_node):
        """ called from _node_is_good_arg """
        return self.unit_dict[ "coor" ].compl_conditions( sent_node, verb_node)

    def process_arg( self, arg_node, verb_node):
        frame_type_arg, frame_inst_arg = \
                super().process_arg( arg_node, verb_node)

        frame_type_arg = self.unit_dict[ "auxf" ].process_arg(
                frame_type_arg, arg_node, verb_node)

        return frame_type_arg, frame_inst_arg

    def _after_arg( self, frame_type_arg, frame_inst_arg, sent_node, verb_node):
        """ called from _process_sentence """
        frame_type_arg, frame_inst_arg = self.unit_dict[ "coor" ].after_arg(
                frame_type_arg, frame_inst_arg, sent_node, verb_node)
        return frame_type_arg, frame_inst_arg

    def after_process_document( self, doc):  # void
        """ overriden block method - monolingual use case """
        self.unit_dict[ "coor" ].after_process_document( doc)
        #self._check_coherence()
        self._postprocessing()
        #self._check_coherence()
        self.unit_dict[ "oblq" ].after_process_document( doc)

        for verb_record in self.dict_of_verbs.values():
            verb_record.build_frame_dag()
        #for verb_record in self.dict_of_verbs.values():
        #    for frame_type in verb_record.frame_types:
        #        print( len( frame_type.superframes), len( frame_type.subframes), len( frame_type.tree_subframes))



        self.unit_dict[ "frdc" ].after_process_document( doc)

        #self._final_control()  # development method
        super().after_process_document( doc)

    def _postprocessing( self):
        for verb_record in self.dict_of_verbs.values():
            for frame_type in verb_record.frame_types:
                self.specific_postprocessing( frame_type)

    def specific_postprocessing( self, frame_type):
        pass

class Main_coor_unit( Extraction_unit):
    """ ARG level unit """
    def compl_conditions( self, sent_node, verb_node):
        return self._could_be_coord_arg(sent_node, verb_node)

    def _could_be_coord_arg( self, sent_node, verb_node):
        """ whether sent node is an argument of the verb, but because of the verb
        is a conjunct, the sent node is """
        if verb_node.deprel == "conj":
            coord_head_node = verb_node.parent
            if sent_node.parent is coord_head_node:  # sent and verb nodes are siblings
                # there should not be two subjects or direct objects
                for child_node in verb_node.children:
                    if "subj" in child_node.deprel and "subj" in sent_node.deprel:
                        return False
                    if "obj" in child_node.deprel and "obj" in sent_node.deprel:
                        return False
                # sent node should be on the same side of both verbs
                before_coord = sent_node.ord < coord_head_node.ord and \
                               sent_node.ord < verb_node.ord
                after_coord = sent_node.ord > coord_head_node.ord and \
                               sent_node.ord > verb_node.ord
                return before_coord or after_coord
        return False

    def after_arg( self, frame_type_arg, frame_inst_arg, sent_node, verb_node):
        """ marks argument as possibly coordinated """
        if self._could_be_coord_arg( sent_node, verb_node):
            frame_inst_arg.is_coord_arg = True
            self.arg_example_counter[ "possible" ] += 1
        return frame_type_arg, frame_inst_arg

    def after_process_document( self, _):
        num_of_successes = 0
        for verb_record in self.extractor.dict_of_verbs.values():
            frames_by_arg_num = sorted( verb_record.frame_types,
                    key=lambda frame_type : len( frame_type.args), reverse=True)
            for frame_type in frames_by_arg_num:
                success = frame_type.try_delete_coord_args()
                if success:
                    self.arg_example_counter[ "deleted" ] += 1
                    num_of_successes += 1
                    verb_record.consider_merging( frame_type)
    
class Main_subj_unit( Extraction_unit):
    """ ARG level unit """
    def adding_missing_subjects( self, frame_type, frame_inst, verb_node):
        if not frame_type.has_subject():
            subj_token = Sent_token( None, "", "")
            subj_token.mark_elision()  # TODO rewrite with property
            elided_type_arg = self.extractor.frame_type_arg_class( "nsubj", "", [])
            elided_inst_arg = self.extractor.frame_inst_arg_class( "PRON")
            self.frm_example_counter[ "added" ] += 1

            # elided_type_arg, elided_inst_arg, subj_token = \
            #         self.process_subj_elision( frame_type, frame_inst,
            #                                    elided_type_arg, elided_inst_arg,
            #                                    subj_token, verb_node)

            frame_inst.add_elided_token( subj_token)
            self.extractor.connect_arg_with_frame(
                    frame_type, frame_inst, elided_type_arg, elided_inst_arg, subj_token)

            assert frame_type.verb_record is None

        return frame_type, frame_inst

    # def process_subj_elision( self, frame_type, frame_inst, elided_type_arg,
    #                           elided_inst_arg, subj_token, verb_node):
    #     """ for overloading """
    #     return elided_type_arg, elided_inst_arg, subj_token

class Main_auxf_unit( Extraction_unit):
    """ ARG level unit """
    def process_arg( self, frame_type_arg, arg_node, _):
        """ used in language specific modules
        head of dependent clause obtains form from its AUX children
        if there is Fin among them, it gets Fin (fin)
        otherwise it gets form from the first AUX child (nonfin)
        if there are no AUX children, the original form remains (orig)
        """
        if "comp" in frame_type_arg.deprel or "csubj" in frame_type_arg.deprel:
            if frame_type_arg.form == "Fin":
                self.arg_example_counter[ "orig_fin" ] += 1
                return frame_type_arg
            aux_fin_child_nodes = [ child_node for child_node in arg_node.children
                                    if child_node.upos == "AUX" and
                                       child_node.feats[ "VerbForm" ] == "Fin" ]
            if aux_fin_child_nodes:
                frame_type_arg.form = "Fin"
                self.arg_example_counter[ "changed_fin" ] += 1
                return frame_type_arg
            self.arg_example_counter[ "orig_nonfin" ] += 1
        return frame_type_arg

class Main_oblq_unit( Extraction_unit):
    """ ARG level unit
    !!! the variant method is not definitively solved
    """
    ACTANT_ALWAYS = 1
    ACTANT_RATHER = 2
    HEURISTIC = 3
    ADJUNCT_RATHER = 4
    ADJUNCT_ALWAYS = 5
    def __init__( self, *args, params=""):
        super().__init__( *args, params=params)
        self.this_verb_portions = defaultdict( int)
        self.all_verbs_portions = defaultdict( int)
        self.important_values = defaultdict( float)

        self.variant_num = int( params) if params else 3

    def change_udeprels( self, udeprels):
        udeprels = [ "nsubj", "csubj", "obj", "iobj",
                     "obl", "ccomp", "xcomp", "expl" ]
        return udeprels

    def after_process_document( self, _):
        # if self.variant_num == self.ACTANT_ALWAYS:
        #
        # elif self.variant_num == self.ADJUNCT_ALWAYS:
        #     all_obl_args = []
        # for verb_record in self.extractor.dict_of_verbs.values():
        #     for frame_type in verb_record.frame_types:
        #         obl_args = [ arg for arg in frame_type.args if "obl" in arg.deprel ]
        #         all_obl_args += obl_args
        # for obl_arg in all_obl_args:
        #     self.arg_example_counter["total"] += 1
        #     if obl_arg.deleted:  # already merged
        #         self.arg_example_counter[ "already" ] += 1
        #         continue
        #     self.arg_example_counter["okik"] += 1
        #     self.choose_adjunct(obl_arg)
        # return
        value_triplets = []
        obl_dict = {}
        for verb_record in self.extractor.dict_of_verbs.values():
            for frame_type in verb_record.frame_types:
                for arg in frame_type.args:
                    if "obl" in arg.deprel:
                        if arg.deprel in [ "obl:arg", "obl:agent" ]:
                            continue
                        self.arg_example_counter[ "total" ] += 1
                        this_verb_portion = round( 100 *
                                self._arg_in_this_verb( verb_record, arg), 2)
                        all_verbs_portion = round( 100 *
                                self._arg_in_all_verbs( obl_dict, arg), 2)

                        self.this_verb_portions[ int( round( this_verb_portion/10)) ] += 1
                        self.all_verbs_portions[ int( round( all_verbs_portion/10)) ] += 1

                        value_triplets.append( ( arg, this_verb_portion, all_verbs_portion))
                        assert arg.frame_type.verb_record is not None

                        #str_arg = str( arg).split( '-')[1]
                        #print( str_arg, this_verb_portion, all_verbs_portion, sep='\t')
        # for verb_record in self.extractor.dict_of_verbs.values():
        #     for frame_type in verb_record.frame_types:
        #         for arg in frame_type.args:
        #             if "obl" in arg.deprel:
        #                 self.arg_example_counter["seond_deleted"] += 1
        #                 self.choose_adjunct(arg)
        # for verb_record in self.extractor.dict_of_verbs.values():
        #     for frame_type in verb_record.frame_types:
        #         for arg in frame_type.args:
        #             if "obl" in arg.deprel:
        #                 self.arg_example_counter["undeleted"] += 1
        # return
        this_verb_portions = [ value for _, value, _ in value_triplets ]
        all_verbs_portions = [ value for _, _, value in value_triplets ]
        if this_verb_portions != [] and all_verbs_portions != []:
            avg_this = sum( this_verb_portions) / len( this_verb_portions)
            min_this = min( this_verb_portions)
            max_this = max( this_verb_portions)
            avg_all = sum( all_verbs_portions) / len( all_verbs_portions)
            min_all = min( all_verbs_portions)
            max_all = max( all_verbs_portions)
            self.important_values[ "avg_this" ] = avg_this
            self.important_values[ "min_this" ] = min_this
            self.important_values[ "max_this" ] = max_this
            self.important_values[ "avg_all" ] = avg_all
            self.important_values[ "min_all" ] = min_all
            self.important_values[ "max_all" ] = max_all

            if self.variant_num == self.ACTANT_ALWAYS:
                for arg, _, _ in value_triplets:
                    self.choose_actant()
            elif self.variant_num == self.ADJUNCT_ALWAYS:
                for arg, _, _ in value_triplets:
                    if arg.deleted:  # already merged
                        self.arg_example_counter[ "deleted" ] += 1
                        continue
                    self.choose_adjunct( arg)
            else:
                for arg, this_verb_portion, all_verbs_portion in value_triplets:
                    #assert arg.frame_type.verb_record is not None or arg.deleted
                    if arg.deleted:  # already merged
                        self.arg_example_counter[ "deleted" ] += 1
                        continue
                    elif this_verb_portion < avg_this:
                        if all_verbs_portion > avg_all:
                            self.choose_adjunct( arg)
                        else:  # all_verbs_portion >= avg_all
                            self.further_examine( arg, this_verb_portion, all_verbs_portion, True)
                    else:  # this_verb_portion >= avg_this
                        if all_verbs_portion < avg_all:
                            self.choose_actant()
                        else:  # all_verbs_portion >= avg_all
                            self.further_examine( arg, this_verb_portion, all_verbs_portion, False)

    @staticmethod
    def dist_from_mean( avg_val, ext_val, value):
        value_from_avg = abs( avg_val - value)
        ext_from_avg = abs( avg_val - ext_val)
        result = 100 / ext_from_avg * value_from_avg
        return result

    def leave_undecided( self, arg):
        arg.definitive = False
        self.arg_example_counter[ "unknown" ] += 1

    def choose_actant( self):
        self.arg_example_counter[ "actant" ] += 1

    def choose_adjunct( self, arg):
        self.extractor.delete_arg( arg)
        self.arg_example_counter[ "adjunct"] += 1

    def further_examine( self, arg, this_verb_portion, all_verbs_portion, this_under_avg):
        self.arg_example_counter[ "examine" ] += 1
        if self.variant_num == self.ACTANT_RATHER:
            self.choose_actant()
            self.arg_example_counter[ "exam_actant" ] += 1
        elif self.variant_num == self.ADJUNCT_RATHER:
            self.choose_adjunct( arg)
            self.arg_example_counter[ "exam_adjunct" ] += 1
        else:  # self.variant_num == self.HEURISTIC:
            avg_this = self.important_values[ "avg_this" ]
            min_this = self.important_values[ "min_this" ]
            max_this = self.important_values[ "max_this" ]
            avg_all = self.important_values[ "avg_all" ]
            min_all = self.important_values[ "min_all" ]
            max_all = self.important_values[ "max_all" ]

            ext_this, ext_all = max_this, max_all
            if this_under_avg:
                ext_this, ext_all = min_this, min_all

            this_dist = self.dist_from_mean( avg_this, ext_this, this_verb_portion)
            all_dist = self.dist_from_mean( avg_all, ext_all, all_verbs_portion)
            if this_dist < all_dist:
                self.choose_actant()
                self.arg_example_counter[ "exam_actant" ] += 1
            else:
                self.choose_adjunct( arg)
                self.arg_example_counter[ "exam_adjunct" ] += 1


    def _arg_in_all_verbs( self, deprel_dict, arg):
        arg_str = arg.to_str()
        if arg_str in deprel_dict:
            avg_occur_portion = deprel_dict[ arg_str ]
        else:
            sum_occur_portion = 0
            for verb_record in self.extractor.dict_of_verbs.values():
                occur_portion = self._arg_in_this_verb( verb_record, arg)
                sum_occur_portion += occur_portion
            verbs_num = len( self.extractor.dict_of_verbs)
            avg_occur_portion = sum_occur_portion / verbs_num
            deprel_dict[ arg_str ] = avg_occur_portion
            #print( arg_str, round( 100 * avg_occur_portion, 3), sep='\t')
        return avg_occur_portion

    @staticmethod
    def _arg_in_this_verb( verb_record, arg):
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

    def print_other_stats( self):
        print( "obl this verb portions:")
        print( sorted( self.this_verb_portions.items()))
        #    print( key, self.this_verb_portions[ key ])
        print( "obl all verbs portions:")
        print( sorted( self.all_verbs_portions.items()))
        #    print( key, self.all_verbs_portions[ key ])
        print( "other obl values:")
        for key, value in self.important_values.items():
            print( key, round( value, 1))

class Main_frdc_unit( Extraction_unit):
    """ ARG level unit """
    def __init__( self, *args, params=""):
        super().__init__( *args, params=params)
        reduction_coef_str = params
        try:
            self.reduction_coef = float( reduction_coef_str)
        except ValueError:
            print( "Incorrect format of reduction coefficient!", file=sys.stderr)
            exit()
        self.diff_dict = {}

    def after_process_document( self, _):
        # building frame tree structure
        for verb_record in self.extractor.dict_of_verbs.values():
            for frame_type in verb_record.frame_types:
                frame_type.choose_tree_superframe()

        # reduction with statistics
        deprel_dict_before = self.count_statistics( "before")
        for verb_record in self.extractor.dict_of_verbs.values():
            verb_record.frame_reduction( self.reduction_coef)  # reducing number of frames before outputting
            #verb_record.frame_reduction( False)
        deprel_dict_after = self.count_statistics( "after")

        for key, value_before in deprel_dict_before.items():
            value_after = deprel_dict_after[ key ]
            diff = value_before - value_after
            if diff:
                self.diff_dict[ key ] = diff

    def count_statistics( self, before_after):
        deprel_dict = defaultdict(int)
        for verb_record in self.extractor.dict_of_verbs.values():
            self.frm_example_counter[ before_after + "_frames" ] += len( verb_record.frame_types)
            for frame_type in verb_record.frame_types:
                superframes_num = len( frame_type.superframes)
                self.frm_example_counter[ before_after + "_" + str( superframes_num) ] += 1
                for frame_arg_type in frame_type.args:
                    deprel_dict[ frame_arg_type.deprel ] += 1
        return deprel_dict

    def print_other_stats( self):
        print( self.diff_dict)
