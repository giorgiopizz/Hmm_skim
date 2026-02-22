import ROOT


def load_cpp_utils(module_folder, data_folder, year, is_data=False):
    MUON_SF_FILE = f"{data_folder}/{year}/muon_Z.json.gz"
    MUON_ID_TAG = "NUM_MediumID_DEN_TrackerMuons"
    MUON_ISO_TAG = "NUM_LoosePFIso_DEN_MediumID"
    MUON_TRG_TAG = "NUM_IsoMu24_DEN_CutBasedIdMedium_and_PFIsoMedium"

    # # FIXME
    # MUON_ID_TAG = "NUM_TightID_DEN_TrackerMuons"
    # MUON_ISO_TAG = "NUM_TightPFIso_DEN_TightID"
    # MUON_TRG_TAG = "NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight"

    MUON_SCARE_FILE = f"{data_folder}/{year}/muon_scalesmearing.json.gz"

    line = f"""
    #include "{module_folder}/muon_scare.cpp"
    """
    ROOT.gInterpreter.Declare(line)
    print("Loaded Muon C++ modules")

    line = f"""
    auto cset_muon_sf = correction::CorrectionSet::from_file("{MUON_SF_FILE}");
    auto ceval_muon_id = cset_muon_sf->at("{MUON_ID_TAG}");
    auto ceval_muon_iso = cset_muon_sf->at("{MUON_ISO_TAG}");
    auto ceval_muon_trg = cset_muon_sf->at("{MUON_TRG_TAG}");

    auto cset_muon_scare = correction::CorrectionSet::from_file("{MUON_SCARE_FILE}");
    auto muon_scare = MuonScaRe(std::move(cset_muon_scare));
    """
    ROOT.gInterpreter.Declare(line)


def run_muon_sf(df, is_data=False, run_syst=True):
    if not is_data:
        for mu_idx in [1, 2]:
            df = df.Define(
                f"weight_sf_mu{mu_idx}_id",
                f'ceval_muon_id->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > 15 ? mu{mu_idx}_pt : 15, "nominal"}})',
            )
            if run_syst:
                df = df.Define(
                    f"weight_sf_mu{mu_idx}_id_up",
                    f'ceval_muon_id->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > 15 ? mu{mu_idx}_pt : 15, "systup"}})',
                )
                df = df.Define(
                    f"weight_sf_mu{mu_idx}_id_down",
                    f'ceval_muon_id->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > 15 ? mu{mu_idx}_pt : 15, "systdown"}})',
                )

            df = df.Define(
                f"weight_sf_mu{mu_idx}_iso",
                f'ceval_muon_iso->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > 15 ? mu{mu_idx}_pt : 15, "nominal"}})',
            )
            if run_syst:
                df = df.Define(
                    f"weight_sf_mu{mu_idx}_iso_up",
                    f'ceval_muon_iso->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > 15 ? mu{mu_idx}_pt : 15, "systup"}})',
                )
                df = df.Define(
                    f"weight_sf_mu{mu_idx}_iso_down",
                    f'ceval_muon_iso->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > 15 ? mu{mu_idx}_pt : 15, "systdown"}})',
                )

            df = df.Define(
                f"weight_sf_mu{mu_idx}_trg",
                f'ceval_muon_trg->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > 26 ? mu{mu_idx}_pt : 26, "nominal"}})',
            )
            if run_syst:
                df = df.Define(
                    f"weight_sf_mu{mu_idx}_trg_up",
                    f'ceval_muon_trg->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > 26 ? mu{mu_idx}_pt : 26, "systup"}})',
                )
                df = df.Define(
                    f"weight_sf_mu{mu_idx}_trg_down",
                    f'ceval_muon_trg->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > 26 ? mu{mu_idx}_pt : 26, "systdown"}})',
                )

    # run ScaRe
    for mu_idx in [1, 2]:
        df = df.Define(
            f"mu{mu_idx}_pt_no_corr",
            f"mu{mu_idx}_pt",
        )

    if is_data:
        for mu_idx in [1, 2]:
            df = df.Redefine(
                f"mu{mu_idx}_pt",
                f"muon_scare.pt_scale(1, mu{mu_idx}_pt, mu{mu_idx}_eta, mu{mu_idx}_phi, mu{mu_idx}_charge)",
            )
    else:
        for mu_idx in [1, 2]:
            df = df.Define(
                f"mu{mu_idx}_pt_scale_corr",
                f"muon_scare.pt_scale(0, mu{mu_idx}_pt, mu{mu_idx}_eta, mu{mu_idx}_phi, mu{mu_idx}_charge)",
            )

            df = df.Define(
                f"mu{mu_idx}_pt_corr",
                f"muon_scare.pt_resol(mu{mu_idx}_pt_scale_corr, mu{mu_idx}_eta, mu{mu_idx}_phi, float(mu{mu_idx}_nTrackerLayers), event, luminosityBlock)",
            )

            if run_syst:
                df = df.Define(
                    f"mu{mu_idx}_pt_scale_up",
                    f'muon_scare.pt_scale_var(mu{mu_idx}_pt_corr, mu{mu_idx}_eta, mu{mu_idx}_phi, mu{mu_idx}_charge, "up")',
                )
                df = df.Define(
                    f"mu{mu_idx}_pt_scale_down",
                    f'muon_scare.pt_scale_var(mu{mu_idx}_pt_corr, mu{mu_idx}_eta, mu{mu_idx}_phi, mu{mu_idx}_charge, "dn")',
                )

                df = df.Define(
                    f"mu{mu_idx}_pt_res_up",
                    f'muon_scare.pt_resol_var(mu{mu_idx}_pt_scale_corr, mu{mu_idx}_pt_corr, mu{mu_idx}_eta, "up")',
                )
                df = df.Define(
                    f"mu{mu_idx}_pt_res_down",
                    f'muon_scare.pt_resol_var(mu{mu_idx}_pt_scale_corr, mu{mu_idx}_pt_corr, mu{mu_idx}_eta, "dn")',
                )

            df = df.Redefine(
                f"mu{mu_idx}_pt",
                f"mu{mu_idx}_pt_corr",
            )

    # df.Display(["weight_sf_mu1_id", "mu1_pt_scale_up", "mu1_pt_res_up", "mu1_pt"], 10).Print()
    return df
