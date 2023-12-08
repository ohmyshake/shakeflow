nohup python s0_download.py > s0_download.log  2>&1  &
nohup python s1_build_db.py > s1_build_db.log  2>&1  &
nohup python s2_cc_stack.py > s2_cc_stack.log  2>&1  &
nohup python s3_dvv.py > s3_dvv.log  2>&1  &