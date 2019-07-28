# Data engineering in Dotscience
# ==============================
#
# In this script, we take a raw dataset from S3, and split it into two modelling sets:
# a small and large, each containing training, test and validation sets. 

"""

### Plan for splitting data

51,839 samples, let's construct two datasets for training models...

* small
  * 10k train
  * 1k test
  * 500 validate
* large
  * 50k train
  * 1k test
  * 839 validate

"""

import dotscience as ds
import numpy as np
import pickle
import os
from shutil import copyfile

ds.start()

roadsigns = pickle.load(open(ds.input("../s3/roadsigns.p"),"rb"))

if not os.path.exists("../data"):
    os.mkdir("../data")
    
# Shuffle the data otherwise the small training set is
# almost all one type of roadsign and gets crap accuracy

SEED = 42

for k in roadsigns.keys():
    # Very important that we set the seed every time
    # so that each shuffle of the keys is the same
    np.random.seed(SEED)
    np.random.shuffle(roadsigns[k])

# Sample ranges of the data

samples = [{"small-train": 10000, "small-test": 1000, "small-validate": 500},
           {"large-train": 50000, "large-test": 1000, "large-validate": 839}]

for sampleset in samples:
    i = 0
    for k in sorted(sampleset.keys()):
        count = sampleset[k]
        range_start = i
        range_end = i+count
        i += count
        print ("sample", k, "start", range_start, "end", range_end)
        result = {x: roadsigns[x][range_start:range_end] for x in roadsigns.keys()}
        pickle.dump(result, open(ds.output("../data/%s.p" % (k,)), "wb"))
        
# just make a copy of the labels so we keep them together with the data
copyfile(ds.input("../s3/signnames.csv"), ds.output("../data/signnames.csv"))

ds.publish("created small and large sample sets")