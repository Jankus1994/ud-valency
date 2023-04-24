from udapi.core.block import Block

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
                self.case_feat == another_frame_argument.form and
                self.case_mark_rels == another_frame_argument.case_mark_rels ):
            return True
        return False


class Frame:
    """ classs representing verb frame with information about the verb
    and with a list of its arguments
    """
    def __init__( self, verb_lemma, verb_form, voice):
        self.verb_lemma = verb_lemma
            
        self.verb_form = verb_form
        if ( verb_form == "" ):
            self.verb_form = "0"        
            
        self.voice = voice
        if ( voice == "" ):
            self.voice = "0"          
        
        self.arguments = []
        self.frequency = 1 
    
    def add_argument( self, new_argument): # void
        #for old_argument in self.arguments:
        #    if ( old_argument.is_identical_with( new_argument) ):
        #        return
        self.arguments.append( new_argument)
    
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
    
    def increment_frequency( self): # void
        self.frequency += 1
    
    def arguments_to_string( self): # -> str
        """ converts verb frame arguments to string
        called while printing frames to the output in after_process_document
        """
        argument_strings_list = []
        for argument in self.arguments:
            argument_string = argument.deprel + '-' + argument.form
            if ( argument.case_mark_rels != [] ):                
                argument_string += '(' + ','.join( argument.case_mark_rels) + ')'
            argument_strings_list.append(  argument_string)
        final_string = ", ".join( argument_strings_list)
        return final_string


class Verb_record:
    """ class representing one verb with possibly more verb frames """
    def __init__( self, lemma):
        self.lemma = lemma
        self.frames = []

    def add_frame( self, new_frame):
        for old_frame in self.frames:
            if ( old_frame.is_identical_with( new_frame) ):
                old_frame.increment_frequency()
                return                
        self.frames.append( new_frame)
        

class Old_frame_extractor( Block):
    """ udapi block extracting frame from each verb node and printing results to output """
    def __init__( self):
        super().__init__()
        self.appropriate_udeprels = [ "nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl" ]
        self.appropriate_deprels = [ "obl:arg", "obl:agent" ]
        self.dict_of_verbs = {}

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
        arguments = []
        for child in node.children:
            if ( child.udeprel in self.appropriate_udeprels or 
                    child.deprel in self.appropriate_deprels ):
                argument = self.create_argument( child)                
                arguments.append( argument)
        return arguments

    def create_frame( self, node): # -> Frame
        """ creates a verb frame for a given verb node """
        verb_lemma = node.lemma
        verb_form = node.feats[ "VerbForm" ]
        voice = node.feats[ "Voice" ]
        frame = Frame( verb_lemma, verb_form, voice)

        arguments = self.select_arguments( node)
        for argument in arguments:
            frame.add_argument( argument)

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
        sorted_verb_lemmas = sorted( self.dict_of_verbs.keys())
        for verb_lemma in sorted_verb_lemmas:
            verb_record = self.dict_of_verbs[ verb_lemma ]
            verb_record.frames.sort( key =
                    lambda frame: frame.frequency, reverse = True )
            sorted_frames = sorted( verb_record.frames, key =
                    lambda frame: ( frame.verb_form, frame.voice ))
            for frame in sorted_frames:            
                print( "{:<20}{:<7}{:<7}{:<80}{:<7}".format(                    
                        frame.verb_lemma,
                        frame.verb_form,
                        frame.voice,
                        ": " + frame.arguments_to_string(),
                        "= " + str( frame.frequency))
                )
