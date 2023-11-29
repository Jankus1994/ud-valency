from udapi.core.block import Block
from verb_record import Verb_record
from frame_type import Frame_type
from frame_inst_arg import Frame_inst_arg
from frame_type_arg import Frame_type_arg
from frame_inst import Frame_inst
from sent_token import Sent_token
from dict_printer import Dict_printer
from collections import defaultdict, Counter
from extraction_unit import Extraction_unit

class Base_frame_extractor( Block):
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

    proper_unit_codes = [ "outp" ]

    def __init__( self, lang_mark="", output_form="text", output_name="",
                  config_name="config.txt", **kwargs):
        """ called from Frame_aligner.__init__ """
        super().__init__( **kwargs)

        self.unit_classes = {}

        #
        #self.fill_unit_class_names( "Base", proper_unit_codes)
        self.unit_classes[ "outp" ] = Base_outp_unit

        self.appropriate_udeprels = \
                [ "nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl" ]
        self.appropriate_child_rels = [ "case", "mark" ]

        self.lang_mark = lang_mark

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

        self.unit_dict = defaultdict( lambda : Extraction_unit("", "", None, False))
        self.config_name = config_name

        self.frame_examples_counter = Counter()
        self.arg_examples_counter = Counter()

    def before_process_document( self, _):
        self.process_config_file( self, self.lang_mark)

    def process_config_file( self, lang_mark):
        if self.config_name:
            unit_dict = defaultdict( Extraction_unit)
            with open( self.config_name, 'r') as config_file:
                for line in config_file:
                    if line.rstrip( '\n') == "" or line.startswith( '#'):
                        continue
                    value, precode, params, _ = line.split( '\t')
                    act_lang_mark, code = "", precode
                    if ':' in precode:
                        act_lang_mark, code = precode.split( ':', 2)
                        #print( self.lang_mark, lang_mark)
                        if act_lang_mark != lang_mark:
                            continue
                    extraction_unit_class, active = Extraction_unit, False
                    if bool( int( value)):
                        extraction_unit_class, active = self.unit_classes[ code ], True
                    unit_dict[ code ] = \
                            extraction_unit_class( code, act_lang_mark, self, active,
                                                   params=params)
            self.unit_dict = unit_dict

    def after_config(self):
        return

    def print_units( self):
        for unit in self.unit_dict.values():
            print( unit.name, unit.active)
        print( "---")


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
        if self.node_is_appropriate(node):
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

    def node_is_appropriate( self, node):
        return node.upos == "VERB"

    def _process_frame( self, verb_node):  # -> Frame_inst
        """ called from process_node """
        # new frame
        frame_type = self.frame_type_class( self.appropriate_udeprels)
        frame_type.set_verb_features( verb_node)
        frame_inst = self.frame_inst_class()

        # creating and adding args to the frame type/inst
        # creating tokens for example sentence and adding them to frame_inst
        frame_type, frame_inst = \
                self._process_sentence( frame_type, frame_inst, verb_node)

        frame_type, frame_inst = \
                self._after_sent( frame_type, frame_inst, verb_node)

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
                frame_type_arg, frame_inst_arg = \
                        self.process_arg( sent_node, verb_node)
                frame_type_arg, frame_inst_arg = \
                        self._after_arg( frame_type_arg, frame_inst_arg,
                                         sent_node, verb_node)
                self.connect_arg_with_frame( frame_type, frame_inst,
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
        is_complement = sent_node.parent is verb_node or \
            self._compl_conditions( sent_node, verb_node)

        ok_deprel = sent_node.udeprel in self.appropriate_udeprels

        result = is_complement and ok_deprel
        return result

    def _compl_conditions( self, sent_node, verb_node):
        """ for overloading
        other conditions for being a complement, other than the verb is the parent
        """
        return False

    def process_arg(self, arg_node, verb_node):
        deprel, form, child_rels, upostag = self._get_arg_features( arg_node)
        frame_type_arg = self.frame_type_arg_class(
                            deprel, form, child_rels)
        frame_inst_arg = self.frame_inst_arg_class( upostag)

        return frame_type_arg, frame_inst_arg

    def _after_arg( self, frame_type_arg, frame_inst_arg, sent_node, verb_node):
        """ for overloading """
        return frame_type_arg, frame_inst_arg

    def _after_sent( self, frame_type, frame_inst, verb_node):
        """ for overloading """
        return frame_type, frame_inst

    @staticmethod
    def connect_arg_with_frame( frame_type, frame_inst,
                                frame_type_arg, frame_inst_arg, token):
        token.arg = frame_inst_arg
        frame_inst.add_arg( frame_inst_arg)
        frame_type_arg.add_inst( frame_inst_arg)
        frame_type.add_arg( frame_type_arg)

    @staticmethod
    def delete_arg( frame_type_arg):
        frame_type = frame_type_arg.frame_type
        verb_record = frame_type.verb_record
        frame_type_arg.delete()
        if verb_record is not None:
            verb_record.consider_merging( frame_type)

    @staticmethod
    def substitute_arg( old_frame_arg, new_frame_arg):
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
        token = Sent_token( token_node.ord, token_node.form, token_node.lemma)

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
        self.unit_dict[ "outp" ].after_process_document( doc)

    def _check_coherence( self):
        for verb_lemma in self.dict_of_verbs.keys():
            verb_record = self.dict_of_verbs[ verb_lemma ]
            verb_record.check_coherence()
            pass

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

    def print_example_counts( self, extractor_name, exam_unit_names):
        frame_inst_count = 0
        arg_inst_count = 0
        # logfile = open("log"+extractor_name, 'w')
        for verb_record in self.dict_of_verbs.values():
            for frame_type in verb_record.frame_types:
                insts_count = len( frame_type.insts)
                frame_inst_count += insts_count
                arg_inst_count += len( frame_type.args) * insts_count
        #         for arg in frame_type.args:
        #             print(arg.deprel, file=logfile)
        # logfile.close()

        print( '\n'+extractor_name)
        print( "frame insts:", frame_inst_count)
        for unit_name in exam_unit_names:
            unit = self.unit_dict[ unit_name ]
            if unit.active :
                for count_name, freq in unit.frm_example_counter.items():
                    perc = round( freq / frame_inst_count * 100, 1)
                    print( unit_name + ':' + count_name, freq, perc)

        print( "---\narg insts:", arg_inst_count)
        for unit_name in exam_unit_names:
            unit = self.unit_dict[ unit_name ]
            if unit.active:
                for count_name, freq in unit.arg_example_counter.items():
                    perc = round( freq / arg_inst_count * 100, 1)
                    print( unit_name + ':' + count_name, freq, perc)

        print( "---\nother stats:")
        for unit_name in exam_unit_names:
            unit = self.unit_dict[ unit_name ]
            if unit.active:
                unit.print_other_stats()
        print( "===\n")


        # else:
        #     unit = self.unit_dict[ exam_unit_name ]
        #     if unit.frm_example_counter:
        #         print( "\nframe insts:", frame_inst_count)
        #     for count_name, freq in unit.frm_example_counter.items():
        #         perc = round( freq / frame_inst_count * 100, 1)
        #         print( exam_unit_name + ':' + count_name, freq, perc)
        #
        #     if unit.arg_example_counter:
        #         print( "\narg insts:", arg_inst_count)
        #     for count_name, freq in unit.arg_example_counter.items():
        #         perc = round( freq / arg_inst_count * 100, 1)
        #         print( exam_unit_name + ':' + count_name, freq, perc)


    def output_result_dict( self):
        Dict_printer.print_dict( self.output_form, self.dict_of_verbs, self.output_name)
        #Dict_printer.print_verbs_by_arg_form( self.dict_of_verbs, "Dat")

class Base_outp_unit( Extraction_unit):
    """ Extraction unit for program output """
    def after_process_document( self, _):
        self.extractor.output_result_dict()
