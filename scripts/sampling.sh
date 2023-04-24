#!/bin/bash

export PATH=../../udapi-python/bin:$PATH
export PYTHONPATH=../../udapi-python:../../udapi-python/udapi/block/valency:$PYTHONPATH

select_samples() {
  corp=$1
  for sample_id in 1 12 123
  do
    test_corp="$corp"_"$sample_id"
    python3 sampler.py $corp $test_corp $sample_id
  done
}

select_samples acquis_cs_en
select_samples acquis_cs_sk