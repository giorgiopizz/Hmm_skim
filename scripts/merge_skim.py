#!/usr/bin/env python3
import json
import argparse
import sys
import os

from scripts.submit_skim import base_output_folder


def add_dict(d1, d2):
    if isinstance(d1, dict):
        d = {}
        common_keys = set(list(d1.keys())).intersection(list(d2.keys()))
        for key in common_keys:
            d[key] = add_dict(d1[key], d2[key])
        for key in d1:
            if key in common_keys:
                continue
            d[key] = d1[key]
        for key in d2:
            if key in common_keys:
                continue
            d[key] = d2[key]

        return d
    elif isinstance(d1, set):
        return d1.union(d2)
    else:
        try:
            tmp = d1 + d2
        except Exception as e:
            print("Error adding")
            print(d1)
            print(d2)
            raise Exception("Error adding", d1, d2, e)
            tmp = d1
        return tmp


def add_dict_iterable(iterable):
    tmp = -99999
    for it in iterable:
        if tmp == -99999:
            tmp = it
        else:
            tmp = add_dict(tmp, it)
    return tmp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year", type=str, default="2024", help="Year of the production"
    )
    args = parser.parse_args()
    year = args.year

    with open("condor_jobs/jobs_mapped.json") as f:
        jobs_mapped = json.load(f)

    # open each output.json from the jobs
    jobs_results = []
    for ijob in jobs_mapped:
        job_folder = f"condor_jobs/job_{ijob}"
        if not os.path.exists(f"{job_folder}/output.json"):
            # print in yellow color
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

    for ds in jobs_results:
        jobs_results[ds]["is_data"] = "Muon0" in ds or "Muon1" in ds

    sys.path.insert(0, "productions/")
    from xs import xs

    lumis = {
        "2024": 109.98799,
        "2023": 18.0630,
    }

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
    with open(f"{base_output_folder}/{year}/results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    print(json.dumps(final_results, indent=2))
