#!/usr/bin/env python3
import ROOT
import os
import argparse
from utils.utils import get_fw_path

import json


ROOT.gROOT.SetBatch(True)

base_output_folder = get_fw_path() + "/rootfiles/"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year", type=str, default="2024", help="Year of the production"
    )
    args = parser.parse_args()
    year = args.year

    fw_path = get_fw_path()
    prod_folder = f"{fw_path}/productions/{year}/"

    results_folder = f"{base_output_folder}/{year}/"
    os.makedirs(results_folder, exist_ok=True)

    with open(f"{prod_folder}/fileset.json", "r") as f:
        fileset_data = json.load(f)
    is_datas = {}
    datasets_files = {}

    def merge_files(files, nevents_per_chunk=10_000_000):
        merged_files = []
        cur_files = []
        cur_nevents = 0
        i_random = 0
        for f in files:
            if cur_nevents >= nevents_per_chunk:
                merged_files.append(cur_files)
                cur_files = []
                cur_nevents = 0
            # random.Random(i_random).shuffle(fileinfo["path"])
            i_random += 1
            fpath = f["path"][0]
            cur_files.append(fpath)
            cur_nevents += f["nevents"]
        if len(cur_files) > 0:
            merged_files.append(cur_files)
        return merged_files

    i_random = 0
    for dataset in fileset_data:
        # if dataset != "DY2Mu":
        #     continue
        # if "Muon0" not in dataset:
        #     continue

        # files = []
        # for fileinfo in fileset_data[dataset]["files"][:100]:
        #     # random.Random(i_random).shuffle(fileinfo["path"])
        #     files += [fileinfo["path"][0]]
        #     i_random += 1
        nevents_per_chunk = 100_000_000
        if "to2Mu" in dataset:
            nevents_per_chunk = 5_000_000
        datasets_files[dataset] = merge_files(
            fileset_data[dataset]["files"][:], nevents_per_chunk
        )[:]

        if "Muon0" in dataset or "Muon1" in dataset:
            is_datas[dataset] = True
        else:
            is_datas[dataset] = False

    ijob = 0
    condor_folder = f"{fw_path}/condor_jobs/"
    os.makedirs(condor_folder, exist_ok=True)

    jobs_mapped = {}
    for ds in datasets_files:
        for ifile, file in enumerate(datasets_files[ds]):
            os.makedirs(f"{condor_folder}/job_{ijob}", exist_ok=True)
            jobs_mapped[ijob] = {
                "dataset": ds,
                "ifile": ifile,
                "outfile": f"{results_folder}/{ds}_skimmed_{ifile}.root",
                "is_data": is_datas[ds],
            }
            with open(f"{condor_folder}/job_{ijob}/input.json", "w") as f:
                json.dump(
                    {
                        "dataset": ds,
                        "file": file,
                        "outfile": f"{results_folder}/{ds}_skimmed_{ifile}.root",
                        "is_data": is_datas[ds],
                    },
                    f,
                    indent=2,
                )

            ijob += 1
    print(f"Total jobs: {ijob}")
    with open(f"{condor_folder}/jobs_mapped.json", "w") as f:
        json.dump(jobs_mapped, f, indent=2)
    exit(1)
