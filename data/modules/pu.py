import ROOT


def load_cpp_utils(data_folder, year):
    golden_files = {
        "2024": "Cert_Collisions2024_378981_386951_Golden.json",
        "2023": "Cert_Collisions2023_366442_370790_Golden.json",
    }

    pu_keys = {
        "2024": {
            "file": "puWeights_BCDEFGHI.json.gz",
            "json": "Collisions24_BCDEFGHI_goldenJSON",
        },
        "2023": {
            "file": "puWeights.json.gz",
            "json": "Collisions2023_366403_369802_eraBC_GoldenJson",
        },
    }

    pu_file = f"{data_folder}/{year}/{pu_keys[year]['file']}"
    pu_json = pu_keys[year]["json"]

    golden_file = golden_files[year]

    line = f"""
    #include "{data_folder}/modules/trig_match.cpp"
    #include "{data_folder}/modules/lumi.h"

    auto cset_pu = correction::CorrectionSet::from_file("{pu_file}");
    auto ceval_pu = cset_pu->at("{pu_json}");

    auto lumi_filter = LumiFilter("{data_folder}/{year}/{golden_file}");
    """
    ROOT.gInterpreter.Declare(line)
