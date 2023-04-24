import pickle

from udapi.core.block import Block
#from udapi.block.valency.html_creator import HTML_creator

class Frame_argument:
    """ class representing verb frame argument """
    def __init__( self, deprel, case_feat, case_mark_rels, example_node):
        self.deprel = deprel            
        self.case_feat = case_feat
        if ( case_feat == "" ):
            self.case_feat = "0"                
        self.case_mark_rels = case_mark_rels
        self.example_node = example_node  # for later highlighting in the example sentence
    
    def is_identical_with( self, another_frame_argument): # -> bool
        if ( self.deprel == another_frame_argument.deprel and
                self.case_feat == another_frame_argument.form and
                self.case_mark_rels == another_frame_argument.case_mark_rels ):
            return True
        return False


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
            token_dict[ "form" ] = node._form
            
            if ( node == actual_node ):
                token_dict[ "highlight" ] = 2
            elif ( node in argument_nodes ):
                token_dict[ "highlight" ] = 1
            else:
                token_dict[ "highlight" ] = 0
                
            token_dict[ "space" ] = not ( node.no_space_after or node == sentence_nodes[ -1 ] )
            
            self.tokens.append( token_dict)

        self.elided_tokens = []
        for elided_token in elided_tokens:
            elided_token_dict = {}
            elided_token_dict[ "form" ] = elided_token
            elided_token_dict[ "highlight" ] = 1  # we suppose that all elided tokens are frame arguments
            self.elided_tokens.append( elided_token_dict)



class Frame:
    """ class representing verb frame with information about the verb
    and with a list of its arguments
    """
    def __init__( self, node, ):
        self.verb_lemma = node.lemma
        self.verb_form = "0" 
        self.voice = "0"

        self.example_sentences = []        
        self.arguments = []
        self.str_arguments = [] # filled with args_to_string_list
        self.superframe = None # frame containng this frame - for the final frame reduction
        self.frequency = 1
    
    def set_verb_form( self, verb_form):
        if ( self.verb_form != "" ):
            self.verb_form = verb_form       

    def set_voice( self, voice):
        if ( self.voice != "" ):
            self.voice = voice
    
    def add_argument( self, new_argument): # void
        self.arguments.append( new_argument)
    
    def process_example_sentence( self, node, arguments, elided_tokens = []):  # void
        sentence = Example_sentence(node, arguments)
        assert( hasattr( sentence, "elided_tokens"))
        self.example_sentences.append( sentence)
    
    def has_identical_arguments_with( self, another_frame): # -> bool
        """ chceks if this frame has identical arguments with another frame """
        if ( len( self.arguments) == len( another_frame.arguments) ):
            sorted_self_args = sorted(self.arguments, key =
                    lambda arg:(arg.deprel, arg.form, arg.case_mark_rels))
            sorted_another_frame_args = sorted(another_frame.arguments, key =
                    lambda arg:(arg.deprel, arg.form, arg.case_mark_rels))
            for i in range( len( sorted_self_args)):
                if not ( sorted_self_args[ i ].is_identical_with( sorted_another_frame_args[ i ]) ):
                    return False
            return True
        return False
    
    def is_identical_with( self, another_frame): # -> bool
        """ chceks if this frame is identical with another frame """
        if ( self.verb_lemma == another_frame.verb_lemma and
                self.verb_form == another_frame.verb_form and
                self.voice == another_frame.voice and
                self.has_identical_arguments_with( another_frame) ):
            return True
        return False
    
    def add_frame_instance( self, example_sentence): # void
        self.frequency += 1
        self.example_sentences.append( example_sentence)

    def args_to_string_list( self):
        """ converts Frame_arguments to their string representation
        and saves them into the str_arguments attribute of the frame
        """
        self.str_arguments = []
        for argument in self.arguments:
            argument_string = argument.deprel + '-' + argument.form
            if ( argument.case_mark_rels != [] ):
                argument_string += '(' + ','.join( argument.case_mark_rels) + ')'
            self.str_arguments.append( argument_string)
    
    def args_to_one_string( self): # -> str
        """ creates one long string of all frame arguments """
        self.args_to_string_list()
        final_string = ' '.join( self.str_arguments)
        return final_string


class Verb_record:
    """ class representing one verb with possibly more verb frames """
    def __init__( self, lemma):
        self.lemma = lemma
        self.frames = []

    def add_frame( self, new_frame):
        for old_frame in self.frames:
            if ( old_frame.is_identical_with( new_frame) ):
                old_frame.add_frame_instance( new_frame.example_sentences[ 0 ])
                return
        self.frames.append( new_frame)
        

class Frame_extractor( Block):
    """ udapi block extracting frame from each verb node and printing results to output """
    def __init__( self, output = None, **kwargs):
        super().__init__( **kwargs)
        self.appropriate_udeprels = [ "nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl" ]
        self.appropriate_deprels = [ "obl:arg", "obl:agent" ]
        self.dict_of_verbs = {}
        self.output = output

    def create_argument( self, node): # -> Frame_argument
        """ creates Frame_argument from a node depending on a verb """
        deprel = node.deprel
        case_feat = node.feats[ "Case" ]
        case_mark_rels = []
        for child in node.children:
            if ( child.deprel in [ "case", "mark" ] ):
                case_mark_rel = child.deprel + '-' + child.lemma
                case_mark_rels.append( case_mark_rel)
        argument = Frame_argument( deprel, case_feat, case_mark_rels, node)
        return argument

    def select_arguments( self, node): # -> list of Frame_arguments
        """ iterates through verb children and calls create_argument for each of them """
        frame_arguments = []
        for child in node.children:
            if ( child.udeprel in self.appropriate_udeprels or 
                    child.deprel in self.appropriate_deprels ):
                argument = self.create_argument( child)                
                frame_arguments.append( argument)
        return frame_arguments

    def create_frame( self, node): # -> Frame
        """ creates a verb frame for a given verb node """
        frame = Frame( node)
        frame.set_verb_form( node.feats[ "VerbForm" ])
        frame.set_voice( node.feats[ "Voice" ])
        
        frame_arguments = self.select_arguments( node)
        for argument in frame_arguments:
            frame.add_argument( argument)
        
        frame.process_example_sentence( node, [ arg.example_node for arg in frame.arguments ])
        return frame
    
    def process_node( self, node): # void
        """ overridden block method
        searching verbs and calling create_frame for them
        """
        if ( node.upos == "VERB" ):
            if ( node.lemma in self.dict_of_verbs ):
                verb_record = self.dict_of_verbs[ node.lemma ]
            else:
                verb_record = Verb_record( node.lemma)
                self.dict_of_verbs[ node.lemma ] = verb_record
            verb_frame = self.create_frame( node)
            verb_record.add_frame( verb_frame)

    def after_process_document( self, _): # void
        """ overriden block method, processing output """
        # sorting verb records and their frames
        verb_lemmas = sorted( self.dict_of_verbs.keys())
        for verb_lemma in verb_lemmas:
            verb_record = self.dict_of_verbs[ verb_lemma ]
            verb_record.frames.sort( key =
                    lambda frame: frame.frequency, reverse = True )
            sorted_frames = sorted( verb_record.frames, key =
                    lambda frame: ( frame.verb_form, frame.voice ))
            verb_record.frames = sorted_frames
            self.dict_of_verbs[ verb_lemma ] = verb_record

        # two options of output, depending on if the output pickle file was specified
        if ( self.output is None ):
            self.print_raw_frames( verb_lemmas)
        else:
            self.pickle_dict()

    def print_raw_frames( self, verb_lemmas):
         for verb_lemma in verb_lemmas:
            verb_record = self.dict_of_verbs[ verb_lemma ]
            for frame in verb_record.frames:            
                print( "{:<20}{:<7}{:<7}{:<80}{:<7}".format(
                        frame.verb_lemma,
                        frame.verb_form,
                        frame.voice,
                        ": " + frame.args_to_one_string(),
                        "= " + str( frame.frequency))
                )
    def pickle_dict( self):
        p = pickle.dump( self.dict_of_verbs, open( self.output, 'wb'))

    # def process_tree( self, tree):
    #     print( "FET")
    #     super().process_tree( tree)
