import pickle
from udapi.block.valency.verb_record import Verb_record

class Frame_extractor():
    """ tool used by frame_aligner to extract frames from each verb node """
    appropriate_udeprels = ["nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl"]
    appropriate_deprels = ["obl:arg", "obl:agent"]

    def __init__( self, pickle_output = None):
        self.verb_record_class = Verb_record
        self.pickle_output = pickle_output
        self.dict_of_verbs = {}
    
    def process_node( self, node): # void
        """ searching verbs and calling create_frame for them """
        if node.upos == "VERB":
            if node.lemma in self.dict_of_verbs:
                verb_record = self.dict_of_verbs[ node.lemma ]
            else:
                verb_record = self.verb_record_class( node.lemma)
                self.dict_of_verbs[ node.lemma ] = verb_record
            frame_instance = verb_record.process_frame( node)
            return frame_instance
        return None

    def after_process_document( self, _): # void
        # sorting verb records and their frames
        print( len( self.dict_of_verbs))
        verb_lemmas = sorted( self.dict_of_verbs.keys())
        for verb_lemma in verb_lemmas:
            verb_record = self.dict_of_verbs[ verb_lemma ]
            verb_record.frame_types.sort( key = \
                    lambda frame_type: len( frame_type.instances), reverse = True )
            sorted_frame_types = sorted( verb_record.frame_types, key = \
                    lambda frame_type: ( frame_type.verb_form, frame_type.voice ))
            verb_record.frame_types = sorted_frame_types
            self.dict_of_verbs[ verb_lemma ] = verb_record

        # two options of output, depending on if the output pickle file was specified
        if self.pickle_output is None:
            self.print_raw_frames( verb_lemmas)
        else:
            self.pickle_dict()

    def print_raw_frames( self, verb_lemmas):
        for verb_lemma in verb_lemmas:
            verb_record = self.dict_of_verbs[ verb_lemma ]
            for frame_type in verb_record.frame_types:            
                print( "{:<20}{:<7}{:<7}{:<80}{:<7}".format(
                        frame_type.verb_lemma,
                        frame_type.verb_form,
                        frame_type.voice,
                        ": " + frame_type.args_to_one_string(),
                        "= " + str( len( frame_type.instances)))
                )
    def pickle_dict( self):
        p = pickle.dump( self.dict_of_verbs, open( self.pickle_output, 'wb'))

    def process_tree( self, tree):
        frame_instances = []
        for node in tree.descendants:
            frame_instance = self.process_node( node)
            if frame_instance is not None:
                frame_instances.append( frame_instance)
        return frame_instances
