"""
tool for extracting parallel sentences from acquis corpora in xml format
writes sentences in two separate files
the sentences will be later parsed
the correspondence between the sentences is kept by line number

run from parallextract.sh

if other corpora are included, the extractor will be generalized
with corpus-specific child classes
"""

import sys
import xml.etree.ElementTree as et


class Parall_extractor_acquis:
    def __init__( self, corpus_file_name, out_file_1, out_file_2):
        self.tree = et.ElementTree( file = corpus_file_name)
        self.out_file_1 = out_file_1
        self.out_file_2 = out_file_2
    
    def extract( self):
        root = self.tree.getroot()
        links = root.findall( ".//link")
        for link in links:
            s1_elem = link.find( "s1")
            text_1 = self.extract_sentence( s1_elem)
            self.out_file_1.write( text_1 + '\n')
            
            s2_elem = link.find( "s2")
            text_2 = self.extract_sentence( s2_elem)
            self.out_file_2.write( text_2 + '\n')
                
    def extract_sentence( self, s_elem):
        p_elems = s_elem.findall( "p")
        if ( not p_elems ):
            text = s_elem.text
        else:
            texts = [ p_elem.text for p_elem in p_elems ]
            text = ' '.join( texts)
        return text
        
if ( len( sys.argv) == 4 ):
    corpus_file_name = sys.argv[ 1 ]
    out_file_name_1 = sys.argv[ 2 ]
    out_file_name_2 = sys.argv[ 3 ]
    with open( out_file_name_1, 'w') as out_file_1, open( out_file_name_2, 'w') as out_file_2:
        parall_extractor_acquis = \
                Parall_extractor_acquis( corpus_file_name, out_file_1, out_file_2)
        parall_extractor_acquis.extract()
