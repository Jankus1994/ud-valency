from udapi.core.block import Block

class Pokus( Block):
    
    def process_node( self, node): # void
        """ overridden block method
        searching verbs and calling create_frame for them
        """
        if ( node.upos == "VERB" and node.lemma == "moci" and node.feats["VerbForm"] == "Part" and node.feats["Voice"]=="Act"):
            num_xcomp = 0
            num_csubj = 0
            deti = [ child for child in node.children if child.udeprel in [ "xcomp", "ccomp", "obj", "iobj", "csubj", "nsubj", "expl" ] or child.deprel in [ "obl:arg", "obl:agent" ] ]
            if len(deti) == 2:
                for child in deti:
                    if ( child.deprel == "xcomp" and child.feats["Case"]== "" ):
                        num_xcomp += 1
                    elif ( child.deprel == "csubj" and child.feats["Case"]== ""):
                        vnucata = [ vnuca for vnuca in child.children if vnuca.deprel == "mark" ]
                        if ( vnucata ):
                            break
                        num_csubj += 1
                if (num_xcomp == 2 or ( num_xcomp == 1 and num_csubj == 1 and not vnucata)):
                    print( "xcomp: " + str( num_xcomp) + "   csubj: " + str(num_csubj) + "   " + str( node.root))
