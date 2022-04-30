import pickle

from udapi.core.block import Block

class Pokus( Block):

    def process_bundle( self, bundle): # void
        print( len( bundle.trees))
    #def process_node( self, node):
    #    print( node.lemma)
        #pass
    #def process_document( self, doc):
    #    print( len( doc.bundles))
