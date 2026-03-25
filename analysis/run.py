import ROOT
import glob
import json
import correctionlib
import argparse
from config import get_config

correctionlib.register_pyroot_binding()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year", type=str, help="Year of the production", required=True
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Whether to do snapshot instead of filling histograms",
    )
    parser.add_argument(
        "--ptll", action="store_true", help="Whether to apply ptll reweighting"
    )
    parser.add_argument(
        "--sigma_calib", action="store_true", help="Whether to apply sigma calibration"
    )
    args = parser.parse_args()
    year = args.year
    do_snapshot = args.snapshot
    apply_ptll = args.ptll
    apply_sigma_calib = args.sigma_calib

    datasets, variables, regions, base_folder = get_config(year, apply_ptll)

    datasets_flat = []
    for ds in datasets:
        for ds_single in datasets[ds]["names"]:
            datasets_flat.append(ds_single)

    rescales = {}
    with open(f"{base_folder}/results.json") as f:
        data = json.load(f)
        for ds in datasets_flat:
            rescales[ds] = data.get(ds, {}).get("rescale", 1.0)
    print(rescales)

    specs = {}
    for ds in datasets:
        spec = ROOT.RDF.Experimental.RDatasetSpec()
        for ds_single in datasets[ds]["names"]:
            meta = ROOT.RDF.Experimental.RMetaData()
            meta.Add("rescale", rescales[ds_single])
            meta.Add("dataset", ds)
            files = glob.glob(f"{base_folder}/{ds_single}_skimmed_*.root")[:]
            if len(files) == 0:
                raise Exception(f"No files found for dataset {ds_single}")
            sample = ROOT.RDF.Experimental.RSample(
                ds_single,
                "Events",
                files,
                meta,
            )
            spec.AddSample(sample)
        specs[ds] = spec

    # load ptll rwgt
    if apply_ptll:
        line = f"""
        auto ptll_rwgt = correction::CorrectionSet::from_file("rwgts/{year}.json")->at("ptll_rwgt");
        auto njet_rwgt = correction::CorrectionSet::from_file("rwgts/{year}.json")->at("njet_rwgt");
        """
        ROOT.gInterpreter.Declare(line)

    if apply_sigma_calib:
        line = f"""
        auto sigma_calib = correction::CorrectionSet::from_file("calib_sigma/calib_sigma.json")->at("calib_sigma");
        auto res_calib = correction::CorrectionSet::from_file("calib_sigma/calib_resolution.json")->at("calib_resolution");
        """
        ROOT.gInterpreter.Declare(line)

    from modules.cs_variables import (
        run_cs_variables,
        load_cpp_utils as load_cs_variables_cpp_utils,
    )
    from modules.muon_sf import (
        load_cpp_utils as load_muon_sf_cpp_utils,
        run_muon_scare,
        run_muon_sf,
    )
    from modules.vbf_selector import (
        run_vbf_selector,
        load_cpp_utils as load_vbf_selector_utils,
    )

    load_cs_variables_cpp_utils("../modules")
    load_muon_sf_cpp_utils("../modules", "../data", year)
    load_vbf_selector_utils("../modules", "", "")
    # load_scare_closure()

    # line = f"""
    # auto ceval_muon_trg = correction::CorrectionSet::from_file("../data/{year}/muon_Z.json.gz")->at("NUM_IsoMu24_DEN_CutBasedIdMedium_and_PFIsoMedium");
    # """
    # ROOT.gInterpreter.Declare(line)

    ROOT.EnableImplicitMT()

    def process_dataset(spec):
        is_data = spec.GetSampleNames()[0].startswith("Muon")
        dataset = spec.GetMetaData()[0].GetS("dataset")
        is_dy = dataset == "DY"
        df = ROOT.RDataFrame(spec)

        # for mu_idx in [1, 2]:
        #     var = "pt"
        #     df = df.Define(f"mu{mu_idx}_{var}_all_corr", f"mu{mu_idx}_{var}")
        #     # df = df.Redefine(f"mu{mu_idx}_{var}", f"mu{mu_idx}_{var}_no_corr")
        #     df = df.Redefine(f"mu{mu_idx}_{var}", f"mu{mu_idx}_{var}_no_bs")
        #     for var in ["eta", "phi", "mass"]:
        #         df = df.Redefine(f"mu{mu_idx}_{var}", f"mu{mu_idx}_{var}_no_fsr")

        # # FIXME
        # if not is_data:
        #     for mu_idx in [1, 2]:
        #         pt_min = 10
        #         df = df.Redefine(
        #             f"weight_sf_mu{mu_idx}_id",
        #             f'ceval_muon_id->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > {pt_min} ? mu{mu_idx}_pt : {pt_min}, "nominal"}})',
        #         )
        #         df = df.Redefine(
        #             f"weight_sf_mu{mu_idx}_iso",
        #             f'ceval_muon_iso->evaluate({{mu{mu_idx}_eta, mu{mu_idx}_pt > {pt_min} ? mu{mu_idx}_pt : {pt_min}, "nominal"}})',
        #         )

        #     # mu_idx = 1
        #     # pt_min_trigger = 26
        #     # df = df.Redefine(
        #     #     f"weight_sf_mu{mu_idx}_trg",
        #     #     f'ceval_muon_trg->evaluate({{fabs(mu{mu_idx}_eta) < 2.4 ? mu{mu_idx}_eta : 2.399 * (mu{mu_idx}_eta / fabs(mu{mu_idx}_eta)), mu{mu_idx}_pt > {pt_min_trigger} ? mu{mu_idx}_pt : {pt_min_trigger}, "nominal"}})',
        #     # )

        if is_data:
            df = df.Define("weight", "1.0")
        else:
            df = df.DefinePerSample("rescale", """rdfsampleinfo_.GetD("rescale")""")
            sfs = []
            sfs += [
                f"weight_sf_mu{mu_idx}_{typ}"
                for mu_idx in [1, 2]
                for typ in ["id", "iso"]
            ]
            # sfs += ["weight_sf_mu1_trg"]
            # sfs += ["weight_trigger_SF"]
            sfs += ["weight_sf_pu"]
            weight_sf = "genWeight * rescale * " + " * ".join(sfs)
            df = df.Define("weight", weight_sf)

        # for mu_idx in [1, 2]:
        #     var = "pt"
        #     df = df.Define(f"mu{mu_idx}_{var}_all_corr", f"mu{mu_idx}_{var}")
        #     df = df.Redefine(f"mu{mu_idx}_{var}", f"mu{mu_idx}_{var}_no_bs")
        #     for var in ["eta", "phi", "mass"]:
        #         df = df.Redefine(f"mu{mu_idx}_{var}", f"mu{mu_idx}_{var}_no_fsr")

        # df = run_muon_sf(df, year, is_data, run_syst=False)

        # if not is_data:
        #     sfs = []
        #     sfs += [
        #         f"weight_sf_mu{mu_idx}_{typ}"
        #         for mu_idx in [1, 2]
        #         for typ in ["id", "iso"]
        #     ]
        #     sfs += ["weight_sf_mu1_trg"]
        #     df = df.Redefine("weight", "weight * " + " * ".join(sfs))

        # for mu_idx in [1, 2]:
        #     var = "pt"
        #     df = df.Redefine(f"mu{mu_idx}_{var}", f"mu{mu_idx}_{var}_no_corr")
        #     # df = df.Redefine(f"mu{mu_idx}_{var}", f"mu{mu_idx}_{var}_all_corr")

        # df = df.Filter("mu1_pfIsoId >= 3 && mu2_pfIsoId >= 3")
        # df = df.Filter("mu1_pt > 26 && mu2_pt > 15 && mu1_pt_no_corr > 15")
        df = df.Filter("mu1_pt > 26 && mu2_pt > 20")

        # typ = "BKG"
        # if is_data:
        #     typ = "DATA"
        # elif is_dy:
        #     typ = "SIG"

        # df = run_muon_scare_closure(df, typ)

        # if is_dy:
        #     df = df.Filter(
        #         "mu1_nTrackerLayers > 6.5 && mu1_nTrackerLayers < 17.5 && mu2_nTrackerLayers > 6.5 && mu2_nTrackerLayers < 17.5"
        #     )

        # if is_dy or is_data:
        # df = run_muon_scare(df, is_data, do_smear=not is_data, run_syst=False)

        df = df.Define(
            "mu1_p4", "ROOT::Math::PtEtaPhiMVector(mu1_pt, mu1_eta, mu1_phi, mu1_mass)"
        )
        df = df.Define(
            "mu2_p4", "ROOT::Math::PtEtaPhiMVector(mu2_pt, mu2_eta, mu2_phi, mu2_mass)"
        )

        df = df.Redefine("mll", "(mu1_p4 + mu2_p4).M()")

        # df = df.Redefine(
        #     "mll",
        #     "sqrt(2 * mu1_pt * mu2_pt * (cosh(mu1_eta - mu2_eta) - cos(mu1_phi - mu2_phi)))",
        # )

        # FIXME
        # df = df.Filter("mu1_pt > 26 && mu2_pt > 26 && mu1_pt_no_corr > 26")

        df = df.Filter("mu1_pdgId != mu2_pdgId")

        # df = df.Define("mll", " (mu1_p4 + mu2_p4).M() ")
        df = df.Define("ptll", " (mu1_p4 + mu2_p4).Pt() ")

        df = df.Define("ptl1", "mu1_pt")
        df = df.Define("ptl2", "mu2_pt")
        df = df.Define("etal1", "mu1_eta")
        df = df.Define("etal2", "mu2_eta")

        # df = df.Define("dRll", "ROOT::Math::VectorUtil::DeltaR(mu1_p4, mu2_p4)")
        # df = df.Filter("dRll >= 0.3")

        df = df.Define("etall", "(mu1_p4 + mu2_p4).Eta()")
        # df = df.Define("detall", "abs(mu1_p4.Eta() - mu2_p4.Eta())")
        # df = df.Define(
        #     "dphill",
        #     "ROOT::Math::VectorUtil::DeltaPhi(mu1_p4, mu2_p4)",
        # )

        # # df = df.Redefine(
        # df = df.Define(
        #     # "Jet_bad", "Jet_pt < 50 && abs(Jet_eta) > 2.5 && abs(Jet_eta) < 3"
        #     "Jet_bad",
        #     "Jet_pt < 25",
        # )

        cols = df.GetColumnNames()
        jet_cols = [str(col) for col in cols]
        jet_cols = list(
            filter(
                lambda k: (
                    k.startswith("Jet_")
                    and "vbf_idx" not in k
                    and "bad" not in k
                    and "vbf_indices" not in k
                ),
                jet_cols,
            )
        )
        for col in jet_cols + ["Jet_bad"]:
            col_name = col[4:]
            df = df.Redefine(f"Jet_{col_name}", f"Jet_{col_name}[!Jet_bad]")

        df = run_vbf_selector(df, year)

        df = df.Define(
            "is_vbf",
            # "vbf_jet_idx1 >= 0 && vbf_jet_idx2 >= 0 && vbf_mjj > 400 && vbf_detajj > 2.5 && !Jet_bad[vbf_jet_idx1] && !Jet_bad[vbf_jet_idx2]",
            "vbf_jet_idx1 >= 0 && vbf_jet_idx2 >= 0 && vbf_mjj > 400 && vbf_detajj > 2.5",
        )

        # df = df.Define(
        #     "Jet_horn", "Jet_pt < 50 && abs(Jet_eta) > 2.5 && abs(Jet_eta) < 3"
        # )

        if apply_sigma_calib:
            if is_data:
                df = df.Redefine(
                    "per_event_mass_res",
                    'per_event_mass_res * sigma_calib->evaluate({"data", ptl1, abs(etal1), abs(etal2)})',
                )
            else:
                df = df.Redefine(
                    "per_event_mass_res",
                    # 'per_event_mass_res * sigma_calib->evaluate({"mc", ptl1, abs(etal1), abs(etal2)})',
                    # FIXME!
                    'per_event_mass_res * sigma_calib->evaluate({"mc", ptl1, abs(etal1), abs(etal2)}) * res_calib->evaluate({ptl1, abs(etal1), abs(etal2)})',
                )

        df = df.Define("sigma_res", "per_event_mass_res / mll")

        df = df.Define("ptj1", "Jet_pt.size() > 0 ? Jet_pt[0] : -999")
        df = df.Define("ptj2", "Jet_pt.size() > 1 ? Jet_pt[1] : -999")
        df = df.Define("etaj1", "Jet_pt.size() > 0 ? Jet_eta[0] : -999")
        df = df.Define("etaj2", "Jet_pt.size() > 1 ? Jet_eta[1] : -999")
        df = df.Define("njet", "Jet_pt.size()")

        df = df.Define(
            "j1_p4",
            "Jet_pt.size() > 0 ? ROOT::Math::PtEtaPhiMVector(Jet_pt[0], Jet_eta[0], Jet_phi[0], Jet_mass[0]) : ROOT::Math::PtEtaPhiMVector(0, 0, 0, 0)",
        )
        df = df.Define(
            "j2_p4",
            "Jet_pt.size() > 1 ? ROOT::Math::PtEtaPhiMVector(Jet_pt[1], Jet_eta[1], Jet_phi[1], Jet_mass[1]) : ROOT::Math::PtEtaPhiMVector(0, 0, 0, 0)",
        )

        df = df.Define("mjj", "Jet_pt.size() > 1 ? (j1_p4 + j2_p4).M() : -999")
        df = df.Define("ptjj", "Jet_pt.size() > 1 ? (j1_p4 + j2_p4).Pt() : -999")
        df = df.Define(
            "detajj", "Jet_pt.size() > 1 ? abs(j1_p4.Eta() - j2_p4.Eta()) : -999"
        )
        df = df.Define(
            "dphijj",
            "Jet_pt.size() > 1 ? ROOT::Math::VectorUtil::DeltaPhi(j1_p4, j2_p4) : -999",
        )

        df = df.Define("Jet_btag", "Jet_btagPNetB >= 0.1917 && abs(Jet_eta) < 2.5")
        df = df.Define("bveto", "Sum(Jet_btag) == 0")

        df = run_cs_variables(df)

        if is_dy and apply_ptll:
            # df = df.Define(
            #     "weight_ptll_rwgt",
            #     "ptll_rwgt->evaluate({ptll})",
            # )
            df = df.Define(
                "weight_ptll_rwgt",
                # "ptll_rwgt->evaluate({std::min((int) njet, 2), std::min((float) ptll, 199.9f)})",
                'ptll_rwgt->evaluate({is_vbf ? "VBF" : "ggF", (int) njet, std::min((float) ptll, 199.9f)})',
            )
            df = df.Define(
                "weight_njet_rwgt",
                "njet_rwgt->evaluate({(float)njet})",
            )
            df = df.Redefine("weight", "weight * weight_ptll_rwgt * weight_njet_rwgt")

        results = {}
        results["sumw"] = df.Sum("weight")

        for region in regions:
            mask = regions[region]["mask"]
            df = df.Define(region, mask)

        for region in regions:
            if regions[region].get("skip_fill", False):
                continue
            df_region = df.Filter(region)
            if not do_snapshot:
                for var in variables:
                    axis = variables[var]["axis"]
                    var_for_fill = variables[var].get("variable", var)
                    if isinstance(var_for_fill, str):
                        hist = df_region.Histo1D(
                            (f"histo_{var}", f"histo_{var}", *axis),
                            var_for_fill,
                            "weight",
                        )
                    else:
                        hist = df_region.Histo2D(
                            (f"histo_{var}", f"histo_{var}", *axis),
                            *var_for_fill,
                            "weight",
                        )
                    results[f"{region}/{var}"] = hist
            else:
                opts = ROOT.RDF.RSnapshotOptions()
                opts.fLazy = True
                vars_to_save = ["weight"]
                for var in variables:
                    var_for_fill = variables[var].get("variable", var)
                    vars_to_save.append(var_for_fill)
                vars_to_save = list(set(vars_to_save))
                results[region] = df_region.Snapshot(
                    "Events",
                    f"ntuples/{dataset}_{region}.root",
                    vars_to_save,
                    opts,
                )

        return results

    results_datasets = {}
    for ds in specs:
        print(f"Processing dataset {ds}...")
        results_datasets[ds] = process_dataset(specs[ds])
    ROOT.RDF.RunGraphs(
        [h for results in results_datasets.values() for h in results.values()]
    )
    print("done!")

    if not do_snapshot:
        integrals = {}
        for ds in results_datasets:
            print(f"Dataset: {ds}")
            sumw = results_datasets[ds]["sumw"].GetValue()
            print("Integral:", sumw)
            integrals[ds] = sumw

        filename = f"roots/{year}"
        if not apply_ptll:
            filename = f"roots/{year}_extract_ptll"

        with open(f"{filename}_integrals.json", "w") as f:
            json.dump(integrals, f, indent=4)

        fout = ROOT.TFile(f"{filename}.root", "RECREATE")

        for var in results_datasets[ds]:
            if var == "sumw":
                continue
            fout.mkdir(var)
            fout.cd(var)
            for ds in results_datasets:
                hist = results_datasets[ds][var]
                hist.Write(f"histo_{ds}")
        fout.Close()

        # df.Display({"weight"}, 10).Print()
