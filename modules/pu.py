import ROOT


def load_cpp_utils(module_folder, data_folder, year):
    golden_files = {
        "2025": "Cert_Collisions2025_391658_398903_Golden.json",
        "2024": "Cert_Collisions2024_378981_386951_Golden.json",
        "2023": "Cert_Collisions2023_366442_370790_Golden.json",
        "2022EE": "Cert_Collisions2022_355100_362760_Golden.json",
        "2022": "Cert_Collisions2022_355100_362760_Golden.json",
    }

    pu_keys = {
        "2025": {
            "file": "puWeights_BCDEFGHI.json.gz",
            "json": "Collisions24_BCDEFGHI_goldenJSON",
        },
        "2024": {
            "file": "puWeights_BCDEFGHI.json.gz",
            "json": "Collisions24_BCDEFGHI_goldenJSON",
        },
        "2023BPix": {
            "file": "puWeights.json.gz",
            "json": "Collisions2023_369803_370790_eraD_GoldenJson",
        },
        "2023": {
            "file": "puWeights.json.gz",
            "json": "Collisions2023_366403_369802_eraBC_GoldenJson",
        },
        "2022EE": {
            "file": "puWeights.json.gz",
            "json": "Collisions2022_359022_362760_eraEFG_GoldenJson",
        },
        "2022": {
            "file": "puWeights.json.gz",
            "json": "Collisions2022_355100_357900_eraBCD_GoldenJson",
        },
    }

    _year = year
    if year == "2025":
        _year = "2024"

    pu_file = f"{data_folder}/{_year}/{pu_keys[year]['file']}"
    pu_json = pu_keys[year]["json"]

    golden_file = golden_files[year]

    line = f"""
    #include "{module_folder}/trig_match.cpp"
    #include "{module_folder}/lumi.h"


    auto lumi_filter = LumiFilter("{data_folder}/{year}/{golden_file}");
    """

    line += f"""
    auto cset_pu = correction::CorrectionSet::from_file("{pu_file}");
    auto ceval_pu = cset_pu->at("{pu_json}");
    """

    ROOT.gInterpreter.Declare(line)
