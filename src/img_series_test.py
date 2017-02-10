import pypeline as pype
from pypeline import pipeline_img_series

import sys
import os


import time

os.chdir(r'\\skynet\PechinTest2\emphysema_pipeline_test_20170124\library\recon\100\5a1eebd46534e0e22036254ddd54c4db_k1_st2.0\img')
test=pipeline_img_series('5a1eebd46534e0e22036254ddd54c4db_d100_k1_st2.0.img',
                         '5a1eebd46534e0e22036254ddd54c4db_d100_k1_st2.0.prm')

test.to_memory()
