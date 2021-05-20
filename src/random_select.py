# Randomly select TP and FP cases for evaluation
import numpy as np
import random
import os
import tifffile

DATADIR = "/Users/hoanguyen/DATA/DeepCoronaScan/OUTPUTS/GradCAM/scan3d/exp21/model-0001-0.4784-0.8079.hdf5"
OUTDIR = "/Users/hoanguyen/DATA/DeepCoronaScan/OUTPUTS/GradCAM/Evaluation"

os.makedirs(OUTDIR, exist_ok=True)

if __name__ == "__main__":
    folders_TP = [x for x in os.listdir("{}/TP".format(DATADIR)) if ("POISSY" in x) and (not x.startswith("."))]
    folders_FP = [x for x in os.listdir("{}/FP".format(DATADIR)) if ("POISSY" in x) and (not x.startswith("."))]
    
    print("POISSY TP: ", len(folders_TP))
    print("POISSY FP: ", len(folders_FP))
    
    eval_folders_TP = random.sample(folders_TP, 70)
    eval_folders_FP = random.sample(folders_FP, 30)
    
    for sample in eval_folders_TP + eval_folders_FP:
        print(sample)
        if sample in eval_folders_TP:
            folder = os.path.join(DATADIR, "TP", sample)
        else:
            folder = os.path.join(DATADIR, "FP", sample)
        
        im = tifffile.imread(os.path.join(folder, "image.tif"))
        cam = tifffile.imread(os.path.join(folder, "cam.tif"))
        merge = np.concatenate([np.expand_dims(im, axis=3), cam],axis=3)
        
        os.makedirs(os.path.join(OUTDIR, sample), exist_ok=True)
        tifffile.imwrite(os.path.join(OUTDIR, sample, "cam.tif"), merge)
        
        