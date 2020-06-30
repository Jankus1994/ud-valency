class Frame_type_argument:
    """ class representing verb frame argument """
    def __init__( self, node, deprel="", case_feat="", case_mark_rels=[]):
        if node is None:
            self.deprel = deprel
            self.case_feat = case_feat
            self.case_mark_rels = case_mark_rels
        else:
            self.deprel = node.deprel

            self.case_feat = node.feats[ "Case" ]
            if self.case_feat == "":
                self.case_feat = "0"

            self.case_mark_rels = []
            for child in node.children:
                if child.deprel in ["case", "mark"]:
                    case_mark_rel = child.deprel + '-' + child.lemma
                    self.case_mark_rels.append( case_mark_rel)

    def is_identical_with( self, another_frame_argument):  # -> bool
        if self.deprel == another_frame_argument.deprel and \
                self.case_feat == another_frame_argument.case_feat and \
                self.case_mark_rels == another_frame_argument.case_mark_rels:
            return True
        return False

class Frame_instance_argument( Frame_type_argument):
    def __init__( self, node, deprel="", case_feat="", case_mark_rels=[]):
        self.node = node
        #self.translations = []
        super().__init__( node, deprel, case_feat, case_mark_rels)


class Example_sentence:
    """ class representing an example sentence for a verb frame
    it contains list of word forms with some information
    used in creation of HTML table
    """
    def __init__( self, actual_node, argument_nodes, elided_tokens = []):
        sentence_nodes = actual_node.root.descendants
        self.tokens = []
        for node in sentence_nodes:
            token_dict = {}
            token_dict[ "form" ] = node.form

            if node is actual_node:
                token_dict[ "highlight" ] = 2
            elif node in argument_nodes:
                token_dict[ "highlight" ] = 1
            else:
                token_dict[ "highlight" ] = 0

            token_dict[ "space" ] = not ( node.no_space_after or node == sentence_nodes[ -1 ] )

            self.tokens.append( token_dict)

        self.elided_tokens = []
        for elided_token in elided_tokens:
            elided_token_dict = {}
            elided_token_dict[ "form" ] = elided_token
            elided_token_dict[ "highlight" ] = 1  # we suppose that all elided tokens
                                                  # are frame arguments
            self.elided_tokens.append( elided_token_dict)


class Frame_instance:
    def __init__( self, frame_type, verb_node):
        self.example_sentence_class = Example_sentence
        self.argument_class = Frame_instance_argument
        
        self.frame_type = frame_type
        self.verb_node = verb_node

        self.arguments = []
        self.sentence = None
        self.frame_link = None

    def process_sentence( self, elided_tokens = []):  # void
        arg_nodes = [ arg.node for arg in self.arguments ]
        self.sentence = self.example_sentence_class( \
                self.verb_node, arg_nodes, elided_tokens)

    def add_argument( self, argument_node):
        argument = self.argument_class( argument_node)
        self.arguments.append( argument)

    def get_type( self):
        return self.frame_type

    def change_frame_type( self, new_frame_type):
        self.frame_type = new_frame_type

    def set_frame_link( self, frame_link):
        self.frame_link = frame_link
        

class Frame_type:
    """ class representing verb frame with information about the verb
    and with a list of its arguments
    """
    appropriate_udeprels = [ "nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl" ]
    appropriate_deprels = [ "obl:arg", "obl:agent" ]

    def __init__( self, verb_node):
        self.frame_instance_class = Frame_instance
        self.argument_class = Frame_type_argument

        self.verb_lemma = verb_node.lemma

        # verb form
        self.verb_form = verb_node.feats[ "VerbForm" ]
        if self.verb_form == "":
            self.verb_form = "0"

        # voice
        self.voice = verb_node.feats[ "Voice" ]
        if self.voice == "":
            self.voice = "0"

        self.instances = []
        self.arguments = []
        self.str_arguments = [] # filled with args_to_string_list
        self.frame_links = []  # objects pairing corresponding frames from two languages

        self.first_frame_instance = self.frame_instance_class( self, verb_node)
        self.process_arguments( verb_node)
        self.process_first_instance()
        #self.superframe = None # frame containng this frame - for the final frame reduction

    def process_arguments( self, verb_node):
        """ iterates through verb children and calls create_argument for each of them """
        for child_node in verb_node.children:
            if child_node.udeprel in self.appropriate_udeprels or \
                    child_node.deprel in self.appropriate_deprels:
                argument = Frame_type_argument( child_node)
                self.arguments.append( argument)
                self.first_frame_instance.add_argument( child_node)
        self.sort_arguments()

    def sort_arguments( self):
        # TODO: maybe move the sorting to frame_argument
        self.arguments = sorted( self.arguments, key =
                lambda arg :( arg.deprel, arg.case_feat, arg.case_mark_rels ))

    def process_first_instance( self):
        self.first_frame_instance.process_sentence()
        self.instances.append( self.first_frame_instance)

    def get_instance( self):
        return self.first_frame_instance

    def add_frame_link( self, frame_link):
        if frame_link not in self.frame_links:
            #if frame_link:
            # !!! maybe we should control if the link includes this frame !!!
            self.frame_links.append( frame_link)
    
    def find_link_with( self, translation_frame_type):
        for frame_link in self.frame_links:
            if frame_link.links_type( translation_frame_type):
                return frame_link
        return None


    def has_identical_arguments_with( self, another_frame_type):  # -> bool
        """ checks if this frame has identical arguments with another frame """
        if len( self.arguments) != len( another_frame_type.arguments):
            return False            

        for i in range( len( self.arguments)):
            if not self.arguments[ i ].is_identical_with( another_frame_type.arguments[ i ]):
                return False
        return True

    def is_identical_with( self, another_frame_type):  # -> bool
        """ checks if this frame is identical with another frame """
        if self.verb_lemma == another_frame_type.verb_lemma and \
                self.verb_form == another_frame_type.verb_form and \
                self.voice == another_frame_type.voice and \
                self.has_identical_arguments_with( another_frame_type):
            return True
        return False

    def try_merge_with( self, another_frame_type):
        # controls if the frames are identical and if yes, merges them
        if self.is_identical_with( another_frame_type):
            for frame_instance in another_frame_type.instances:
                frame_instance.change_frame_type( self)
                self.instances.append( frame_instance)
            return True
        return False


    def args_to_string_list( self):
        """ converts Frame_arguments to their string representation
        and saves them into the str_arguments attribute of the frame
        """
        self.str_arguments = []
        for argument in self.arguments:
            argument_string = argument.deprel + '-' + argument.case_feat
            if argument.case_mark_rels != []:
                argument_string += '(' + ','.join( argument.case_mark_rels) + ')'
            self.str_arguments.append( argument_string)

    def args_to_one_string( self): # -> str
        """ creates one long string of all frame arguments """
        self.args_to_string_list()
        final_string = ' '.join( self.str_arguments)
        return final_string

    #def


class Frame_link:
    def __init__( self, a_frame_type, b_frame_type):
        """ lang_code... strinng code of language, that comes first """
        self.a_frame_type = a_frame_type
        self.b_frame_type = b_frame_type
        self.frame_instance_pairs = []

    def add_frame_instance_pair( self, a_frame_instance, b_frame_instance):
        a_frame_instance.set_frame_link( self)
        b_frame_instance.set_frame_link( self)
        frame_instance_pair = a_frame_instance, b_frame_instance
        self.frame_instance_pairs.append( frame_instance_pair)
        #print( len(  self.frame_instance_pairs))
    
    def links_type( self, translation_frame_type):
        # assymetric !
        return self.b_frame_type == translation_frame_type

