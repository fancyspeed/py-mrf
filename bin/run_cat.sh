#!/bin/sh -x

python prepare.py
python mymrf.py
python construct.py
python MAP.py tmp/cat_mrf_result data/cat_truth

