import os


def get_fw_path():
    return os.environ["FW_PATH"]


base_output_folder = get_fw_path() + "/rootfiles/"
base_output_folder = "/eos/user/g/gpizzati/hmm_skim/"

def get_results_folder(tag, year):
    return f"{base_output_folder}/{tag}/{year}/"


def common_args(additional_args: list[dict] = []):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year", type=str, required=True, help="Year of the production"
    )
    parser.add_argument("--tag", type=str, required=True, help="Tag of the production")
    for arg in additional_args:
        arg_name = arg.pop("name")
        parser.add_argument(arg_name, **arg)
    args = parser.parse_args()
    print(f"Running with year={args.year} and tag={args.tag}")
    return args


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


def add_dict_iterable(iterable):
    tmp = -99999
    for it in iterable:
        if tmp == -99999:
            tmp = it
        else:
            tmp = add_dict(tmp, it)
    return tmp
