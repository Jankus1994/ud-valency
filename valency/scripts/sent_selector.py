"""
selects a given number of sentences from a parallel czech-english conllu file
and prints them to output file
used during development when not necessery to process the whole corpus
run from sent_selector.sh
"""

import sys

class Sent_selector:
    def __init__( self, sents_num, input_filename, output_filename, \
                    a_zone_mark, b_zone_mark):
        self.sents_num = sents_num
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.a_zone_mark = a_zone_mark
        self.b_zone_mark = b_zone_mark

    def select( self):
        with open( input_filename, 'r', encoding="utf-8") as input_file, \
                open( output_filename, 'w', encoding="utf-8") as output_file:
            previous_sent_id = "" #
            sent_num = 0 #
            for input_line in input_file:
                if "# sent_id = " in input_line:
                    sent_id = input_line.lstrip( "# sent_id = ")
                    if "/" + self.a_zone_mark in sent_id:  # e.g. /CS
                        plain_sent_id = int( sent_id.rstrip( \
                                        "/" + self.a_zone_mark  + "\n"))
                    elif "/" + self.b_zone_mark in sent_id:
                        plain_sent_id = int( sent_id.rstrip( \
                                        "/" + self.b_zone_mark + "\n"))
                    if plain_sent_id != previous_sent_id: #
                        sent_num += 1 #
                        previous_sent_id = plain_sent_id #
                    if sent_num > self.sents_num: #
                        break #
                    #if plain_sent_id > self.sents_num:
                    #    break
                 
                output_file.write( input_line)



if __name__ == "__main__":
    if len( sys.argv) == 6:
        sents_num = int( sys.argv[ 1 ])
        input_filename = sys.argv[ 2 ]
        output_filename = sys.argv[ 3 ]
        a_zone_mark = sys.argv[ 4 ]
        b_zone_mark = sys.argv[ 5 ]

        sent_selector = Sent_selector( sents_num, input_filename, output_filename, \
                                            a_zone_mark, b_zone_mark)
        sent_selector.select()
