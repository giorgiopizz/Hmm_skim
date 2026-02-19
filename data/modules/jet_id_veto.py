import ROOT


def load_cpp_utils(data_folder, year, is_data=False):
    if year == "2024":
        JETID_FILE = f"{data_folder}/{year}/jetid.json.gz"
        line = f"""
        auto cset_jetid = correction::CorrectionSet::from_file("{JETID_FILE}");
        """
        ROOT.gInterpreter.Declare(line)

    jetveto_tags = {
        "2024": "Summer24Prompt24_RunBCDEFGHI_V1",
        "2023": "Summer23Prompt23_RunC_V1",
    }
    JETVETO_FILE = f"{data_folder}/{year}/jetvetomaps.json.gz"
    JETVETO_TAG = jetveto_tags[year]

    line = f"""
    #include "{data_folder}/modules/jet_id_veto.cpp"
    """
    ROOT.gInterpreter.Declare(line)
    print("Loaded JET ID/VETO C++ modules")

    line = f"""
    auto cset_jetveto = correction::CorrectionSet::from_file("{JETVETO_FILE}");

    auto ceval_jetveto = cset_jetveto->at("{JETVETO_TAG}");
    """
    ROOT.gInterpreter.Declare(line)


def run_jetid_veto(df, year):

    if year == "2024":
        df = df.Define(
            "Jet_id_tight_tightlep",
            "jet_id(cset_jetid, Jet_eta, Jet_chHEF, Jet_neHEF, Jet_chEmEF, Jet_neEmEF, Jet_muEF, Jet_chMultiplicity, Jet_neMultiplicity)",
        )

    else:
        df = df.Define(
            "Jet_id_tight_tightlep",
            "jet_id_v12(Jet_eta, Jet_neHEF, Jet_chEmEF, Jet_neEmEF, Jet_muEF, Jet_jetId)",
        )

    df = df.Define("Jet_tightId", "std::get<0>(Jet_id_tight_tightlep)")
    df = df.Define("Jet_tightLepVetoId", "std::get<1>(Jet_id_tight_tightlep)")

    df = df.Define(
        "Jet_veto_map",
        "jet_veto(ceval_jetveto, Jet_eta, Jet_phi)",
    )

    df = df.Define(
        "Jet_veto",
        "(Jet_pt > 15) && (Jet_veto_map != 0) && (Jet_tightLepVetoId == 1) && ((Jet_chEmEF + Jet_neEmEF) < 0.9)",
    )

    # df.Display(["Jet_tightId", "Jet_tightLepVetoId", "Jet_veto_map", "Jet_veto"]).Print()

    return df
