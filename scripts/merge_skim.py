import json
import argparse

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
    
    
    results = []
    for ds in datasets_files:
        for ifile, file in enumerate(datasets_files[ds]):

            
            results.append(result)

    for i in range(len(results)):
        ds = list(results[i].keys())[0]
        for key in ["sumw", "nevents_before", "nevents_after"]:
            results[i][ds][key] = results[i][ds][key]

        for key in ["nevents"]:
            results[i][ds]["files"][0][key] = results[i][ds]["files"][0][key]

    results = add_dict_iterable(results)
    with open("skimmed_results.json", "w") as f:
        json.dump(results, f, indent=2)
