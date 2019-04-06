import sys
import xml.etree.ElementTree as et

class Parallextract:
    def __init__( self, corpus_name, output_name_1, output_name_2):
        self.tree = et.ElementTree( file = corpus_name)
        self.out_1 = open( output_name_1, 'w')
        self.out_2 = open( output_name_2, 'w')
    
    def extract( self):
        root = self.tree.getroot()
        links = root.findall( ".//link")
        for link in links:
            s1 = link.find( "s1")
            text_1 = self.extract_sentence( s1)
            self.out_1.write( text_1 + '\n')
            
            s2 = link.find( "s2")
            text_2 = self.extract_sentence( s2)
            self.out_2.write( text_2 + '\n')
                
    def extract_sentence( self, s):
        ps = s.findall( "p")
        if ( not ps ):
            text = s.text
        else:
            texts = [ p.text for p in ps ]
            text = ' '.join( texts)
        return text
        
if ( len( sys.argv) == 4 ):
    p = Parallextract( sys.argv[ 1 ], sys.argv[ 2 ], sys.argv[ 3 ])
    p.extract()
