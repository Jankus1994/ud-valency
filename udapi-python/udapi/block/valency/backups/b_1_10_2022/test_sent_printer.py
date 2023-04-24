from random import sample

from udapi.core.block import Block

class Test_sent_printer( Block):
    def __init__( self, out_file_name, **kwargs):
        """ overriden block method """
        super().__init__( **kwargs)
        self.out_file = open( out_file_name, 'w')

    def process_bundle( self, bundle):
        bundle_id = bundle.bundle_id
        a_verbs, a_sent_text = self.process_tree( bundle.trees[ 0 ])
        b_verbs, b_sent_text = self.process_tree( bundle.trees[ 1 ])
        output_string = '\t'.join( [ bundle_id, a_verbs, b_verbs, a_sent_text, b_sent_text])
        print( output_string, file=self.out_file)

    def process_tree( self, tree_root):
          verbs = ','.join( [ node.lemma for node in tree_root.descendants
                              if node.upos == "VERB" ])
          sent_text = tree_root.get_sentence()
          return verbs, sent_text

    def process_end( self):
        self.out_file.close()
