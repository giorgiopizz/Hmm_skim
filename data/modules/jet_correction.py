import ROOT


def load_cpp_utils(data_folder, is_data=False):
    JERC_FILE = f"{data_folder}/2024/jet_jerc.json.gz"
    JERSMEAR_FILE = f"{data_folder}/2024/jer_smear.json.gz"
    JER_JET_ALGO = "AK4PFPuppi"

    line = f"""
    #include "{data_folder}/modules/jet_correction.cpp"
    """
    ROOT.gInterpreter.Declare(line)
    print("Loaded JEC/JER C++ modules")

    if is_data:
        JEC_TAG = "Summer24Prompt24_V2_DATA"
        line = f"""
        auto cset_jerc = correction::CorrectionSet::from_file("{JERC_FILE}");
        auto cset_jersmear = correction::CorrectionSet::from_file("{JERSMEAR_FILE}");
        auto cset_jec_l1 = cset_jerc->at("{JEC_TAG}_L1FastJet_{JER_JET_ALGO}");
        auto cset_jec_l2 = cset_jerc->at("{JEC_TAG}_L2Relative_{JER_JET_ALGO}");
        auto cset_jec_l3 = cset_jerc->at("{JEC_TAG}_L3Absolute_{JER_JET_ALGO}");
        auto cset_jec_l2l3res = cset_jerc->at("{JEC_TAG}_L2L3Residual_{JER_JET_ALGO}");
        """
    else:
        JEC_TAG = "Summer24Prompt24_V2_MC"
        JER_TAG = "Summer23BPixPrompt23_RunD_JRV1_MC"
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


def run_jme_data(df):
    df = df.Define("Jet_pt_no_corr", "Jet_pt")
    df = df.Define("Jet_mass_no_corr", "Jet_mass")

    df = df.Define(
        "Jet_pt_mass_jec",
        "sf_jec_data(cset_jec_l1, cset_jec_l2, cset_jec_l3, cset_jec_l2l3res, Jet_pt, Jet_eta, Jet_phi, Jet_mass, Jet_rawFactor, Jet_area, Rho_fixedGridRhoFastjetAll, run)",
    )
    df = df.Define("Jet_pt_jec", "Jet_pt_mass_jec.get_pt()")
    df = df.Define("Jet_mass_jec", "Jet_pt_mass_jec.get_mass()")

    df = df.Redefine("Jet_pt", "Jet_pt_jec")
    df = df.Redefine("Jet_mass", "Jet_mass_jec")

    # df.Display(["Jet_pt_no_corr", "Jet_pt"]).Print()
    return df


def run_jme_mc(df):
    # 1. first apply JEC
    # 2. apply JER
    # 3. compute JES

    df = df.Define("Jet_pt_no_corr", "Jet_pt")
    df = df.Define("Jet_mass_no_corr", "Jet_mass")

    df = df.Define(
        "Jet_pt_mass_jec",
        "sf_jec(cset_jec, Jet_pt, Jet_eta, Jet_phi, Jet_mass, Jet_rawFactor, Jet_area, Rho_fixedGridRhoFastjetAll)",
    )
    df = df.Define("Jet_pt_jec", "Jet_pt_mass_jec.get_pt()")
    df = df.Define("Jet_mass_jec", "Jet_pt_mass_jec.get_mass()")

    df = df.Define(
        "Jet_seed",
        "(run << 20) + (luminosityBlock << 10) + event + int(Jet_eta.size()) > 0 ? Jet_eta[0]/0.01 : 0",
    )

    df = df.Define(
        "Jet_pt_mass_jec_jer",
        "sf_jer(cset_jer, cset_jer_ptres, ceval_jersmear, Jet_pt_jec, Jet_eta, Jet_phi, Jet_mass_jec, Jet_genJetIdx, Jet_seed, GenJet_pt, GenJet_eta, GenJet_phi, Rho_fixedGridRhoFastjetAll)",
    )

    df = df.Redefine("Jet_pt", "std::get<0>(Jet_pt_mass_jec_jer).get_pt()")
    df = df.Redefine("Jet_mass", "std::get<0>(Jet_pt_mass_jec_jer).get_mass()")

    df = df.Define("Jet_pt_jer_down", "std::get<1>(Jet_pt_mass_jec_jer).get_pt()")
    df = df.Define("Jet_mass_jer_down", "std::get<1>(Jet_pt_mass_jec_jer).get_mass()")

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
