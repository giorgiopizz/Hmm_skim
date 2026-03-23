import os

import argcomplete
import sys


def get_fw_path():
    return os.environ["FW_PATH"]


base_output_folder = get_fw_path() + "/rootfiles/"
base_output_folder = "/eos/user/g/gpizzati/hmm_skim/"

base_condor_folder = get_fw_path() + "/condor_jobs/"
base_condor_folder = "/afs/cern.ch/user/g/gpizzati/Hmm_skim/condor_jobs/"


def get_results_folder(tag, year):
    return f"{base_output_folder}/{tag}/{year}/"


def common_args(additional_args: list[dict] = [], register_argcomplete: bool = True):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year", type=str, required=True, help="Year of the production"
    )
    parser.add_argument("--tag", type=str, required=True, help="Tag of the production")
    for arg in additional_args:
        arg_name = arg.pop("name")
        parser.add_argument(arg_name, **arg)
    if register_argcomplete:
        argcomplete.autocomplete(parser)
    args = parser.parse_args()
    print(f"Running with year={args.year} and tag={args.tag}")
    return args


def print_p(text, *args, type="info"):
    if type == "info":
        print(f"\033[94mInfo: {text}\033[0m", *args)
    elif type == "warning":
        print(f"\033[93mWarning: {text}\033[0m", *args, file=sys.stderr)
    elif type == "error":
        print(f"\033[91mError: {text}\033[0m", *args, file=sys.stderr)
    else:
        print(text)


def parse_samples_datasets(year):
    sys.path.insert(0, f"{get_fw_path()}/productions/{year}/")
    from datasets import datasets
    from samples import Samples

    active_samples = set()
    for ds in datasets:
        for ds_single in datasets[ds]["names"]:
            if ds_single not in Samples:
                print_p(f"Dataset {ds_single} not found in samples.py", type="error")
                raise Exception(f"Dataset {ds_single} not found in samples.py")
            active_samples.add(ds_single)
    # check inactive samples
    all_samples = list(Samples.keys())
    for sample in all_samples:
        if sample not in active_samples:
            print_p(
                f"Sample {sample} is not active in any dataset, deactivating",
                type="warning",
            )
            del Samples[sample]
    return datasets, Samples


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
    elif isinstance(d1, bool):
        return d1 and d2
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


def add_dict_iterable(iterable) -> dict:
    tmp = -99999
    for it in iterable:
        if tmp == -99999:
            tmp = it
        else:
            tmp = add_dict(tmp, it)
    return tmp


cmap_petroff = [
    "#5790fc",
    "#f89c20",
    "#e42536",
    "#964a8b",
    "#9c9ca1",
    "#7a21dd",
]

cmap_pastel = [
    "#A1C9F4",
    "#FFB482",
    "#8DE5A1",
    "#FF9F9B",
    "#D0BBFF",
    "#DEBB9B",
    "#FAB0E4",
    "#CFCFCF",
    "#FFFEA3",
    "#B9F2F0",
]
