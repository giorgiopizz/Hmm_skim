import ROOT


def load_cpp_utils(module_folder, data_folder, year, era=None, is_data=False):
    JERC_FILE = f"{data_folder}/{year}/jet_jerc.json.gz"
    JERSMEAR_FILE = f"{data_folder}/{year}/jer_smear.json.gz"
    JER_JET_ALGO = "AK4PFPuppi"

    line = f"""
    #include "{module_folder}/jet_correction.cpp"
    """
    ROOT.gInterpreter.Declare(line)

    jerc_tags = {
        "2025": {
            "data": "Winter25Prompt25_V3_DATA",
            "mc": ["Winter25Prompt25_V3_MC", "Summer23BPixPrompt23_RunD_JRV1_MC"],
        },
        "2024": {
            "data": "Summer24Prompt24_V2_DATA",
            "mc": ["Summer24Prompt24_V2_MC", "Summer23BPixPrompt23_RunD_JRV1_MC"],
        },
        "2023BPix": {
            "data": "Summer23BPixPrompt23_V3_DATA",
            "mc": ["Summer23BPixPrompt23_V3_MC", "Summer23BPixPrompt23_RunD_JRV1_MC"],
        },
        "2023": {
            "data": "Summer23Prompt23_V2_DATA",
            "mc": ["Summer23Prompt23_V2_MC", "Summer23Prompt23_RunCv1234_JRV1_MC"],
        },
        "2022EE": {
            "data": {
                "E": "Summer22EE_22Sep2023_RunE_V3_DATA",
                "F": "Summer22EE_22Sep2023_RunF_V3_DATA",
                "G": "Summer22EE_22Sep2023_RunG_V3_DATA",
            },
            "mc": ["Summer22EE_22Sep2023_V3_MC", "Summer22EE_22Sep2023_JRV1_MC"],
        },
        "2022": {
            "data": "Summer22_22Sep2023_RunCD_V3_DATA",
            "mc": ["Summer22_22Sep2023_V3_MC", "Summer22_22Sep2023_JRV1_MC"],
        },
    }

    if is_data:
        JEC_TAG = jerc_tags[year]["data"]
        line = f"""
        auto cset_jerc = correction::CorrectionSet::from_file("{JERC_FILE}");
        """
        if isinstance(JEC_TAG, dict):
            line += f"""
                auto cset_jec = cset_jerc->compound().at("{JEC_TAG[era]}_L1L2L3Res_{JER_JET_ALGO}");
                """
        else:
            if year in ["2024"]:
                line += f"""
                auto cset_jec_l1 = cset_jerc->at("{JEC_TAG}_L1FastJet_{JER_JET_ALGO}");
                auto cset_jec_l2 = cset_jerc->at("{JEC_TAG}_L2Relative_{JER_JET_ALGO}");
                auto cset_jec_l3 = cset_jerc->at("{JEC_TAG}_L3Absolute_{JER_JET_ALGO}");
                auto cset_jec_l2l3res = cset_jerc->at("{JEC_TAG}_L2L3Residual_{JER_JET_ALGO}");
                """
            else:
                line += f"""
                auto cset_jec = cset_jerc->compound().at("{JEC_TAG}_L1L2L3Res_{JER_JET_ALGO}");
                """
    else:
        JEC_TAG, JER_TAG = jerc_tags[year]["mc"]
        line = f"""
        auto cset_jerc = correction::CorrectionSet::from_file("{JERC_FILE}");
        auto cset_jersmear = correction::CorrectionSet::from_file("{JERSMEAR_FILE}");
        auto jme_key = "{JEC_TAG}_L1L2L3Res_{JER_JET_ALGO}";
        auto cset_jec = cset_jerc->compound().at(jme_key);
        auto cset_jes = cset_jerc->at("{JEC_TAG}_Total_{JER_JET_ALGO}");

        jme_key = "{JER_TAG}_ScaleFactor_{JER_JET_ALGO}";
        auto cset_jer = cset_jerc->at(jme_key);

        jme_key = "{JER_TAG}_PtResolution_{JER_JET_ALGO}";
        auto cset_jer_ptres = cset_jerc->at(jme_key);

        jme_key = "JERSmear";
        auto ceval_jersmear = cset_jersmear->at(jme_key);

        """
    ROOT.gInterpreter.Declare(line)
    print("Loaded JEC/JER C++ modules")


def run_jme_data(df, year):
    df = df.Define("Jet_pt_no_corr", "Jet_pt")
    df = df.Define("Jet_mass_no_corr", "Jet_mass")

    if year in ["2025"]:
        df = df.Define(
            "Jet_pt_mass_jec",
            "v15::sf_jec_data(cset_jec, Jet_pt, Jet_eta, Jet_phi, Jet_mass, Jet_rawFactor, Jet_area, Rho_fixedGridRhoFastjetAll, run)",
        )
    elif year in ["2024"]:
        df = df.Define(
            "Jet_pt_mass_jec",
            "v15::sf_jec_data(cset_jec_l1, cset_jec_l2, cset_jec_l3, cset_jec_l2l3res, Jet_pt, Jet_eta, Jet_phi, Jet_mass, Jet_rawFactor, Jet_area, Rho_fixedGridRhoFastjetAll, run)",
        )
    else:
        takes_run = "false"
        takes_phi = "false"
        if year in ["2023"]:
            takes_run = "true"
        if year in ["2023BPix"]:
            takes_run = "true"
            takes_phi = "true"

        df = df.Define(
            "Jet_pt_mass_jec",
            f"v12::sf_jec_data(cset_jec, Jet_pt, Jet_eta, Jet_phi, Jet_mass, Jet_rawFactor, Jet_area, Rho_fixedGridRhoFastjetAll, run, {takes_run}, {takes_phi})",
        )
    df = df.Define("Jet_pt_jec", "Jet_pt_mass_jec.get_pt()")
    df = df.Define("Jet_mass_jec", "Jet_pt_mass_jec.get_mass()")

    df = df.Redefine("Jet_pt", "Jet_pt_jec")
    df = df.Redefine("Jet_mass", "Jet_mass_jec")

    # df.Display(["Jet_pt_no_corr", "Jet_pt"]).Print()
    return df


def run_jme_mc(df, year, run_syst=True):
    # 1. first apply JEC
    # 2. apply JER
    # 3. compute JES

    df = df.Define("Jet_pt_no_corr", "Jet_pt")
    df = df.Define("Jet_mass_no_corr", "Jet_mass")

    if year in ["2024", "2025"]:
        df = df.Define(
            "Jet_pt_mass_jec",
            "v15::sf_jec(cset_jec, Jet_pt, Jet_eta, Jet_phi, Jet_mass, Jet_rawFactor, Jet_area, Rho_fixedGridRhoFastjetAll)",
        )
    else:
        takes_phi = "false"
        if year in ["2023BPix"]:
            takes_phi = "true"
        df = df.Define(
            "Jet_pt_mass_jec",
            f"v12::sf_jec(cset_jec, Jet_pt, Jet_eta, Jet_phi, Jet_mass, Jet_rawFactor, Jet_area, Rho_fixedGridRhoFastjetAll, {takes_phi})",
        )
    df = df.Define("Jet_pt_jec", "Jet_pt_mass_jec.get_pt()")
    df = df.Define("Jet_mass_jec", "Jet_pt_mass_jec.get_mass()")

    df = df.Define(
        "Jet_seed",
        "(run << 20) + (luminosityBlock << 10) + event + int(Jet_eta.size()) > 0 ? Jet_eta[0]/0.01 : 0",
    )

    if year in ["2025"]:
        mitigate_horns = "false"
    else:
        mitigate_horns = "true"
    df = df.Define(
        "Jet_pt_mass_jec_jer",
        f"sf_jer(cset_jer, cset_jer_ptres, ceval_jersmear, Jet_pt_jec, Jet_eta, Jet_phi, Jet_mass_jec, Jet_genJetIdx, Jet_seed, GenJet_pt, GenJet_eta, GenJet_phi, Rho_fixedGridRhoFastjetAll, {mitigate_horns})",
    )

    df = df.Redefine("Jet_pt", "std::get<0>(Jet_pt_mass_jec_jer).get_pt()")
    df = df.Redefine("Jet_mass", "std::get<0>(Jet_pt_mass_jec_jer).get_mass()")

    if run_syst:
        df = df.Define("Jet_pt_jer_down", "std::get<1>(Jet_pt_mass_jec_jer).get_pt()")
        df = df.Define(
            "Jet_mass_jer_down", "std::get<1>(Jet_pt_mass_jec_jer).get_mass()"
        )

        df = df.Define("Jet_pt_jer_up", "std::get<2>(Jet_pt_mass_jec_jer).get_pt()")
        df = df.Define("Jet_mass_jer_up", "std::get<2>(Jet_pt_mass_jec_jer).get_mass()")

        # apply JES uncertainties
        df = df.Define(
            "Jet_pt_mass_jes",
            "sf_jes(cset_jes, Jet_eta, Jet_pt, Jet_mass)",
        )
        df = df.Define("Jet_pt_jes_down", "std::get<0>(Jet_pt_mass_jes).get_pt()")
        df = df.Define("Jet_mass_jes_down", "std::get<0>(Jet_pt_mass_jes).get_mass()")

        df = df.Define("Jet_pt_jes_up", "std::get<1>(Jet_pt_mass_jes).get_pt()")
        df = df.Define("Jet_mass_jes_up", "std::get<1>(Jet_pt_mass_jes).get_mass()")

    # df.Display(["Jet_pt_no_corr", "Jet_pt_jec", "Jet_pt", "Jet_eta"]).Print()

    return df
