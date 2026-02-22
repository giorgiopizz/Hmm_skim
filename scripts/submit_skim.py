#!/usr/bin/env python3
import subprocess
import ROOT
import os
from utils.utils import get_fw_path, common_args, get_results_folder
import gzip
import json
import sys


ROOT.gROOT.SetBatch(True)


def chunksize_per_dataset(year, dataset):
    if year == "2024":
        nevents_per_chunk = 100_000_000
        if "to2Mu" in dataset:
            nevents_per_chunk = 5_000_000
    else:
        nevents_per_chunk = 10_000_000
        if "to2Mu" in dataset:
            nevents_per_chunk = 5_000_000
    return nevents_per_chunk


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


if __name__ == "__main__":
    args = common_args()
    year = args.year
    tag = args.tag

    fw_path = get_fw_path()
    data_folder = f"{fw_path}/data/{year}/"

    results_folder = get_results_folder(tag, year)
    os.makedirs(results_folder, exist_ok=False)

    with gzip.open(f"{data_folder}/fileset.json.gz", "rb") as f:
        fileset_data = json.loads(f.read().decode("utf-8"))

    # get only enabled samples
    fw_path = get_fw_path()
    prod_folder = f"{fw_path}/productions/{year}/"
    sys.path.insert(0, prod_folder)
    from samples import Samples

    fileset_data_new = {}
    for sample in Samples:
        fileset_data_new[sample] = fileset_data[sample]
    fileset_data = fileset_data_new

    is_datas = {}
    datasets_files = {}

    i_random = 0
    for dataset in fileset_data:
        nevents_per_chunk = chunksize_per_dataset(year, dataset)
        datasets_files[dataset] = merge_files(
            fileset_data[dataset]["files"][:], nevents_per_chunk
        )[:]

        is_datas[dataset] = fileset_data[dataset].get("is_data", False)

    ijob = 0
    condor_folder = f"{fw_path}/condor_jobs/{tag}_{year}/"
    if os.path.exists(condor_folder):
        subprocess.run(f"rm -rf {condor_folder}", shell=True)

    os.makedirs(condor_folder, exist_ok=True)

    cmd = f"cp -r {fw_path}/data {condor_folder}/."
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        raise Exception("Failed to copy data folder")

    cmd = f"cp -r {fw_path}/modules {condor_folder}/."
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        raise Exception("Failed to copy modules folder")

    with open(f"{fw_path}/utils/condor_job/run.sh", "r") as f:
        run_sh_content = f.read()
    run_sh_content = run_sh_content.replace("RPLME_YEAR", year)
    with open(f"{condor_folder}/run.sh", "w") as f:
        f.write(run_sh_content)

    cmd = f"cp {fw_path}/runners/runner.py {condor_folder}/."
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        raise Exception("Failed to copy runner.py")

    cmd = f"cp {os.environ['X509_USER_PROXY']} {condor_folder}/my_cert"
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        raise Exception("Failed to copy proxy certificate")

    jobs_mapped = {}
    for ds in datasets_files:
        for ifile, file in enumerate(datasets_files[ds]):
            os.makedirs(f"{condor_folder}/job_{ijob}", exist_ok=True)
            outfile = f"{results_folder}/{ds}_skimmed_{ifile}.root"
            jobs_mapped[ijob] = {
                "dataset": ds,
                "ifile": ifile,
                "outfile": outfile,
                "is_data": is_datas[ds],
            }
            with open(f"{condor_folder}/job_{ijob}/input.json", "w") as f:
                json.dump(
                    {
                        "dataset": ds,
                        "file": file,
                        "outfile": outfile,
                        "is_data": is_datas[ds],
                    },
                    f,
                    indent=2,
                )

            ijob += 1
    print(f"Total jobs: {ijob}")

    with open(f"{condor_folder}/jobs_mapped.json", "w") as f:
        json.dump(jobs_mapped, f, indent=2)

    with open(f"{fw_path}/utils/condor_job/submit.jdl", "r") as f:
        submit_jdl_content = f.read()

    submit_jdl_content = submit_jdl_content.replace(
        "RPLME_JOBS", " ".join([f"job_{i}" for i in range(ijob)])
    )

    with open(f"{condor_folder}/submit.jdl", "w") as f:
        f.write(submit_jdl_content)
