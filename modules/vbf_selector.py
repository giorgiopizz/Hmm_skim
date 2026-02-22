import ROOT


def load_cpp_utils(module_folder, data_folder, year, is_data=False):
    line = f"""
    #include "{module_folder}/vbf_selector.cpp"
    """
    ROOT.gInterpreter.Declare(line)
    print("Loaded VBF Selector C++ module")


def run_vbf_selector(df, year):
    df = df.Define(
        "Jet_vbf_indices", "GetVBFJetIndices(Jet_pt, Jet_eta, Jet_phi, Jet_mass)"
    )
    df = df.Define("Jet_vbf_idx1", "std::get<0>(Jet_vbf_indices)")
    df = df.Define("Jet_vbf_idx2", "std::get<1>(Jet_vbf_indices)")
    return df
