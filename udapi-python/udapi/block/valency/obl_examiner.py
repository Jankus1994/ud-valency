from udapi.core.block import Block
from collections import Counter, defaultdict

class Obl_examiner( Block):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.verb_num = 0
        self.verb_lemmas = set()
        self.verb_lemmas_num = 0
        self.verb_with_obl_num = 0
        self.verb_lemmas_with_obl = set()
        self.verbs_by_obl_num = defaultdict( int)
        self.verb_lemmas_by_obl_num = defaultdict( set)

        self.obl_num = 0
        self.obl_on_verb_num_1 = 0
        self.obl_on_verb_num_2 = 0
        self.obl_parent_upos_counter = Counter()
        self.verb_child_deprel_counter = Counter()
        self.verb_arg_num_counter = Counter()
        self.obl_form_counter = Counter()
        self.obl_form_lemmas = defaultdict( set)
        #self.relevant_deprels = [ "nsubj", "obj", "iobj",
        #                          "csubj", "ccomp", "xcomp",
        #                          "obl", "expl" ]
    def process_node( self, node):
        if node.upos == "VERB":
            self.process_verb( node)
        if node.deprel == "obl":
            self.process_obl( node)

    def process_verb( self, verb_node):
        self.verb_num += 1
        self.verb_lemmas.add( verb_node.lemma)
        obl_children = []
        for verb_child in verb_node.children:
            deprel = verb_child.deprel
            if deprel in [ "nsubj", "obj", "obl" ]:
                self.verb_child_deprel_counter[ deprel ] += 1
            elif deprel in [ "iobj", "csubj", "ccomp", "xcomp", "expl" ]:
                self.verb_child_deprel_counter[ "other" ] += 1
            if verb_child.deprel == "obl":
                obl_children.append( verb_child)
                self.obl_on_verb_num_1 += 1
        if obl_children != []:
            self.verb_with_obl_num += 1
            self.verb_lemmas_with_obl.add( verb_node.lemma)
            obl_num = len( obl_children)
            self.verbs_by_obl_num[ obl_num ] += 1
            self.verb_lemmas_by_obl_num[ obl_num ].add( verb_node.lemma)

    def process_obl( self, obl_node):
        self.obl_num += 1
        parent_node = obl_node.parent
        parent_upos = parent_node.upos
        self.obl_parent_upos_counter[ parent_upos ] += 1
        if parent_upos == "VERB":
            self.obl_on_verb_num_2 += 1
            obl_form = self.get_obl_form( obl_node)
            self.obl_form_counter[ obl_form ] += 1
            parent_lemma = parent_node.lemma
            self.obl_form_lemmas[ obl_form ].add( parent_lemma)
        else:
            return
            print( obl_node.root.text)
            print(parent_upos, parent_node._form, obl_node._form)
            print( "===")

    def get_obl_form( self, obl_node):
        obl_case = obl_node.feats[ "Case" ]
        prepositions = []
        postpositions = []
        for obl_child in obl_node.children:
            if obl_child.deprel == "case":
                if obl_child.ord < obl_node.ord:
                    prepositions.append( obl_child.lemma)
                else:
                    postpositions.append( obl_child.lemma)
        obl_form = '+'.join( prepositions + [ obl_case ] + postpositions)
        return obl_form


    def after_process_document( self, _):
        self.basic_stats()
        self.counter_stats()

    @staticmethod
    def percentage( part, whole):
        return round( 100 * part / whole, 1)

    def print_partial_stats( self, stat_name, part_verbs, part_verb_lemmas):
        print( stat_name)
        print( "\t# of verbs:", part_verbs)
        portion = self.percentage( part_verbs, self.verb_num)
        print( "\t% of verbs:", portion)
        #print( "\t# of verb lemmas:", part_verb_lemmas)
        #portion = self.percentage( part_verb_lemmas, self.verb_lemmas_num)
        #print( "\t% of verb lemmas:", portion)
        print( "------")

    def basic_stats( self):
        print( "============")
        print( "# of verbs:", self.verb_num)
        self.verb_lemmas_num = len( self.verb_lemmas)
        #print( "# of verb lemmas:", self.verb_lemmas_num)
        print( "# of obls:", self.obl_num)
        if self.obl_on_verb_num_1 == self.obl_on_verb_num_2:
            print( "# of obls on verb:", self.obl_on_verb_num_1)
            obl_on_verbs_perc = self.percentage( self.obl_on_verb_num_1, self.obl_num)
            print( "% of obls on verb:", obl_on_verbs_perc)
        #print( "# of obls on verbs:", self.obl_on_verb_num_1, self.obl_on_verb_num_2)
        print( "------")
        self.print_partial_stats( "verbs with any obl", self.verb_with_obl_num,
                                  len( self.verb_lemmas_with_obl))
        for obl_num in self.verbs_by_obl_num.keys():
            stat_name = "# of obls: " + str( obl_num)
            self.print_partial_stats( stat_name, self.verbs_by_obl_num[ obl_num ],
                                  len( self.verb_lemmas_by_obl_num[ obl_num ]))
        # este nieco? nieco o zavislostiach obliqov na neslovesach?

    def counter_stats( self):
        print( "============")
        print( "upostags of obl parents:")
        for upos, freq in self.obl_parent_upos_counter.most_common():
            print( upos, freq)
        print( "------")
        print( "deprels of verb children:")
        for deprel, freq in self.verb_child_deprel_counter.most_common():
            #if deprel in self.relevant_deprels:
            print( deprel, freq)
        print( "------")
        spec_records = []
        all_verb_lemma_count = len( self.verb_lemmas)
        print( "obl forms:")
        for obl_form, overall_count in self.obl_form_counter.most_common( 10):
            overall_portion = self.percentage( overall_count, self.verb_num)
            #count_with_lemmas = len( self.obl_form_lemmas[ obl_form ])
            #portion_of_lemmas = self.percentage( count_with_lemmas, len( self.verb_lemmas))
            #specificity = round( overall_count / count_with_lemmas, 3)
            print( obl_form, overall_count, overall_portion)#,
                   #count_with_lemmas, portion_of_lemmas)
            #spec_records.append( ( obl_form, overall_count,
            #                      count_with_lemmas, portion_of_lemmas))
        #spec_records.sort( key=lambda spec_record: spec_record[ 3 ], reverse=True)
        #for spec_record in spec_records[ :10 ]:
        #    obl_form, overall_count, count_with_lemmas, portion_of_lemmas = spec_record
        #    print( obl_form, overall_count, count_with_lemmas, portion_of_lemmas)



