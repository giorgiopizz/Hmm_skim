#!/usr/bin/env python3
import glob
from utils.utils import common_args, base_condor_folder

if __name__ == "__main__":
    args = common_args()
    condor_folder = f"{base_condor_folder}/{args.tag}_{args.year}"
    tot = glob.glob(f"{condor_folder}/job_*/input.json")
    err = glob.glob(f"{condor_folder}/job_*/err.txt")
    missing = set(list(map(lambda x: x.split("/")[-2], tot))) - set(
        list(map(lambda x: x.split("/")[-2], err))
    )
    print("Total jobs", len(tot))
    print(f"Missing {len(missing)} jobs:", missing)

    good_errors = [
        "Warning in <TClass::Init>: no dictionary for class edm::Hash<1> is available",
        "Warning in <TClass::Init>: no dictionary for class edm::ProcessHistory is available",
        "Warning in <TClass::Init>: no dictionary for class edm::ProcessConfiguration is available",
        "Warning in <TClass::Init>: no dictionary for class edm::ParameterSetBlob is available",
        "Warning in <TClass::Init>: no dictionary for class pair<edm::Hash<1>,edm::ParameterSetBlob> is available",
    ]

    def good_error(line):
        if any([err in line for err in good_errors]):
            return True
        if line.startswith("Warning"):
            return True
        if line.startswith("Info"):
            return True
        return False

    to_resubmit = []
    for job in err:
        with open(job, "r") as f:
            content = f.read().split("\n")
            for line in content:
                if line.strip() == "":
                    continue
                if good_error(line):
                    continue
                print(f"Error in {job}: {line}")
                to_resubmit.append(job.split("/")[-2])
                break
    print(f"Failed {len(to_resubmit)} jobs")

    if len(to_resubmit) > 0:
        cmd = "queue 1 Folder in " + " ".join(to_resubmit)
        print(f"\n{cmd}\n")
