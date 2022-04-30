import xml.etree.ElementTree as et
tree = et.ElementTree( file="../data/vallex_3.0.xml")
root = tree.getroot()
items = root.findall( ".//slot")
attribs = set()
for item in items:
    attrib_name = "type"
    if attrib_name in item.attrib:
        attribs.add( item.attrib[ attrib_name ])
    else:
        attribs.add( None)
print( attribs)
