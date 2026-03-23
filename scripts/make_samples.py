#!/usr/bin/env python
import sys
from utils.utils import get_fw_path, common_args, print_p
import subprocess


def query_dataset(query):
    cmd = 'dasgoclient --query="dataset={}" --json'.format(query)
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        print("Error querying DAS:", stderr.decode())
        return []
    import json

    res = json.loads(stdout.decode())

    if len(res) == 0 or len(res[0]["dataset"]) == 0:
        print_p(f"No dataset found for query {query}", type="error")
        exit(1)
    datasets = []
    for result in res:
        assert len(result["dataset"]) == 1
        dataset = result["dataset"][0]["name"]
        datasets.append(dataset)
    datasets = list(
        filter(lambda k: "ext" not in k, datasets)
    )  # filter out extension datasets
    datasets = sorted(datasets)
    return datasets[0]


if __name__ == "__main__":
    args = common_args(
        [
            dict(
                name="-j",
                type=int,
                default=2,
                help="Number of parallel jobs to run for querying the fileset",
            )
        ]
    )
    year = args.year
    max_cores = args.j

    fw_path = get_fw_path()
    prod_folder = f"{fw_path}/productions/{year}/"
    sys.path.insert(0, prod_folder)
    from pre_samples import Samples

    data_folder = f"{fw_path}/data/{year}/"

    for sample in Samples:
        if "pattern" in Samples[sample]:
            dataset = query_dataset(Samples[sample]["pattern"])

            # datasets = rucio_utils.query_dataset(Samples[sample]["pattern"])
            # datasets = list(
            #     filter(lambda k: "ext" not in k, datasets)
            # )  # filter out extension datasets
            # datasets = sorted(datasets)
            # if len(datasets) == 0:
            #     print(f"No datasets found for pattern {Samples[sample]['pattern']}")
            #     continue
            Samples[sample]["nanoAOD"] = dataset
        # print("new nanoAOD pattern for sample", sample, ":", Samples[sample]["nanoAOD"])

    with open(
        f"/home/gpizzati/code/hmm/flaf/FLAF/config/Run3_{year}/datasets.yaml"
    ) as f:
        flaf_datasets = f.read()
    with open(
        f"/home/gpizzati/code/hmm/flaf/H_mumu/config/Run3_{year}/datasets.yaml"
    ) as f:
        flaf_datasets_sig = f.read()
    for sample in Samples:
        if (
            Samples[sample]["nanoAOD"] not in flaf_datasets
            and Samples[sample]["nanoAOD"] not in flaf_datasets_sig
        ):
            print(
                f"Warning: sample {sample} with nanoAOD {Samples[sample]['nanoAOD']} not found in FLAF datasets"
            )
    with open(f"{fw_path}/productions/{year}/samples.py", "w") as f:
        f.write("Samples = {}\n")

        for sample in Samples:
            f.write(f'Samples["{sample}"] = {{\n')
            for key in Samples[sample]:
                if key in ["pattern"]:
                    continue
                if isinstance(Samples[sample][key], str):
                    f.write(f'        "{key}": "{Samples[sample][key]}",\n')
                else:
                    f.write(f'        "{key}": {Samples[sample][key]},\n')

            f.write("}\n\n")
        f.write("\n")
