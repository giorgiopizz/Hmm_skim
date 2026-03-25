#!/usr/bin/env python3
import glob
from utils.utils import common_args, base_condor_folder, parse_samples_datasets
from tabulate import tabulate
import json

if __name__ == "__main__":
    args = common_args()
    condor_folder = f"{base_condor_folder}/{args.tag}_{args.year}"
    tot = glob.glob(f"{condor_folder}/job_*/input.json")
    err = glob.glob(f"{condor_folder}/job_*/err.txt")
    missing = set(list(map(lambda x: x.split("/")[-2], tot))) - set(
        list(map(lambda x: x.split("/")[-2], err))
    )
    # print("Total jobs", len(tot))
    # print(f"Missing {len(missing)} jobs:", missing)

    good_errors = [
        "Warning in <TClass::Init>: no dictionary for class edm::Hash<1> is available",
        "Warning in <TClass::Init>: no dictionary for class edm::ProcessHistory is available",
        "Warning in <TClass::Init>: no dictionary for class edm::ProcessConfiguration is available",
        "Warning in <TClass::Init>: no dictionary for class edm::ParameterSetBlob is available",
        "Warning in <TClass::Init>: no dictionary for class pair<edm::Hash<1>,edm::ParameterSetBlob> is available",
        # FIXME, don't know why these error happen, but output usually looks good
        "RDataFrame::Run: event loop was interrupted",
        "Error R__unzip_header: error in header.",
        "R__unzipLZMA: error",
    ]

    def good_error(line):
        if any([err in line for err in good_errors]):
            return True
        # if line.startswith("Warning: Error"):
        #     return True
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
        try:
            with open(job.replace("err.txt", "output.json"), "r") as f:
                txt = f.read()
                if txt == "":
                    # empty output.json is also a failure
                    to_resubmit.append(job.split("/")[-2])
                    continue
                content = json.loads(txt)
        except Exception as e:
            print(f"Error reading output.json for {job}: {e}")
            to_resubmit.append(job.split("/")[-2])
    # print(f"Failed {len(to_resubmit)} jobs")
    to_resubmit = list(set(to_resubmit))

    if len(to_resubmit) > 0:
        cmd = "queue 1 Folder in " + " ".join(to_resubmit)
        print(f"\n{cmd}\n")

    import json
    from collections import defaultdict

    datasets, samples = parse_samples_datasets(args.year)

    # --- Report per dataset ---
    jobs_mapped_path = f"{condor_folder}/jobs_mapped.json"
    with open(jobs_mapped_path, "r") as f:
        jobs_mapped = json.load(f)

    failed_folders = set(to_resubmit)
    missing_folders = set(missing)

    report = defaultdict(
        lambda: {"dataset": "", "total": 0, "failed": [], "missing": []}
    )
    report_dataset = defaultdict(lambda: {"total": 0, "failed": [], "missing": []})

    for job_id, info in jobs_mapped.items():
        sample = info["dataset"]

        correct_ds_name = ""
        for ds_name in datasets:
            if sample in datasets[ds_name]["names"]:
                correct_ds_name = ds_name
                break
        if correct_ds_name == "":
            print(f"Warning: dataset {info['dataset']} not found in any dataset group")
            correct_ds_name = info["dataset"]
        ds_name = correct_ds_name
        report[sample]["dataset"] = ds_name

        report[sample]["total"] += 1
        report_dataset[ds_name]["total"] += 1

        job_folder = f"job_{job_id}"
        if job_folder in failed_folders:
            report[sample]["failed"].append(job_id)
            report_dataset[ds_name]["failed"].append(job_id)
        elif job_folder in missing_folders:
            report[sample]["missing"].append(job_id)
            report_dataset[ds_name]["missing"].append(job_id)

    # Build table
    table = []
    for sample in sorted(report.keys(), key=lambda x: report[x]["dataset"]):
        r = report[sample]
        n_failed = len(r["failed"])
        n_missing = len(r["missing"])
        pct = 100.0 * (r["total"] - n_missing) / r["total"] if r["total"] > 0 else 0
        failed_str = ", ".join(sorted(r["failed"], key=int)) if r["failed"] else "-"
        if len(failed_str) > 50:
            failed_str = failed_str[:50] + "..."
        missing_str = ", ".join(sorted(r["missing"], key=int)) if r["missing"] else "-"
        if len(missing_str) > 50:
            missing_str = missing_str[:50] + "..."
        # make dataset name bold
        dataset_name = f"\033[1m{r['dataset']}\033[0m"
        # print in green if pct is 100, red if pct is less than 50, yellow otherwise
        table.append(
            [
                dataset_name,
                sample,
                r["total"],
                f"{pct:.1f}%",
                f"{n_failed} ({failed_str})",
                f"{n_missing} ({missing_str})",
            ]
        )
        if pct == 100:
            for i in range(len(table[-1])):
                table[-1][i] = f"\033[92m{table[-1][i]}\033[0m"
        elif pct < 50:
            for i in range(len(table[-1])):
                table[-1][i] = f"\033[91m{table[-1][i]}\033[0m"
        else:
            for i in range(len(table[-1])):
                table[-1][i] = f"\033[93m{table[-1][i]}\033[0m"

    headers = [
        "Dataset",
        "Sample",
        "Total",
        "Completed",
        "Failed (job IDs)",
        "Missing (job IDs)",
    ]
    print(
        "\n"
        + tabulate(
            table, headers=headers, tablefmt="grid", stralign="left", numalign="left"
        )
    )

    # Build table
    table = []
    for ds in sorted(
        report_dataset.keys(), key=lambda x: report_dataset[x]["total"], reverse=True
    ):
        r = report_dataset[ds]
        n_failed = len(r["failed"])
        n_missing = len(r["missing"])
        pct = 100.0 * (r["total"] - n_missing) / r["total"] if r["total"] > 0 else 0
        failed_str = ", ".join(sorted(r["failed"], key=int)) if r["failed"] else "-"
        if len(failed_str) > 50:
            failed_str = failed_str[:50] + "..."
        missing_str = ", ".join(sorted(r["missing"], key=int)) if r["missing"] else "-"
        if len(missing_str) > 50:
            missing_str = missing_str[:50] + "..."
        dataset_name = f"\033[1m{ds}\033[0m"
        table.append(
            [
                dataset_name,
                r["total"],
                f"{pct:.1f}%",
                f"{n_failed} ({failed_str})",
                f"{n_missing} ({missing_str})",
            ]
        )
        if pct == 100:
            for i in range(len(table[-1])):
                table[-1][i] = f"\033[92m{table[-1][i]}\033[0m"
        elif pct < 50:
            for i in range(len(table[-1])):
                table[-1][i] = f"\033[91m{table[-1][i]}\033[0m"
        else:
            for i in range(len(table[-1])):
                table[-1][i] = f"\033[93m{table[-1][i]}\033[0m"

    # Totals
    total_all = sum(r["total"] for r in report.values())
    failed_all = sum(len(r["failed"]) for r in report.values())
    missing_all = sum(len(r["missing"]) for r in report.values())
    pct_all = 100.0 * (total_all - missing_all) / total_all if total_all > 0 else 0
    table.append(
        [
            "\033[1mTOTAL\033[0m",
            total_all,
            f"{pct_all:.1f}%",
            f"{failed_all}",
            f"{missing_all}",
        ]
    )

    headers = [
        "Dataset",
        "Total",
        "Completed",
        "Failed (job IDs)",
        "Missing (job IDs)",
    ]
    print(
        "\n"
        + tabulate(
            table, headers=headers, tablefmt="grid", stralign="left", numalign="left"
        )
    )
