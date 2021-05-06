"""
selects a given number of sentences from a parallel czech-english conllu file
and prints them to output file
used during development when not necessery to process the whole corpus
run from sent_selector.sh
"""

import sys

class Merged_selector:
    def __init__( self, sents_num, input_filename, output_filename):
        self.sents_num = sents_num
        self.input_filename = input_filename
        self.output_filename = output_filename

    def select( self):
        with open( input_filename, 'r') as input_file, \
                open( output_filename, 'w') as output_file:
            for input_line in input_file:
                if "# sent_id = " in input_line:
                    sent_id = input_line.lstrip( "# sent_id = ")
                    if "/cs" in sent_id:
                        plain_sent_id = int( sent_id.rstrip( "/cs\n"))
                    elif "/en" in sent_id:
                        plain_sent_id = int( sent_id.rstrip( "/en\n"))

                    if plain_sent_id > self.sents_num:
                        break
                 
                output_file.write( input_line)



if __name__ == "__main__":
    if len( sys.argv) == 4:
        sents_num = int( sys.argv[ 1 ])
        input_filename = sys.argv[ 2 ]
        output_filename = sys.argv[ 3 ]

        merged_selector = Merged_selector( sents_num, input_filename, output_filename)
        merged_selector.select()
