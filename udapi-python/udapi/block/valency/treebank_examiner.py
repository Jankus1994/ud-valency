from udapi.core.block import Block
from frame_extractor import Frame_extractor
from cs_frame_extractor import Cs_frame_extractor
from en_frame_extractor import En_frame_extractor
from collections import Counter

class Treebank_examiner( Block):
    def __init__( self,  output_name="", lang_mark="", **kwargs):
        super().__init__( **kwargs)
        self.output_name = output_name

        if lang_mark == "cs":
            extractor_class = Cs_frame_extractor
        elif lang_mark == "en":
            extractor_class = En_frame_extractor
        else:
            extractor_class = Frame_extractor
        self.extractor = extractor_class( lang_mark=lang_mark, **kwargs)

        # counters
        self.main_counter = Counter()
        self.pred_coord_counter = Counter()
        self.pred_coord_cc_counter = Counter()
        self.all_verbs_count = 0

    def before_process_document( self, doc):
        super().before_process_document( doc)
        self.extractor.before_process_document( doc)

    def process_tree( self, tree_root):
        super().process_tree( tree_root)

    def process_node( self, node):
        if self.extractor.node_is_appropriate(node):
            self.all_verbs_count += 1
            pred_ret = self.count_coord_predicates( node)
            #if pred_ret:
            #    print( pred_ret)

    def count_coord_predicates( self, predicate_node):
        conj_nodes = [ child for child in predicate_node.children
                       if child.udeprel == "conj"]
        conj_num = len( conj_nodes)
        if conj_num:
            key = "pred_coord_" + str( conj_num + 1)  # plus the actual, head node
            self.pred_coord_counter[ key ] += 1
            last_conj_node = conj_nodes[ -1 ]
            cc_nodes = [ child for child in last_conj_node.children
                         if child.udeprel == "cc"]
            if cc_nodes:
                cc_form = cc_nodes[ 0 ].form
                key = "pred_coord_cc_" + cc_form
                self.pred_coord_cc_counter[ key ] += 1
            coord_pred_nodes = [ predicate_node ] + [ child for child in predicate_node.children if child.udeprel == "conj" ]
            coord_pred_forms = [ node.form for node in coord_pred_nodes ]
            return ' '.join( coord_pred_forms)

    def after_process_document( self, doc):
        super().after_process_document( doc)
        self.extractor.after_process_document( doc)
        self.print_counters()

    def print_counters( self):
        self.print_counter( self.pred_coord_counter, self.all_verbs_count)
        self.extractor.print_units()
        #self.print_counter( self.pred_coord_cc_counter)

    def print_counter( self, counter, all_count):
        print("all", all_count)
        for key, value in counter.most_common():
            perc = round(value / all_count * 100, 1)
            print( key, value, perc)