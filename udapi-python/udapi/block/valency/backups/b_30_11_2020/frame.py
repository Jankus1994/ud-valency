from udapi.block.valency.role import Role
from udapi.block.valency.token import Token

class Frame_inst_arg:
    def __init__( self, frame_instance):
        self.frame_instance = None
        self.frame_type_arg = None
        self.frame_inst_arg_link = None


class Frame_type_arg:
    """ class representing verb frame argument """
    def __init__( self, node, deprel="", case_feat="", case_mark_rels=[]):
        self.frame_type = None
        self.fram_type_arg_links = []
        self.frame_type_inst_args = []

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

    def is_identical_with( self, another_frame_arg):  # -> bool
        if self.deprel == another_frame_arg.deprel and \
                self.case_feat == another_frame_arg.form and \
                self.case_mark_rels == another_frame_arg.case_mark_rels:
            return True
        return False


class Example_sentence:
    """ class representing an example sentence for a verb frame
    it contains list of word forms with some information
    used in creation of HTML table
    """
    def __init__( self, actual_node, arg_nodes, elided_tokens = []):
        sentence_nodes = actual_node.root.descendants
        self.tokens = []
        for node in sentence_nodes:
            token = Token()
            token.set_form(node._form)

            if node is actual_node:
                token.set_role( Role.PRED)
            elif node in arg_nodes:
                token.set_role( Role.ARG)
            #else:
            #    token.set_role( Role.NONE)  # ... default

            space_after = not ( node.no_space_after or node == sentence_nodes[ -1 ] )
            token.set_space( space_after)

            self.tokens.append( token)

        self.elided_tokens = []
        for elided_token in elided_tokens:
            elided_token = Token()
            # form is already set
            # space dos not need to be set
            elided_token.set_role( Role.ARG)  # we suppose that all elided tokens
                                              # are frame arguments
            self.elided_tokens.append( elided_token)


class Frame_inst:
    def __init__( self, frame_type):
        self.example_sentence_class = Example_sentence
        self.frame_inst_arg_class = Frame_inst_arg
        
        self.frame_type = frame_type
        self.frame_inst_link = None

        self.args = []
        self.sentence = None

    def process_sentence( self, verb_node, elided_tokens = []):  # void
        arg_nodes = [ arg.node for arg in self.args ]
        self.sentence = self.example_sentence_class( verb_node, arg_nodes, elided_tokens)

    def add_arg( self, arg_node):
        arg = self.frame_inst_arg_class( arg_node)
        self.args.append( arg)

    def get_type( self):
        return self.frame_type

    def change_frame_type( self, new_frame_type):
        self.frame_type = new_frame_type

    def set_frame_inst_link( self, frame_inst_link):
        self.frame_inst_link = frame_inst_link
        

class Frame_type:
    """ class representing verb frame with information about the verb
    and with a list of its arguments
    """
    appropriate_udeprels = [ "nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl" ]
    appropriate_deprels = [ "obl:arg", "obl:agent" ]

    def __init__( self, verb_node):
        self.frame_inst_class = Frame_inst
        self.frame_type_arg_class = Frame_type_arg

        self.verb_lemma = verb_node.lemma

        # verb form
        self.verb_form = verb_node.feats[ "VerbForm" ]
        if self.verb_form == "":
            self.verb_form = "0"

        # voice
        self.voice = verb_node.feats[ "Voice" ]
        if self.voice == "":
            self.voice = "0"

        self.insts = []
        self.args = []
        self.str_args = [] # filled with args_to_string_list
        self.frame_type_links = []  # objects pairing corresponding frames from two languages

        self.first_frame_inst = self.frame_inst_class( self)
        self.first_frame_inst.process_sentence( verb_node)
        self.process_args( verb_node)
        #self.superframe = None # frame containng this frame - for the final frame reduction

    def process_args( self, verb_node):
        """ iterates through verb children and calls create_arg for each of them """
        for child_node in verb_node.children:
            if child_node.udeprel in self.appropriate_udeprels or \
                    child_node.deprel in self.appropriate_deprels:
                arg = self.frame_type_arg_class( child_node)
                self.args.append( arg)
                self.first_frame_inst.add_arg( child_node)
        self.sort_args()

    def sort_args( self):
        # TODO: maybe move the sorting to frame_arg
        self.args = sorted(self.args, key =
                lambda arg :(arg.deprel, arg.form, arg.case_mark_rels))

    def process_first_inst( self):
        self.first_frame_inst.process_sentence()
        self.insts.append( self.first_frame_inst)

    def get_inst( self):
        return self.first_frame_inst

    def add_frame_type_link( self, frame_type_link):
        if frame_type_link not in self.frame_type_links:
            #if frame_type_link:
            # !!! maybe we should control if the link includes this frame !!!
            self.frame_type_links.append( frame_type_link)
    
    def find_link_with( self, translation_frame_type):
        for frame_type_link in self.frame_type_links:
            if frame_type_link.links_type( translation_frame_type):
                return frame_type_link
        return None


    def has_identical_args_with( self, another_frame_type):  # -> bool
        """ checks if this frame has identical arguments with another frame """
        if len( self.args) != len( another_frame_type.args):
            return False            

        for i in range( len( self.args)):
            if not self.args[ i ].is_identical_with( another_frame_type.args[ i ]):
                return False
        return True

    def is_identical_with( self, another_frame_type):  # -> bool
        """ checks if this frame is identical with another frame """
        if self.verb_lemma == another_frame_type.verb_lemma and \
                self.verb_form == another_frame_type.verb_form and \
                self.voice == another_frame_type.voice and \
                self.has_identical_args_with( another_frame_type):
            return True
        return False

    def try_merge_with( self, another_frame_type):
        # controls if the frames are identical and if yes, merges them
        if self.is_identical_with( another_frame_type):
            for frame_inst in another_frame_type.insts:
                frame_inst.change_frame_type( self)
                self.insts.append( frame_inst)
            return True
        return False


    def args_to_string_list( self):
        """ converts Frame_args to their string representation
        and saves them into the str_args attribute of the frame
        """
        self.str_args = []
        for arg in self.args:
            arg_string = arg.deprel + '-' + arg.form
            if arg.case_mark_rels != []:
                arg_string += '(' + ','.join( arg.case_mark_rels) + ')'
            self.str_args.append( arg_string)

    def args_to_one_string( self): # -> str
        """ creates one long string of all frame arguments """
        self.args_to_string_list()
        final_string = ' '.join( self.str_args)
        return final_string
