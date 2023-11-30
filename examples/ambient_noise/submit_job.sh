nohup python s0_download.py > s0_download.log  2>&1  &
nohup mpirun -n 9 python s1_build_db.py > s1_build_db.log  2>&1  &
nohup python s2_trim.py > s2_trim.log  2>&1  &
nohup python s3_corr.py > s3_corr.log  2>&1  &
nohup python s4_dvv.py > s4_dvv.log  2>&1  &