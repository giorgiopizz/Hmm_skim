#!/usr/bin/env python3
from dbs.apis.dbsClient import DbsApi
from utils import rucio_utils
import concurrent.futures
import json
from utils.utils import get_fw_path, common_args
import sys
import gzip


def fileset(files, max_cores=2):
    url = "https://cmsweb.cern.ch/dbs/prod/global/DBSReader"
    dbs_api = DbsApi(url=url)

    rucio_client = rucio_utils.get_rucio_client()
    xrootd_sites_map = rucio_utils.get_xrootd_sites_map()
    # good_sites = ["IT", "FR", "BE", "CH", "UK", "ES", "DE", "US"]
    good_sites = ["IT", "FR", "BE", "CH", "UK", "ES", "DE"]
    default_kwargs = dict(
        allowlist_sites=[],
        blocklist_sites=[
            # "T2_FR_IPHC",
            # "T2_ES_IFCA",
            # "T2_CH_CERN",
            "T3_IT_Trieste",
        ],
        # regex_sites=[],
        regex_sites=r"T[123]_(" + "|".join(good_sites) + r")_\w+",
        # regex_sites = r"T[123]_(DE|IT|BE|CH|ES|UK|US)_\w+",
        mode="full",  # full or first. "full"==all the available replicas
        client=rucio_client,
        xrootd_sites_map=xrootd_sites_map,
    )
    _files = {k: v for k, v in files.items() if "query" in v}
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_cores) as pool:
        tasks = []
        for dname in _files:
            dataset = _files[dname]["query"]
            tasks.append(
                pool.submit(
                    rucio_utils.get_dataset_files_replicas, dataset, **default_kwargs
                )
            )
        concurrent.futures.wait(tasks)

        for dname, task in zip(_files, tasks):
            dataset_query = _files[dname]["query"]
            outfiles, outsites, _ = task.result()

            filelist = dbs_api.listFiles(dataset=dataset_query, detail=1)
            event_count_map = {
                k["logical_file_name"]: k["event_count"] for k in filelist
            }
            # print(event_count_map)

            result = []
            for replicas, _ in zip(outfiles, outsites):
                prefix = "/store/data"
                if prefix not in replicas[0]:
                    prefix = "/store/mc"
                logical_name = prefix + replicas[0].split(prefix)[-1]
                try:
                    nevents = event_count_map[logical_name]
                except KeyError:
                    continue

                result.append({"path": replicas, "nevents": nevents})
            files[dname]["files"] = result
    return files


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
    from samples import Samples

    data_folder = f"{fw_path}/data/{year}/"

    files = {}

    for sample in Samples:
        files[sample] = {
            "files": [],
        }
        files[sample]["is_data"] = Samples[sample].get("is_data", False)
        for key in Samples[sample]:
            if key == "nanoAOD":
                files[sample]["query"] = Samples[sample][key]

    print("Generating fileset for production folder:", prod_folder)
    print(f"Using {max_cores} cores, this may take a up to 10 minutes")
    files = fileset(files)
    for key in files:
        if len(files[key]["files"]) == 0:
            print(f"Warning: no files found for sample {key}")

    with gzip.open(f"{data_folder}/fileset.json.gz", "wb") as f:
        f.write(json.dumps(files, indent=2).encode("utf-8"))
