#!/usr/bin/env python3
import subprocess
import json
from utils.utils import get_fw_path
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year", type=str, required=True, help="Year of the production"
    )
    args = parser.parse_args()
    year = args.year

    fw_path = get_fw_path()

    prod_folder = f"{fw_path}/productions/{year}/"
    sys.path.insert(0, prod_folder)
    from samples import Samples

    files = {}
    for key in Samples:
        dataset = Samples[key]["nanoAOD"]
        cmd = f'dasgoclient --query="file dataset={dataset}" --limit=1 --format=json'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        dataset_info = json.loads(result.stdout)
        print(dataset)
        file = dataset_info["data"][0]["file"][0]["name"]

        files[key] = file
