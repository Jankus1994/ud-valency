class Obl_examiner:
    def __init__( self):
        self.a_lang_mark = ""
        self.b_lang_mark = ""
        self.node_num = {}
        self.verb_num = {}
        self.sent_num = 0
        self.verbs_with_obl = {}
        self.multiple_obls = {}

    def set_lang_marks( self, a_lang_mark, b_lang_mark):
        self.a_lang_mark = a_lang_mark
        self.b_lang_mark = b_lang_mark
        self.node_num = { self.a_lang_mark: 0, self.b_lang_mark: 0 }
        self.verb_num = { self.a_lang_mark: 0, self.b_lang_mark: 0 }
        self.verbs_with_obl = { self.a_lang_mark: 0, self.b_lang_mark: 0 }
        self.multiple_obls = { self.a_lang_mark: 0, self.b_lang_mark: 0 }

    def examine_sentence( self, tree_root, lang_mark):
        nodes = tree_root.descendants()
        verb_nodes = [ node for node in nodes if node.upos == "VERB" ]
        self.node_num[ lang_mark] += len(nodes)
        self.verb_num[ lang_mark ] += len( verb_nodes)
        if lang_mark == self.a_lang_mark:
            self.sent_num += 1

        for verb_node in verb_nodes:
            obliques = [ node for node in nodes if node.udeprel == "obl"
                         and node.parent == verb_node ]
            self.verbs_with_obl[ lang_mark ] += 1 if obliques else 0
            self.multiple_obls[ lang_mark ] += len( obliques)


    def print_stats( self):
        #print( self.sent_num)
        #print( "Tokens")
        #print( self.token_num)
        print( "Verbs")
        print( self.verb_num)

        print( "Verbs wit obl")
        print( self.verbs_with_obl)
        #print( "Ratio of verbs with obl")
        #print( self.verbs_with_obl / self.verb_num)
        print( "Obl occurences (incl. multiple)")
        print( self.multiple_obls)
        print( "Obls per verb")
        a_mean = self.multiple_obls[ self.a_lang_mark ] / \
                 self.verbs_with_obl[ self.a_lang_mark ]
        b_mean = self.multiple_obls[ self.b_lang_mark ] / \
                 self.verbs_with_obl[ self.b_lang_mark ]
        print( { self.a_lang_mark: a_mean, self.b_lang_mark: b_mean })


