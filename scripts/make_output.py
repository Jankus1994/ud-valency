import yaml
import pickle
import sys

from texter import Texter
from htmler import HTMLer
from htmler_mono import HTMLer_mono


if __name__ == "__main__":
    lang_marks = sys.argv[ 1 ]
    output_form = sys.argv[ 2 ]  # text / html
    treebank_name = sys.argv[ 3 ]
    config_name = sys.argv[ 4 ]

    with open( config_name, 'r') as config:
        config_data = yaml.load( config, Loader=yaml.FullLoader)

        if '-' not in lang_marks:
            a_lang_mark = lang_marks
            input_folder = config_data[ "m_bin_extr" ]
            input_name = input_folder + treebank_name + ".bin"
            with open( input_name, 'rb') as input_file:
                a_valency_dict = pickle.load( input_file)
                if output_form == "text":
                    output_folder = config_data[ "m_texr" ]
                    a_output_name = output_folder + treebank_name + ".txt"
                    texter = Texter()
                    texter.write_dict( a_valency_dict, a_output_name, False)
                elif output_form == "html":
                    output_folder = config_data[ "m_html" ]
                    a_output_name = output_folder + treebank_name + ".html"
                    htmler = HTMLer_mono()
                    htmler.create_html( a_valency_dict, a_output_name, a_lang_mark)

        else:
            a_lang_mark, b_lang_mark = lang_marks.split( '-')
            input_folder = config_data[ "b_bin_link" ]
            input_name = input_folder + treebank_name + ".bin"
            with open( input_name, 'rb') as input_file:
                a_b_valency_dicts = pickle.load( input_file)
                if output_form == "text":
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
