#!/usr/bin/env python3
import glob
from utils.utils import common_args

if __name__ == "__main__":
    args = common_args()
    condor_folder = f"condor_jobs/{args.tag}_{args.year}"
    tot = glob.glob(f"{condor_folder}/job_*/input.json")
    err = glob.glob(f"{condor_folder}/job_*/err.txt")
    missing = set(list(map(lambda x: x.split("/")[1].split("_")[1], tot))) - set(
        list(map(lambda x: x.split("/")[1].split("_")[1], err))
    )
    print("Missing jobs:", missing)
