import sys
import xml.etree.ElementTree as et

"""
searches through vallex xml and prints selected statistics
"""

#if len( sys.argv) < 2:
#    exit()

#filename = sys.argv[ 1 ]
filename = "../data/vallex_3.0.xml"
tree = et.ElementTree( file=filename)
root = tree.getroot()
entries = root.find( "body/entries")
lu_cluster_lens = set()
lem_num = 0
for lexeme_cluster in entries:
    for lexeme in lexeme_cluster:
        l_forms = lexeme.find( "lexical_forms")
        l_units = lexeme.findall( ".//blu")
        for l_form in l_forms:
            mlemmas = l_form.findall( ".//mlemma")
            lem_num += len( mlemmas)
            commonrefl = l_form.find( "commonrefl")
        for blu in l_units:
            for child in blu:
                lu_cluster_lens.add( child.tag)
            
print( lu_cluster_lens)
print( lem_num)


    #if len( lexeme_cluster) != 1:
    #    mlemmas = lexeme_cluster.findall( ".//mlemma")
    #    for mlemma in mlemmas:
    #        print( mlemma.text)
    #    print( "=====")

