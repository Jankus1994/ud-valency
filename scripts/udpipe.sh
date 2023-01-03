 #!/bin/bash

export PATH=../../fast_align/build:$PATH
export PATH=../../udpipe/bin-linux64:$PATH


name=$1
#for i in `seq 2 5`;
#do
#cat ../data/cs/cs.tok."$name" | udpipe --input=horizontal --tag --parse --output=conllu ../../udpipe/models/czech-pdt-ud-2.3-181115.udpipe > ../data/cs/cs_"$name".conllu
cat ../data/en/en.tok."$name" | udpipe --input=horizontal --tag --parse --output=conllu ../../udpipe/models/english-lines-ud-2.3-181115.udpipe > ../data/en/en_"$name".conllu
#done

