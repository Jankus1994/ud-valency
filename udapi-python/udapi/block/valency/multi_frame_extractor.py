import logging
import pickle
import yaml
import sys
#import os

from udapi.core.block import Block
from texter import Texter
from htmler_mono import HTMLer_mono

from base_frame_extractor import Base_frame_extractor
from frame_extractor import Frame_extractor
from csk_frame_extractor import Csk_frame_extractor
from cs_frame_extractor import Cs_frame_extractor
from sk_frame_extractor import Sk_frame_extractor
from en_frame_extractor import En_frame_extractor



class Multi_frame_extractor( Block):
    spec_extractors = {
        "cs": Cs_frame_extractor,
        "sk": Sk_frame_extractor,
        "en": En_frame_extractor,
        "csk": Csk_frame_extractor,
        "main": Frame_extractor,
        "base": Base_frame_extractor,
    }

    def __init__( self, lang_marks, output_form, treebank_name, config_name, **kwargs):
        super().__init__( **kwargs)

        if '-' in lang_marks:
            self.a_lang_mark, self.b_lang_mark = lang_marks.split( '-')
            monolingual = False
        else:
            self.a_lang_mark = lang_marks
            monolingual = True
        self.output_form = output_form
        self.treebank_name = treebank_name

        with open( config_name, 'r') as file:
            self.config_data = yaml.load( file, Loader=yaml.FullLoader)
            extr_config = self.config_data[ "extr_config" ]

            a_explicit_code = self.config_data[ "a_explicit_extractor" ]
            a_extractor_class = self.get_extractor_class( a_explicit_code, self.a_lang_mark)
            self.a_frame_extractor = a_extractor_class( config_name=extr_config)

            if monolingual:
                self.before_process_document = self.mono_before_process_document
                self.process_tree = self.mono_process_tree
                self.after_process_document = self.mono_after_process_document

            else:
                b_explicit_code = self.config_data[ "b_explicit_extractor" ]
                b_extractor_class = self.get_extractor_class( b_explicit_code, self.b_lang_mark)
                self.b_frame_extractor = b_extractor_class( config_name=extr_config)

                self.before_process_document = self.bi_before_process_document
                self.process_bundle = self.bi_process_bundle
                self.after_process_document = self.bi_after_process_document
                self.insts_pairs = []


    def get_extractor_class( self, explicit_code, lang_mark):
        if explicit_code in self.spec_extractors:
            return self.spec_extractors[ explicit_code ]
        if lang_mark in self.spec_extractors:
            return self.spec_extractors[ lang_mark ]
        return Frame_extractor

    def mono_before_process_document( self, doc):
        self.a_frame_extractor.before_process_document( doc)

    def bi_before_process_document( self, doc):
        self.a_frame_extractor.before_process_document(doc)
        self.b_frame_extractor.before_process_document(doc)

    def mono_process_tree( self, tree):
        self.a_frame_extractor.process_tree( tree)

    def bi_process_bundle( self, bundle):
        a_frame_insts = []
        b_frame_insts = []
        for tree_root in bundle.trees:
            if tree_root.zone == self.a_lang_mark:
                a_frame_insts = self.a_frame_extractor.process_tree( tree_root)
            elif tree_root.zone == self.b_lang_mark:
                b_frame_insts = self.b_frame_extractor.process_tree( tree_root)

        insts_pair = ( a_frame_insts, b_frame_insts )
        self.insts_pairs.append( insts_pair)

    def mono_after_process_document( self, doc):
        self.a_frame_extractor.after_process_document( doc)
        a_dict_of_verbs = self.a_frame_extractor.get_dict_of_verbs()

        if self.output_form == "bin":
            self.dump_result( a_dict_of_verbs, self.config_data[ "m_bin_extr" ])
        elif self.output_form == "text":
            output_folder = self.config_data[ "m_text" ]
            a_output_name = output_folder + self.treebank_name + ".txt"
            texter = Texter()
            texter.write_dict( a_dict_of_verbs, a_output_name, False)
        elif self.output_form == "html":
            output_folder = self.config_data[ "m_html" ]
            a_output_name = output_folder + self.treebank_name + ".html"
            htmler = HTMLer_mono()
            htmler.create_html( a_dict_of_verbs, a_output_name, self.a_lang_mark)


    def bi_after_process_document( self, doc):
        self.a_frame_extractor.after_process_document( doc)
        self.b_frame_extractor.after_process_document( doc)
        a_dict_of_verbs = self.a_frame_extractor.get_dict_of_verbs()
        b_dict_of_verbs = self.b_frame_extractor.get_dict_of_verbs()
        a_b_dicts_of_verbs = a_dict_of_verbs, b_dict_of_verbs

        if self.output_form == "bin":
            output_data = (self.insts_pairs, a_b_dicts_of_verbs)
            self.dump_result( output_data, self.config_data[ "b_bin_extr" ])
        elif self.output_form == "text":
            # we save two unlinked text dictionaries in monolingual folder
            output_folder = self.config_data[ "m_text" ]
            a_output_name = output_folder + self.treebank_name + "." + \
                            self.a_lang_mark + ".txt"
            b_output_name = output_folder + self.treebank_name + "." + \
                            self.b_lang_mark + ".txt"
            texter = Texter()
            texter.write_dict( a_dict_of_verbs, a_output_name, False)
            texter.write_dict( b_dict_of_verbs, b_output_name, False)
        elif self.output_form == "html":
            a_output_name = self.config_data[ "m_html" ] + self.treebank_name + \
                            "." + self.a_lang_mark + ".html"
            b_output_name = self.config_data[ "m_html" ] + self.treebank_name + \
                            "." + self.b_lang_mark + ".html"
            htmler = HTMLer_mono()
            htmler.create_html( a_dict_of_verbs, a_output_name, self.a_lang_mark)
            htmler = HTMLer_mono()
            htmler.create_html( b_dict_of_verbs, b_output_name, self.b_lang_mark)

    def dump_result( self, data_to_dump, output_folder):
        output_name = output_folder + self.treebank_name + ".bin"
        sys.setrecursionlimit( 50000)
        pickle.dump( data_to_dump, open( output_name, 'wb'))