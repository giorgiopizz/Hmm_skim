#!/usr/bin/env python3
import json
import argparse
import sys
import os

from utils.utils import common_args, add_dict_iterable, get_fw_path, get_results_folder


if __name__ == "__main__":
    args = common_args()
    year = args.year
    tag = args.tag

    fw_path = get_fw_path()

    condor_folder = f"{fw_path}/condor_jobs/{tag}_{year}"
    with open(f"{condor_folder}/jobs_mapped.json") as f:
        jobs_mapped = json.load(f)

    # open each output.json from the jobs
    jobs_results = []
    for ijob in jobs_mapped:
        job_folder = f"{condor_folder}/job_{ijob}"
        if not os.path.exists(f"{job_folder}/output.json"):
            with open(f"{job_folder}/input.json") as f:
                input_data = json.load(f)
            if input_data["is_data"]:
                # for data raise error
                print(
                    f"\033[91mError: output.json not found in job {ijob} for dataset {input_data['dataset']}\033[0m"
                )
                exit(1)
            else:
                # for mc missing it's ok
                print(f"\033[93mWarning: output.json not found in job {ijob}\033[0m")
                continue

        with open(f"{job_folder}/output.json") as f:
            if f.read() == "":
                print(f"Error: empty output.json in job {ijob}")
                exit(1)
            f.seek(0)
            jobs_results.append(json.load(f))

    jobs_results = add_dict_iterable(jobs_results)
    print(jobs_results)

    sys.path.insert(0, f"{fw_path}/productions")
    from xs import xs
    from lumis import lumis

    lumi = lumis[year]
    final_results = {}
    for dataset in jobs_results:
        final_results[dataset] = {
            "nevents_before": jobs_results[dataset]["nevents_before"],
            "nevents_after": jobs_results[dataset]["nevents_after"],
        }
        if jobs_results[dataset]["is_data"]:
            continue
        rescale = xs[dataset] * 1000 * lumi / jobs_results[dataset]["sumw"]
        final_results[dataset]["rescale"] = rescale
        final_results[dataset]["sumw"] = jobs_results[dataset]["sumw"]
    with open(f"{get_results_folder(tag, year)}/results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    print(json.dumps(final_results, indent=2))
