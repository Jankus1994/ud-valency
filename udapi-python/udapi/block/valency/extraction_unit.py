from collections import Counter

class Extraction_unit:
    def __init__( self, name, lang_mark, extractor, active, params=""):
        self.name = name
        self.lang_mark = lang_mark
        self.extractor = extractor
        self.frm_example_counter = Counter()
        self.arg_example_counter = Counter()
        self.active = active

    def change_udeprels( self, udeprels):
        return udeprels

    def node_is_appropriate( self, node, gen_result):
        return False

    def node_is_inappropriate( self, node, gen_result):
        return False

    def compl_conditions( self, sent_node, verb_node):
        return False

    def process_frame( self, frame_type, verb_node):
        return frame_type

    def node_is_good_arg(self, sent_node, verb_node, gen_result):
        return False

    def process_arg( self, frame_type_arg, arg_node, verb_node):
        return frame_type_arg

    def after_arg(self, frame_type_arg, frame_inst_arg, sent_node, verb_node):
        return frame_type_arg, frame_inst_arg

    def adding_missing_subjects( self, frame_type, frame_inst, verb_node):
        return frame_type, frame_inst

    def process_subj_elision( self, frame_type, frame_inst, elided_type_arg,
                              elided_inst_arg, subj_token, verb_node):
        return elided_type_arg, elided_inst_arg, subj_token

    def specific_postprocessing( self, frame_type):
        return frame_type

    def after_process_document( self, doc):
        return

    def print_other_stats( self):
        return