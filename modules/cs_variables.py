import ROOT


def load_cpp_utils(module_folder):
    line = f"""
    #include "{module_folder}/cs_variables.cpp"
    """
    ROOT.gInterpreter.Declare(line)
    print("Loaded CS Variables C++ modules")


def run_cs_variables(df):
    df = df.Define(
        "cs_variables",
        "compute_cs_variables(mu1_pt, mu1_eta, mu1_phi, mu1_mass, mu1_charge, mu2_pt, mu2_eta, mu2_phi, mu2_mass)",
    )
    for i, var in enumerate(["phi_cs", "cos_theta_cs"]):
        df = df.Define(var, f"std::get<{i}>(cs_variables)")

    df = df.Define(
        "NN_variables",
        "compute_NN_variables((mu1_p4 + mu2_p4), j1_p4, j2_p4, njet)",
    )
    for i, var in enumerate(["zeppenfeld", "min_dphi_lljj", "min_deta_lljj"]):
        df = df.Define(var, f"std::get<{i}>(NN_variables)")
    return df
