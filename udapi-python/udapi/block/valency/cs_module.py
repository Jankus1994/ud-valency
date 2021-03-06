"""
overriden methods of general classes, specific for Czech
"""

from udapi.block.valency.frame_extractor import *
from udapi.block.valency.frame import *

class Cs_frame_type_argument( Frame_type_argument):
    def __init__( self, node, deprel="", case_feat="", case_mark_rels=[]):
        is_numerative  = False
        if node is not None:
            is_numerative, original_case = self.consider_numerative( node)
        super().__init__( node, deprel, case_feat, case_mark_rels)
        if is_numerative:
            self.case_feat = original_case

    @staticmethod
    def consider_numerative( node):
        original_case = ""
        for child in node.children:
            if child.deprel in [ "nummod:gov", "det:numgov" ]:
                original_case = child.feats[ "Case" ]
                return True, original_case
        return False, original_case

#class Cs_frame_instance_argument( Cs_frame_type_argument):
#    def __init__( self, node):
#        self.node = node
#        #self.translations = []
#        super().__init__( node)


#class Cs_frame_instance( Frame_instance):
#    def __init__( self, frame_type, verb_node):
#        super().__init__( frame_type, verb_node):
#        self.argument_class = Cs_frame_instance_argument


class Cs_frame_type( Frame_type):
    def __init__( self, verb_node):
        self.elided_tokens = []
        super().__init__( verb_node)
        self.argument_class = Cs_frame_type_argument
        self.verb_form = "0"  # not setting vf and voice - is it ok??
        self.voice = "0"

    def process_arguments( self, verb_node):
        super().process_arguments( verb_node)
        self.arguments = self.transform_reflex_passive( self.arguments)
        self.arguments = self.process_elided_arguments( verb_node, self.arguments)
        self.sort_arguments()

    def process_first_instance( self):
        # elided tokens filled in process_elided_arguments
        self.first_frame_instance.process_sentence( self.elided_tokens)
        self.instances.append( self.first_frame_instance)


    def transform_reflex_passive( self, frame_args): # -> list of transformed Frame_arguments
        """ tranforming frames with reflexive passive construction to their active equivalent
        zahrada se kosi -> kosi zahradu
        expl:pass-Acc -> 0, nsubj:pass-Nom -> obj-Acc
        """
        expl_arg = Cs_frame_type_argument( None, "expl:pass", "Acc", [])
        nsubj_arg = Cs_frame_type_argument( None, "nsubj:pass", "Nom", [])
        obj_arg = Cs_frame_type_argument( None, "obj", "Acc", [])
        if any( arg.is_identical_with( expl_arg) for arg in frame_args) and \
                any( arg.is_identical_with( nsubj_arg) for arg in frame_args):
            frame_args = self.remove_arg( frame_args, expl_arg)
            frame_args = self.subst_arg( frame_args, nsubj_arg, obj_arg)
        return frame_args

    @staticmethod
    def subst_arg( frame_args, old_arg, new_arg): # -> list of transformed Frame_arguments
        """ substitution of old_arg with new_arg """
        return [ new_arg if arg.is_identical_with( old_arg) \
                         else arg for arg in frame_args ]
    @staticmethod
    def remove_arg( frame_args, rem_arg): # -> list of transformed Frame_arguments
        """ removing rem_arg from list of frame arguments """
        return [ arg for arg in frame_args if not arg.is_identical_with( rem_arg) ]

    def process_elided_arguments( self, verb_node, frame_arguments):
        elided_argument, elided_token = \
                self.consider_elided_subject( verb_node, frame_arguments)
        if elided_argument is not None:
            frame_arguments.append( elided_argument)
            self.elided_tokens.append( elided_token)
        elif not self.args_include_subject( frame_arguments):
            subject_arg = Cs_frame_type_argument( None, "nsubj", "Nom", [])
            frame_arguments.append( subject_arg)
        return frame_arguments

    def consider_elided_subject( self, node, frame_args):
        for frame_arg in frame_args:
            if frame_arg.deprel == "nsubj" or frame_arg.deprel == "csubj":
                return None, None

        # the verb (node) does not have a subject:
        token_person_1_2 = self.get_token_of_person_1_2( node)
        if token_person_1_2 is not None:
            elided_argument = Cs_frame_type_argument( None, "nsubj", "Nom", [])
            return elided_argument, token_person_1_2

        # looking for an auxiliary verb, which would confirm the 1./2. person
        for child in node.children:
            if child.upos == "AUX":
                token_person_1_2 = self.get_token_of_person_1_2( child)
                if token_person_1_2 is not None:
                    elided_argument = Cs_frame_type_argument( None, "nsubj", "Nom", [])
                    return elided_argument, token_person_1_2

        # the node can be a complement of a parant verb, which could confirm the 1./2. person
        if node.deprel == "xcomp" and node.parent.upos == "VERB":
            token_person_1_2 = self.get_token_of_person_1_2( node.parent)
            if token_person_1_2 is not None:
                elided_argument = Cs_frame_type_argument( None, "nsubj", "Nom", [])
                return elided_argument, token_person_1_2

        return None, None

    @staticmethod
    def get_token_of_person_1_2( node):
        token = None
        if node.feats["Person"] == "1":
            if node.feats["Number"] == "Sing":
                token = "já"
            elif node.feats["Number"] == "Plur":
                token = "my"
        elif node.feats["Person"] == "2":
            if node.feats["Number"] == "Sing":
                token = "ty"
            elif node.feats["Number"] == "Plur":
                token = "vy"
        return token

    @staticmethod
    def args_include_subject( frame_args):
        for frame_arg in frame_args:
            if "nsubj" in frame_arg.deprel or "csubj" in frame_arg.deprel:
                return True
        return False


class Cs_verb_record( Verb_record):
    def __init__( self, lemma):
        super().__init__( lemma)
        self.frame_type_class = Cs_frame_type

    def delete_subframes( self):
        frame_types = sorted( self.frame_types, key = \
                lambda arg:len( arg.str_arguments))
        reduced_frame_types = []
        # comparing frames and marking those to delete
        for frame_type in frame_types:
            frame_type.args_to_one_string()
        for frame_type_1 in frame_types:
            # a frame should be deleted if it has a superframe
            frame_type_1_superframes = []
            for frame_type_2 in frame_types:
                frame_1_arg_len = len( frame_type_1.str_arguments)
                frame_2_arg_len = len( frame_type_2.str_arguments)
                frame_1_arg_set = set( frame_type_1.str_arguments)
                frame_2_arg_set = set( frame_type_2.str_arguments)
                if frame_1_arg_len < frame_2_arg_len and \
                        frame_1_arg_set.issubset( frame_2_arg_set):
                    frame_type_1_superframes.append( frame_type_2)

            if frame_type_1_superframes == []:
                reduced_frame_types.append( frame_type_1)
            else:                         
                # !!! we take the biggest (ie. last) superframe - IS IT CORRECT ??? !!!
                # !!! what about sorting the other way around -
                # - could stop after first superframe found with high freq !!!
                biggest_superframe = frame_type_1_superframes[ -1 ]
                # we mark the superframe only if the subframe has
                # a low frequency compared to the superframe                
                if self.compare_instances_number( frame_type_1, biggest_superframe):
                    biggest_superframe.instances += frame_type_1.instances
                else:
                    reduced_frame_types.append( frame_type_1)
        self.frame_types = reduced_frame_types

    @staticmethod
    def compare_instances_number( subframe, superframe): # -> bool
        """ comparing number of instances of a subframe and a superframe
        returns if the superframe is sufficiently more frequent than the subframe
        """
        coef = 2 # !!! 
        if coef * len( subframe.instances) < len( superframe.instances):
            return True
        return False

        
    
class Cs_frame_extractor( Frame_extractor):
    def __init__( self, pickle_output = None):
        super().__init__( pickle_output)
        self.verb_record_class = Cs_verb_record
        #self.cs_dict_of_verbs = {}

    def after_process_document( self, doc): # void
        for verb_record in self.dict_of_verbs.values():
            verb_record.delete_subframes()  # reducing number of frames before outputting
        super().after_process_document( doc)

