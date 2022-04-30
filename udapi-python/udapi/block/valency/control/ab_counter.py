from collections import defaultdict

"""
class counting general items for two languages
can count groups of items, creates frequency dictcionaries
"""

class AB_counter:
    def __init__( self, name):
        self.name = name
        self.a_count = 0
        self.b_count = 0
        self.a_dict = defaultdict( lambda:0)
        self.b_dict = defaultdict( lambda:0)
        self.both_dict = defaultdict( lambda:0)
        self.both_same = {True:0, False:0}
    def count( self, a_items, b_items):
        self.a_count += len( a_items)
        self.b_count += len( b_items)
        self.a_dict[ len( a_items) ] += 1
        self.b_dict[ len( b_items) ] += 1
        if len( a_items)!= 0 and len( b_items) != 0:
            self.both_dict[ len( a_items) - len( b_items) ] += 1
            self.both_same[ len( a_items) == len( b_items) ] += 1
    def get_counts( self):
        return self.a_count, self.b_count
    def print_counts( self, output_file):
        print( ">>> " + self.name, file=output_file)
        print( self.a_count, self.b_count, sep='\t', file=output_file)
        print( "A dict: ", dict( sorted( self.a_dict.items())), file=output_file)
        print( "B dict: ", dict( sorted( self.b_dict.items())), file=output_file)
        print( "Both: ", dict( sorted( self.both_dict.items())), file=output_file)
        print( "Both same: ", self.both_same, file=output_file)
        print( "------", file=output_file)


