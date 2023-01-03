export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
scripts for examining oblique dependents
'

data=../../data
corp_name=UD_pud.EN

udapy \
    read.Conllu \
        files="$data"/m_conllu/"$corp_name".conllu \
    valency.Obl_examiner \

# OBECNE OBLIQOVE STATISTIKY
# statistiky, kolko je obliqov
# vyskyty obliqov voci ostatnym deprelom, priemer na sloveso atd.
# podoba obliqov, ake maju padu a predlozky, ich cetnost

# POKRACUJ TU: NAPIS UDAPI BLOCH SKUMAJUCI TIETO TRI VECI, ALE NEPRACUJUCI
# S EXTRACTOROM
# - NECH SKUMA, CO MA
# - NECH TO VYPISE PREHLADNE
# - NECH SA LAHKO A OPAKOVATELNE SPUSTA
# - PRESKUMAJ MOZNOSTI VYPISU PRIAMO DO PODOBY LATEXOVEJ TABULKY