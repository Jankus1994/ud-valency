from udapi.core.block import Block

class Sample_printer( Block):
    def __init__( self, output_name, **kwargs):
        super().__init__( **kwargs)
        self.output = open( output_name, 'w')
        self.counter = 0

    def process_tree( self, root):
        self.counter += 1
        if self.counter % 10 == 0:
            sent = ' '.join( [ node.form  for node in root.descendants ])
            print( sent, file=self.output)

    #def after_process_document( self, _):

