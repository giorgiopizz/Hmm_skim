import ROOT


def load_cpp_utils(module_folder):
    line = f"""
    #include "{module_folder}/fsr_recovery.cpp"
    """
    ROOT.gInterpreter.Declare(line)
    print("Loaded FSR Recovery C++ modules")


def run_fsr_recovery(df):
    for mu_idx in [1, 2]:
        df = df.Define(
            f"mu{mu_idx}_fsr_p4",
            f"fsr_corrected_p4(mu{mu_idx}_pt, mu{mu_idx}_eta, mu{mu_idx}_phi, mu{mu_idx}_mass, mu{mu_idx}_fsrPhotonIdx, FsrPhoton_pt, FsrPhoton_eta, FsrPhoton_phi, FsrPhoton_dROverEt2, FsrPhoton_relIso03, FsrPhoton_electronIdx)",
        )
        for var in ["pt", "eta", "phi", "mass"]:
            df = df.Define(
                f"mu{mu_idx}_{var}_no_fsr",
                f"mu{mu_idx}_{var}",
            )
            df = df.Redefine(
                f"mu{mu_idx}_{var}",
                f"std::get<0>(mu{mu_idx}_fsr_p4) ? std::get<1>(mu{mu_idx}_fsr_p4).{var}() : mu{mu_idx}_{var}",
            )
        df = df.Define(
            f"mu{mu_idx}_is_fsr_recovered",
            f"std::get<0>(mu{mu_idx}_fsr_p4)",
        )
    return df
