export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python/:$PYTHONPATH

: '
scripts for examining oblique dependents
'

data=../../data

run_examiner () {
  corp_name=$1
  udapy \
      read.Conllu \
          files="$data"/m_conllu/"$corp_name".conllu \
      valency.Obl_examiner
}

run_examiner UD_pud.EN
run_examiner UD_pud.CS
run_examiner UD_pud.ES