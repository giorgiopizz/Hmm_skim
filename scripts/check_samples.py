#!/usr/bin/env python3
from utils.utils import parse_samples_datasets
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year", type=str, required=True, help="Year of the production"
    )
    args = parser.parse_args()
    year = args.year

    datasets, samples = parse_samples_datasets(year)

    print("Active samples")
    for dataset in datasets:
        print(f"Dataset {dataset}:")
        for sample in datasets[dataset]["names"]:
            print(f"\t{sample}")
