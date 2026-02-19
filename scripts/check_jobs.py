#!/usr/bin/env python3
import glob

tot = glob.glob("condor_jobs/job_*/input.json")
err = glob.glob("condor_jobs/job_*/err.txt")
missing = set(list(map(lambda x: x.split("/")[1].split("_")[1], tot))) - set(list(map(lambda x: x.split("/")[1].split("_")[1], err)))
print("Missing jobs:", missing)
