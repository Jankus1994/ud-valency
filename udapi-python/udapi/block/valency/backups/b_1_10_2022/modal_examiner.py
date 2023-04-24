class  Modal_examiner:
    def __init__( self):
        self.a_lang_mark = ""
        self.b_lang_mark = ""
        self.sent_num = 0
        self.num_of_double_verbs = {}
        self.lemma_examples = {}
        self.cs_modal_lemmas = [ "muset", "moci", "mít", "smět", "chtít",
                                 "hodlat", "umět", "dovést" ]
        self.en_modal_lemmas = [ "can", "could", "may", "might", "shall", "should",
                                 "will", "would", "must" ]

    def set_lang_marks( self, a_lang_mark, b_lang_mark):
        self.a_lang_mark = a_lang_mark
        self.b_lang_mark = b_lang_mark
        self.num_of_double_verbs = { self.a_lang_mark: 0, self.b_lang_mark: 0 }
        self.lemma_examples = { self.a_lang_mark: [], self.b_lang_mark: [] }


    def examine_sentence( self, tree_root, lang_mark):
        nodes = tree_root.descendants()
        verb_nodes = [ node for node in nodes if node.upos in [ "VERB", "AUX"] ]
        verbs_on_verb = [ verb_node for verb_node in verb_nodes
                           if verb_node.parent in verb_nodes ]

        if lang_mark == "cs":
            cs_modals = [ verb_on_verb for verb_on_verb in verbs_on_verb
                          if verb_on_verb.parent.lemma in self.cs_modal_lemmas ]
            self.num_of_double_verbs[ lang_mark ] += len( cs_modals)
            self.lemma_examples[ lang_mark ] += \
                    [ ( verb_node.lemma + '_' + verb_node.parent.lemma )
                      for verb_node in cs_modals ]

        if lang_mark == "en":
            en_modals = [ verb_on_verb for verb_on_verb in verbs_on_verb
                          if verb_on_verb.lemma in self.en_modal_lemmas ]
            for verb_on_verb in verbs_on_verb:
                if verb_on_verb.lemma == "have":
                    for child in verb_on_verb.parent.children:
                        if child.lemma == "to":
                            en_modals += [ verb_on_verb ]
            self.num_of_double_verbs[ lang_mark ] += len( en_modals)
            self.lemma_examples[ lang_mark ] += \
                    [ ( verb_node.lemma + '_' + verb_node.parent.lemma )
                      for verb_node in en_modals ]



    def print_stats( self):
        print( self.a_lang_mark)
        print( self.num_of_double_verbs[ self.a_lang_mark ])
        #print( self.lemma_examples[ self.a_lang_mark ])
        print( "")

        print( self.b_lang_mark)
        print( self.num_of_double_verbs[ self.b_lang_mark ])
        #print( self.lemma_examples[ self.b_lang_mark ])



