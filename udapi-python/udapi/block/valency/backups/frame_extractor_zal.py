import pickle

from udapi.core.block import Block
#from udapi.block.valency.html_creator import HTML_creator

class Frame_argument:
    """ class representing verb frame argument """
    def __init__( self, deprel, case_feat, case_mark_rels):
        self.deprel = deprel            
        self.case_feat = case_feat
        if ( case_feat == "" ):
            self.case_feat = "0"                
        self.case_mark_rels = case_mark_rels
    
    def is_identical_with( self, another_frame_argument): # -> bool
        if ( self.deprel == another_frame_argument.deprel and
                self.case_feat == another_frame_argument.case_feat and
                self.case_mark_rels == another_frame_argument.case_mark_rels ):
            return True
        return False


class Example_sentence:
    """ class representing an example sentence for a verb frame
    it contains list of word forms with some information
    used in creation of HTML table
    """
    def __init__( self, actual_node, argument_nodes):
        sentence_nodes = actual_node.root.descendants
        self.tokens = []
        for node in sentence_nodes:
            token_dict = {}
            token_dict[ "form" ] = node.form
            
            if ( node == actual_node ):
                token_dict[ "highlight" ] = 2
            elif ( node in argument_nodes ):
                token_dict[ "highlight" ] = 1
            else:
                token_dict[ "highlight" ] = 0
                
            token_dict[ "space" ] = not ( node.no_space_after or node == sentence_nodes[ -1 ] )
            
            self.tokens.append( token_dict)            


class Frame:
    """ class representing verb frame with information about the verb
    and with a list of its arguments
    """
    def __init__( self, node):          
        self.verb_lemma = node.lemma
            
        self.verb_form = node.feats[ "VerbForm" ]
        if ( self.verb_form == "" ):
            self.verb_form = "0"        
            
        self.voice = node.feats[ "Voice" ]
        if ( self.voice == "" ):
            self.voice = "0"

        self.example_sentences = []        
        self.arguments = []
        self.frequency = 1
    
    def add_argument( self, new_argument): # void        
        #for old_argument in self.arguments:
        #    if ( old_argument.is_identical_with( new_argument) ):
        #        return
        self.arguments.append( new_argument)
    
    def process_example_sentence( self, node, arguments): # void
        sentence = Example_sentence( node, arguments)
        self.example_sentences.append( sentence)
    
    def has_identical_arguments_with( self, another_frame): # -> bool
        """ chceks if this frame has identical arguments with another frame """
        if ( len( self.arguments) == len( another_frame.arguments) ):
            sorted_self_args = sorted( self.arguments, key =
                    lambda arg:( arg.deprel, arg.case_feat, arg.case_mark_rels ))
            sorted_another_frame_args = sorted( another_frame.arguments, key =
                    lambda arg:( arg.deprel, arg.case_feat, arg.case_mark_rels ))
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
    
    def add_frame_instance( self, new_frame): # void
        self.frequency += 1
        self.example_sentences.append( new_frame.example_sentences[ 0 ])
    
    def arguments_to_string( self): # -> str
        """ converts verb frame arguments to string
        called while printing frames to the output in after_process_document
        """
        argument_strings_list = []
        for argument in self.arguments:
            argument_string = argument.deprel + '-' + argument.case_feat
            if ( argument.case_mark_rels != [] ):                
                argument_string += '(' + ','.join( argument.case_mark_rels) + ')'
            argument_strings_list.append(  argument_string)
        final_string = ' '.join( argument_strings_list)
        return final_string


class Verb_record:
    """ class representing one verb with possibly more verb frames """
    def __init__( self, lemma):
        self.lemma = lemma
        self.frames = []

    def add_frame( self, new_frame):
        for old_frame in self.frames:
            if ( old_frame.is_identical_with( new_frame) ):
                old_frame.add_frame_instance( new_frame)
                return                
        self.frames.append( new_frame)
        

class Frame_extractor( Block):
    """ udapi block extracting frame from each verb node and printing results to output """
    def __init__( self, output='.', **kwargs):
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
        argument = Frame_argument( deprel, case_feat, case_mark_rels)
        return argument

    def select_arguments( self, node): # -> list of Frame_arguments
        """ iterates through verb children and calls create_argument for each of them """
        frame_arguments = []
        argument_nodes = []
        for child in node.children:
            if ( child.udeprel in self.appropriate_udeprels or 
                    child.deprel in self.appropriate_deprels ):
                argument = self.create_argument( child)                
                frame_arguments.append( argument)
                argument_nodes.append( child)
        return ( frame_arguments, argument_nodes )

    def create_frame( self, node): # -> Frame
        """ creates a verb frame for a given verb node """
        frame = Frame( node)
        
        ( frame_arguments, argument_nodes ) = self.select_arguments( node)
        for argument in frame_arguments:
            frame.add_argument( argument)
        
        frame.process_example_sentence( node, argument_nodes)
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
        """ overriden block method
        printing sorted verb frames to the standard output after document processing
        """
        # sorting verb records and their frames
        verb_lemmas = self.dict_of_verbs.keys()
        for verb_lemma in verb_lemmas:
            verb_record = self.dict_of_verbs[ verb_lemma ]
            verb_record.frames.sort( key =
                    lambda frame: frame.frequency, reverse = True )
            sorted_frames = sorted( verb_record.frames, key =
                    lambda frame: ( frame.verb_form, frame.voice ))
            verb_record.frames = sorted_frames
            self.dict_of_verbs[ verb_lemma ] = verb_record
        
        # creating a html table
        p = pickle.dump( self.dict_of_verbs, open( self.output, 'wb'))
        #return
        #html_creator = HTML_creator()
        #html_creator.create_table( self.dict_of_verbs)

