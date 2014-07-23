#!/bin/sh -x

python prepare.py pig
python mymrf.py pig
python construct.py pig
scp tmp/pig_mrf_result liuzuotao@10.241.164.162:
