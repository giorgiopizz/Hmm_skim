import ROOT
import time

import json
import correctionlib
import subprocess
import os
import sys

correctionlib.register_pyroot_binding()

ROOT.gROOT.SetBatch(True)

# ROOT.EnableImplicitMT(True)

data_folder = "data/"
job_folder = "."
run_systematics = True
run_systematics = False

# # # FIXME comment out
data_folder = "../data/"
# job_folder = "../condor_jobs/job_20/"
# # job_folder = "../condor_jobs/job_11/"
job_folder = "../condor_jobs/job_0/"


def load_cpp_utils(data_folder):
    line = """
    #include "DATAFOLDER/modules/trig_match.cpp"
    #include "DATAFOLDER/modules/lumi.h"

    auto cset_pu = correction::CorrectionSet::from_file("FILENAME");
    auto ceval_pu = cset_pu->at("JSONNAME");

    auto lumi_filter = LumiFilter("DATAFOLDER/2024/Cert_Collisions2024_378981_386951_Golden.json");

    """

    line = (
        line.replace("FILENAME", f"{data_folder}/2024/puWeights_BCDEFGHI.json.gz")
        .replace("JSONNAME", "Collisions24_BCDEFGHI_goldenJSON")
        .replace("DATAFOLDER", data_folder)
    )
    ROOT.gInterpreter.Declare(line)


load_cpp_utils(data_folder)
sys.path.append(data_folder)
from modules.muon_sf import run_muon_sf, load_cpp_utils as load_muon_sf_utils  # noqa: E402
from modules.jet_id_veto import run_jetid_veto, load_cpp_utils as load_jet_id_utils  # noqa: E402
from modules.jet_correction import (
    run_jme_mc,
    run_jme_data,
    load_cpp_utils as load_jec_utils,
)  # noqa: E402
from modules.noise_filters import run_noise_filters  # noqa: E402

# exit(0)


def process_file(dataset, file, outfile, is_data):
    load_muon_sf_utils(data_folder, is_data=is_data)
    load_jec_utils(data_folder, is_data=is_data)
    load_jet_id_utils(data_folder)

    df = ROOT.RDataFrame("Events", file)
    # # FIXME DEBUG
    # df = df.Range(1000)

    if not is_data:
        sumw = df.Sum("genWeight")
    else:
        sumw = df.Define("genWeight", "1").Sum("genWeight")
    nevents = df.Count()

    df = run_noise_filters(df, is_data=is_data)
    df = df.Filter("good_event")

    df = df.Define(
        "good_ele",
        "Electron_pt > 20 && abs(Electron_eta) < 2.5 && Electron_mvaIso_WP90",
    )
    df = df.Filter("Electron_pt[good_ele].size() == 0")

    # use always BS pt
    df = df.Define("Muon_pt_no_bs", "Muon_pt")
    df = df.Define("Muon_ptErr_no_bs", "Muon_ptErr")
    df = df.Redefine("Muon_pt", "Muon_bsConstrainedPt")
    df = df.Redefine("Muon_ptErr", "Muon_bsConstrainedPtErr")

    # pfIsoId >= 2 : Loose
    df = df.Define(
        "good_mu",
        "Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_tightId && Muon_pfIsoId >= 4",  # FIXME
    )

    df = df.Filter("Muon_pt[good_mu].size() == 2")

    df = df.Filter("HLT_IsoMu24")

    if is_data:
        df = df.Filter("lumi_filter.Pass(run, luminosityBlock)")

    mu_cols = [
        "pt",
        "ptErr",
        # "bsConstrainedPt",
        # "bsConstrainedPtErr",
        "pt_no_bs",
        "ptErr_no_bs",
        "eta",
        "phi",
        "mass",
        "pdgId",
        "charge",
        "tightId",
        "mediumId",
        "dxy",
        "dz",
        "pfRelIso03_all",
        "pfRelIso04_all",
        "pfIsoId",
        "nTrackerLayers",
        "fsrPhotonIdx",
    ]

    df = df.Define(
        # "muon_order", "Argsort(Muon_pt[good_mu], [](double x, double y) {return x > y;})"
        "muon_order",
        "Argsort(Muon_pt[good_mu])",
    )
    for col in mu_cols:
        df = df.Define(f"mu1_{col}", f"Take(Muon_{col}[good_mu], muon_order)[1]")
        df = df.Define(f"mu2_{col}", f"Take(Muon_{col}[good_mu], muon_order)[0]")

    df = df.Define(
        "mu1_p4", "ROOT::Math::PtEtaPhiMVector(mu1_pt, mu1_eta, mu1_phi, mu1_mass)"
    )
    df = df.Define(
        "mu2_p4", "ROOT::Math::PtEtaPhiMVector(mu2_pt, mu2_eta, mu2_phi, mu2_mass)"
    )
    df = df.Define("mll", "(mu1_p4 + mu2_p4).M()")
    df = df.Filter("mll > 50 && mll < 200")

    df = run_muon_sf(df, is_data, run_syst=run_systematics)
    mu_cols += ["pt_no_corr"]
    if not is_data and run_systematics:
        mu_cols += [
            f"pt_{var}_{tag}" for var in ["scale", "res"] for tag in ["up", "down"]
        ]

    df = df.Define("TrigObj_mask", "TrigObj_id == 13 && (TrigObj_filterBits & 8) != 0")

    df = df.Define(
        "TrigObj_p4",
        "Construct<ROOT::Math::PtEtaPhiMVector>(TrigObj_pt, TrigObj_eta, TrigObj_phi, ROOT::RVecF(TrigObj_pt.size(), 0.))",
    )
    df = df.Redefine("TrigObj_p4", "TrigObj_p4[TrigObj_mask]")

    df = df.Define(
        "mu1_HasMatching_singleMu", "FindMatching(mu1_p4, TrigObj_p4, 0.4) > -1"
    )
    df = df.Define(
        "mu2_HasMatching_singleMu", "FindMatching(mu2_p4, TrigObj_p4, 0.4) > -1"
    )
    mu_cols += ["HasMatching_singleMu"]

    # df = run_jetid_veto(df)
    # if is_data:
    #     df = run_jme_data(df)
    # else:
    #     df = run_jme_mc(df, run_syst=run_systematics)

    if not is_data:
        df = df.Define(
            "weight_sf_pu",
            'ceval_pu->evaluate({Pileup_nTrueInt, "nominal"})',
        )
        if run_systematics:
            df = df.Define(
                "weight_sf_pu_up",
                'ceval_pu->evaluate({Pileup_nTrueInt, "up"})',
            )
            df = df.Define(
                "weight_sf_pu_down",
                'ceval_pu->evaluate({Pileup_nTrueInt, "down"})',
            )

    columns = [
        "event",
        "luminosityBlock",
        "run",
        "Rho_fixedGridRhoFastjetAll",
        "PV_npvs",
    ]
    if not is_data:
        columns += [
            "genWeight",
            # theory weights
            "LHEScaleWeight",
            "LHEPdfWeight",
            "PSWeight",
            # gen part
            "GenPart_pt",
            "GenPart_eta",
            "GenPart_phi",
            "GenPart_mass",
            "GenPart_pdgId",
            "GenPart_status",
            "GenPart_statusFlags",
            # gen jet
            "GenJet_pt",
            "GenJet_eta",
            "GenJet_phi",
            "GenJet_mass",
            "Jet_genJetIdx",
            "Jet_hadronFlavour",
        ]

        columns += ["weight_sf_pu"]
        if run_systematics:
            columns += ["weight_sf_pu_up", "weight_sf_pu_down"]

        # muon SFs
        if not run_systematics:
            for mu_idx in [1, 2]:
                columns += [
                    f"weight_sf_mu{mu_idx}_id",
                    f"weight_sf_mu{mu_idx}_iso",
                    f"weight_sf_mu{mu_idx}_trg",
                ]
        else:
            for mu_idx in [1, 2]:
                columns += [
                    f"weight_sf_mu{mu_idx}_id",
                    f"weight_sf_mu{mu_idx}_id_up",
                    f"weight_sf_mu{mu_idx}_id_down",
                    f"weight_sf_mu{mu_idx}_iso",
                    f"weight_sf_mu{mu_idx}_iso_up",
                    f"weight_sf_mu{mu_idx}_iso_down",
                    f"weight_sf_mu{mu_idx}_trg",
                    f"weight_sf_mu{mu_idx}_trg_up",
                    f"weight_sf_mu{mu_idx}_trg_down",
                ]

    columns += [f"mu{idx}_{col}" for col in mu_cols for idx in [1, 2]]

    jet_cols = [
        "pt",
        "eta",
        "phi",
        "mass",
        "btagPNetB",
        "btagPNetCvL",
        "btagPNetQvG",
        "chHEF",
        "neHEF",
        "chEmEF",
        "neEmEF",
        "muEF",
        "chMultiplicity",
        "neMultiplicity",
        "area",
        "rawFactor",
        # FIXME
        # "tightId",
        # "tightLepVetoId",
        # "veto_map",
        # "veto",
    ]

    # jet_cols += [
    #     "pt_no_corr",
    #     "mass_no_corr",
    # ]
    # if not is_data:
    #     jet_cols += [
    #         "pt_jec",
    #         "mass_jec",
    #     ]
    #     if run_systematics:
    #         # unc
    #         jet_cols += [
    #             "pt_jer_down",
    #             "mass_jer_down",
    #             "pt_jer_up",
    #             "mass_jer_up",
    #             "pt_jes_down",
    #             "mass_jes_down",
    #             "pt_jes_up",
    #             "mass_jes_up",
    #         ]

    if year == "2024":
        jet_cols += ["btagUParTAK4B"]

    columns += [f"Jet_{col}" for col in jet_cols]

    softActivity_cols = [
        "SoftActivityJetHT",
        "SoftActivityJetHT2",
        "SoftActivityJetHT5",
    ]

    columns += softActivity_cols

    nevents_after = df.Count()

    opts = ROOT.RDF.RSnapshotOptions()
    # opts.fLazy = True
    df.Snapshot("Events", outfile, columns, opts)

    sumw = sumw.GetValue()
    nevents = nevents.GetValue()
    nevents_after = nevents_after.GetValue()
    values = {
        "sumw": sumw,
        "nevents_before": nevents,
        "nevents_after": nevents_after,
        "files": [
            {
                "file": outfile,
                "nevents": nevents_after,
            }
        ],
    }
    return {dataset: values}


with open(f"{job_folder}/input.json") as f:
    data = json.load(f)

year = "2024"

out_tmp = data["outfile"]
if "/eos/" in data["outfile"]:
    out_tmp = "output.root"

result = process_file(data["dataset"], data["file"][:2], out_tmp, data["is_data"])

# if "/eos/" in data["outfile"]:
#     cmd = f"xrdcp {out_tmp} root://eosuser.cern.ch/{data['outfile']}"
#     # run cmd, if any error, remove output.root and raise exception
#     proc = subprocess.run(cmd, shell=True)
#     if proc.returncode != 0:
#         os.remove(out_tmp)
#         raise RuntimeError(f"Failed to copy output file: {cmd}")

# os.remove(out_tmp)

# with open(f"{job_folder}/output.json", "w") as f:
#     json.dump(result, f, indent=2)
