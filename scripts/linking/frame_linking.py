import yaml
import pickle
import sys

from texter import Texter
from htmler import HTMLer

from base_linker import Base_linker
from fa_linker import Fa_linker
from ud_linker import Ud_linker
from sim_linker import Sim_linker
from comb_linker import Comb_linker
from dist_measurer import Dist_measurer
from cs_sk_dist_measurer import Cs_Sk_dist_measurer
from link_structures import Frame_type_link

def get_linker( link_config_name):
    with open( link_config_name) as link_config:
        link_config_dict = yaml.load( link_config, Loader=yaml.FullLoader)
        base_linker = Base_linker()

        fa_linker_dict = link_config_dict[ "Fa_linker" ]
        fa_onedir = int( fa_linker_dict[ "onedirectional" ])
        fa_threshold = int( fa_linker_dict[ "threshold" ])
        fa_linker = Fa_linker( onedir_weight=fa_onedir, threshold=fa_threshold)

        ud_linker_dict = link_config_dict[ "Ud_linker" ]
        ud_verb_parent_ord = int( ud_linker_dict[ "verb_parent_ord" ])
        ud_verb_parent_upos = int( ud_linker_dict[ "verb_parent_upos" ])
        ud_verb_ord = int( ud_linker_dict[ "verb_ord" ])
        ud_verb_deprel = int( ud_linker_dict[ "verb_deprel" ])
        ud_verb_depth = int( ud_linker_dict[ "verb_depth" ])
        ud_verb_child_num = int( ud_linker_dict[ "verb_child_num" ])
        ud_threshold = int( ud_linker_dict[ "threshold" ])
        ud_params = ( ud_verb_parent_ord, ud_verb_parent_upos, ud_verb_ord,
                      ud_verb_deprel, ud_verb_depth, ud_verb_child_num )
        ud_linker = Ud_linker( params_weights=ud_params, threshold=ud_threshold)

        sim_linker_dict = link_config_dict[ "Sim_linker" ]
        sim_allow_subst = bool( int( sim_linker_dict[ "substitutions_allowed" ]))
        sim_spec_cs_sk_measurer = bool( int( sim_linker_dict[ "spec_cs_sk_measurer" ]))
        sim_threshold = sim_linker_dict[ "threshold" ]
        measurer = Dist_measurer()
        if sim_spec_cs_sk_measurer:
            measurer = Cs_Sk_dist_measurer
        sim_linker = Sim_linker( measurer_features=( measurer,
                                                     { "allow_substitution":
                                                       bool( sim_allow_subst) }),
                                threshold=sim_threshold)

        comb_linker_dict = link_config_dict[ "Comb_linker" ]
        comb_base = comb_linker_dict[ "base_linker" ]
        comb_fa = comb_linker_dict[ "fa_linker" ]
        comb_ud = comb_linker_dict[ "ud_linker" ]
        comb_sim = comb_linker_dict[ "sim_linker" ]
        comb_threshold =  comb_linker_dict[ "threshold" ]
        linkers = [ base_linker, fa_linker, ud_linker, sim_linker ]
        weights = [ comb_base, comb_fa, comb_ud, comb_sim ]
        comb_linker = Comb_linker( linkers, weights, threshold=comb_threshold)

        alignment_needed = False
        if comb_fa:
            alignment_needed = True

        return comb_linker, alignment_needed

def create_align_maps( align_line):
    word_alignments = align_line.split()
    a_b_align_map = {}
    b_a_align_map = {}
    for word_alignment in word_alignments:
        if '<' in word_alignment:
            sign = '<'
        elif '>' in word_alignment:
            sign = '>'
        else: #if '=' in word_alignment:
            sign = '='
        a_index_str, b_index_str = word_alignment.split( sign)
        a_index = int( a_index_str) + 1
        b_index = int( b_index_str) + 1
        if sign in [ '>', '=']:  # TODO skontrolovat spravny smer
            a_b_align_map[ a_index ] = b_index
        if sign in [ '<', '=']:
            b_a_align_map[ b_index ] = a_index
    return a_b_align_map, b_a_align_map


def link( lang_marks, insts_tuples, link_config_name, align_name):
    linker, alignment_needed = get_linker( link_config_name)
    align_lines = [ "" ] * len( insts_tuples)
    if alignment_needed:
        with open( align_name, 'r') as align_file:
            actual_align_lines = align_file.readlines()
            assert len( insts_tuples) == len( actual_align_lines)
            align_lines = actual_align_lines

    for insts_tuple, align_line in zip( insts_tuples, align_lines):
        a_frame_insts, b_frame_insts = insts_tuple
        a_b_align_map, b_a_align_map = create_align_maps( align_line)
        frame_pairs = linker.link_sent_frames( a_frame_insts, b_frame_insts,
                                               a_b_align_map, b_a_align_map)

        for frame_pair in frame_pairs:
            # linking frame types
            # if the frame type link does not exist yet, create one
            a_frame_type = frame_pair.a_frame_type
            b_frame_type = frame_pair.b_frame_type
            a_b_frame_type_link = a_frame_type.find_link_with( b_frame_type)
                    # could be done the other way around: b_frame.find( frst_frame)
            if a_b_frame_type_link is None:
                a_b_frame_type_link = Frame_type_link( a_frame_type, b_frame_type)
            # linking frame instances
            a_frame_inst = frame_pair.a_frame_inst
            b_frame_inst = frame_pair.b_frame_inst
            a_b_frame_type_link.link_frame_insts( a_frame_inst, b_frame_inst)


if __name__ == "__main__":
    lang_marks = sys.argv[ 1 ]
    output_form = sys.argv[ 2 ]  # bin / text / html
    treebank_name = sys.argv[ 3 ]
    config_name = sys.argv[ 4 ]

    with open( config_name, 'r') as config:
        config_data = yaml.load( config, Loader=yaml.FullLoader)
        link_config = config_data[ "link_config" ]
        align_name = config_data[ "b_aligned" ] + treebank_name
        input_name = config_data[ "b_bin_extr" ] + treebank_name + ".bin"
        link_config_name = config_data[ "link_config" ]

        with open( input_name, 'rb') as input_file:
            print( "Loading data to link...", file=sys.stderr)
            insts_tuples, a_b_valency_dicts = pickle.load( input_file)
            # tha instances in the tuples are part of the dictionary structures,
            # so their linking is done also in a_b_valency_dicts
            print( "Linking...", file=sys.stderr)
            link( lang_marks, insts_tuples, link_config_name, align_name)

            print( "Processing linked output...", file=sys.stderr)
            if output_form == "bin":
                output_name = config_data[ "b_bin_link" ] + treebank_name + ".bin"
                sys.setrecursionlimit( 50000)
                pickle.dump( a_b_valency_dicts, open( output_name, 'wb'))
            elif output_form == "text":
                a_b_valency_dict, b_a_valency_dict = a_b_valency_dicts
                a_lang_mark, b_lang_mark = lang_marks.split( '-')
                a_output_name = config_data[ "b_text" ] + treebank_name + "." + \
                                a_lang_mark + ".txt"
                b_output_name = config_data[ "b_text" ] + treebank_name + "." + \
                                b_lang_mark + ".txt"
                texter = Texter()
                texter.write_dict( a_b_valency_dict, a_output_name, True)
                texter.write_dict( b_a_valency_dict, b_output_name, True)
            elif output_form == "html":
                a_b_valency_dict, b_a_valency_dict = a_b_valency_dicts
                a_lang_mark, b_lang_mark = lang_marks.split( '-')
                a_output_name = config_data[ "b_html" ] + treebank_name + "." + \
                                a_lang_mark + ".html"
                b_output_name = config_data[ "b_html" ] + treebank_name + "." + \
                                b_lang_mark + ".html"
                htmler = HTMLer()
                htmler.create_html( a_b_valency_dict, a_output_name,
                                   a_lang_mark, b_lang_mark)
                htmler = HTMLer()
                htmler.create_html( b_a_valency_dict, b_output_name,
                                    b_lang_mark, a_lang_mark)


