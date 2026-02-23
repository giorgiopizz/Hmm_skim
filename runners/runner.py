import ROOT
import time

import argparse
import json
import correctionlib
import subprocess
import os
import sys

correctionlib.register_pyroot_binding()

ROOT.gROOT.SetBatch(True)


argparsese = argparse.ArgumentParser()
argparsese.add_argument(
    "--year", type=str, required=True, help="Year of the production"
)
argparsese.add_argument(
    "--debug", action="store_true", help="Run in debug mode (process only one file)"
)


args = argparsese.parse_args()
year = args.year
DEBUG = args.debug

data_folder = "data/"
module_folder = "modules/"
job_folder = "."
run_systematics = True
run_systematics = False

if DEBUG:
    tag = "v1"
    # # # FIXME comment out
    data_folder = "../data/"
    module_folder = "../modules/"
    condor_folder = f"../condor_jobs/{tag}_{year}/"
    job_folder = f"{condor_folder}/job_20/"
    # # job_folder = "../condor_jobs/job_11/"
    # job_folder = "../condor_jobs/job_0/"
    job_folder = f"{condor_folder}/job_95/"


sys.path.append(data_folder)
from modules.pu import load_cpp_utils as load_pu_utils  # noqa: E402
from modules.muon_sf import (
    run_muon_sf,
    run_muon_scare,
    load_cpp_utils as load_muon_sf_utils,
)  # noqa: E402
from modules.jet_id_veto import run_jetid_veto, load_cpp_utils as load_jet_id_utils  # noqa: E402
from modules.jet_correction import (
    run_jme_mc,
    run_jme_data,
    load_cpp_utils as load_jec_utils,
)
from modules.noise_filters import run_noise_filters  # noqa: E402
from modules.btag import run_btag  # noqa: E402
from modules.vbf_selector import (
    run_vbf_selector,
    load_cpp_utils as load_vbf_selector_utils,
)  # noqa: E402
from modules.fsr_recovery import (
    run_fsr_recovery,
    load_cpp_utils as load_fsr_recovery_utils,
)  # noqa: E402


def process_file(dataset, file, outfile, is_data):

    load_pu_utils(module_folder, data_folder, year)
    load_muon_sf_utils(module_folder, data_folder, year, is_data=is_data)
    load_jet_id_utils(module_folder, data_folder, year, is_data=is_data)
    load_jec_utils(module_folder, data_folder, year, is_data=is_data)
    load_vbf_selector_utils(module_folder, data_folder, year, is_data=is_data)
    load_fsr_recovery_utils(module_folder)

    # exit()

    df = ROOT.RDataFrame("Events", file)

    if not is_data:
        sumw = df.Sum("genWeight")
    else:
        sumw = df.Define("genWeight", "1").Sum("genWeight")
    nevents = df.Count()

    # Noise filters
    df = run_noise_filters(df, is_data=is_data)
    df = df.Filter("good_event")

    # Pass trigger
    df = df.Filter("HLT_IsoMu24")

    # good lumi
    if is_data:
        df = df.Filter("lumi_filter.Pass(run, luminosityBlock)")

    columns = [
        "event",
        "luminosityBlock",
        "run",
        "Rho_fixedGridRhoFastjetAll",
        "PV_npvs",
        "PV_npvsGood",
    ]

    # Electron veto
    df = df.Define(
        "good_ele",
        "Electron_pt > 20 && abs(Electron_eta) < 2.5 && Electron_mvaIso_WP90",
    )
    df = df.Filter("Electron_pt[good_ele].size() == 0")

    # use always BS pt
    df = df.Redefine("Muon_pt", "Muon_bsConstrainedPt")
    df = df.Redefine("Muon_ptErr", "Muon_bsConstrainedPtErr")
    df = df.Define("Muon_pt_no_bs", "Muon_pt")
    df = df.Define("Muon_ptErr_no_bs", "Muon_ptErr")

    # pfIsoId >= 2 : Loose
    df = df.Define(
        "good_mu",
        "Muon_pt > 10 && abs(Muon_eta) < 2.4 && Muon_mediumId && Muon_pfIsoId >= 2",  # FIXME
    )

    df = df.Filter("Muon_pt[good_mu].size() == 2")

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
        "Muon_order",
        "Reverse(Argsort(Muon_pt[good_mu]))",
    )
    for col in mu_cols:
        df = df.Define(f"mu1_{col}", f"Take(Muon_{col}[good_mu], Muon_order)[0]")
        df = df.Define(f"mu2_{col}", f"Take(Muon_{col}[good_mu], Muon_order)[1]")

    # OS
    df = df.Filter("mu1_charge != mu2_charge")

    # Filter trigger matched
    df = df.Define(
        "mu1_trigger_idx",
        "trg_match_ind(mu1_eta, mu1_phi, TrigObj_id, TrigObj_eta, TrigObj_phi, -99)",
    )
    df = df.Define(
        "mu2_trigger_idx",
        "trg_match_ind(mu2_eta, mu2_phi, TrigObj_id, TrigObj_eta, TrigObj_phi, mu1_trigger_idx)",
    )
    # mu_cols += ["trigger_idx"]
    df = df.Define(
        "mu_trigger_idx", "mu1_pt > mu2_pt ? mu1_trigger_idx : mu2_trigger_idx"
    )
    df = df.Filter("mu_trigger_idx >= 0")

    df = run_muon_sf(df, year, is_data=is_data, run_syst=run_systematics)

    if not is_data:
        df = df.Define(
            "weight_trigger_SF",
            "mu_trigger_idx == mu1_trigger_idx ? weight_sf_mu1_trg : weight_sf_mu2_trg",
        )

    # apply ScaRe
    df = run_muon_scare(df, is_data, run_syst=run_systematics)
    mu_cols += ["pt_no_corr"]
    df = df.Define("Muon_pt_no_corr", "Muon_pt")

    if not is_data and run_systematics:
        mu_cols += [
            f"pt_{var}_{tag}" for var in ["scale", "res"] for tag in ["up", "down"]
        ]

    # FIXME will need to run also on variations of mu_pt
    df = run_fsr_recovery(df)
    mu_cols += [f"{var}_no_fsr" for var in ["pt", "eta", "phi", "mass"]] + [
        "is_fsr_recovered"
    ]
    for var in ["pt", "eta", "phi", "mass"]:
        df = df.Define(f"Muon_{var}_no_fsr", f"Muon_{var}")
    df = df.Define("Muon_is_fsr_recovered", "RVecB(Muon_pt.size(), false)")

    # resort the muons
    for col in mu_cols:
        T = df.GetColumnType(f"mu1_{col}")
        df = df.Redefine(
            f"Muon_{col}", f"ROOT::VecOps::RVec<{T}> {{mu1_{col}, mu2_{col}}}"
        )

    df = df.Redefine("Muon_order", "Reverse(Argsort(Muon_pt))")
    for col in mu_cols:
        df = df.Redefine(f"mu1_{col}", f"Take(Muon_{col}, Muon_order)[0]")
        df = df.Redefine(f"mu2_{col}", f"Take(Muon_{col}, Muon_order)[1]")

    df = df.Define(
        "mu1_p4", "ROOT::Math::PtEtaPhiMVector(mu1_pt, mu1_eta, mu1_phi, mu1_mass)"
    )
    df = df.Define(
        "mu2_p4", "ROOT::Math::PtEtaPhiMVector(mu2_pt, mu2_eta, mu2_phi, mu2_mass)"
    )
    df = df.Define("mll", "(mu1_p4 + mu2_p4).M()")
    df = df.Filter("mll > 50 && mll < 200")

    df = run_jetid_veto(df, year)

    # filter out events with one jet in the veto region
    df = df.Filter("Sum(Jet_veto) == 0")

    if is_data:
        df = run_jme_data(df, year)
    else:
        df = run_jme_mc(df, year, run_syst=run_systematics)

    df = df.Define(
        "Jet_in_horn",
        "(abs(Jet_eta) >= 2.5) && (abs(Jet_eta) < 3.0)",
    )
    df = df.Define(
        "Jet_in_HF",
        "(abs(Jet_eta) >= 3.0) && (abs(Jet_eta) < 5.0)",
    )

    if year == "2024":
        df = df.Define(
            "Jet_bad",
            "(Jet_pt < 50) && Jet_in_horn",
        )
    else:
        df = df.Define(
            "Jet_bad",
            "(Jet_pt < 50) && (Jet_in_horn || Jet_in_HF)",
        )

    df = df.Define("Jet_good", "Jet_pt > 25 && Jet_tightId && !Jet_veto_or_overlap && !Jet_bad")

    jet_cols = [
        "pt",
        "eta",
        "phi",
        "mass",
        "btagPNetB",
        "btagPNetCvL",
        "btagPNetQvG",
    ]
    if year == "2024":
        jet_cols += ["btagUParTAK4B"]
    if not is_data:
        jet_cols += [
            "genJetIdx",
            "hadronFlavour",
        ]

    jet_cols += [
        "pt_no_corr",
        "mass_no_corr",
    ]
    if not is_data:
        jet_cols += [
            "pt_jec",
            "mass_jec",
        ]
        if run_systematics:
            # unc
            jet_cols += [
                "pt_jer_down",
                "mass_jer_down",
                "pt_jer_up",
                "mass_jer_up",
                "pt_jes_down",
                "mass_jes_down",
                "pt_jes_up",
                "mass_jes_up",
            ]

    df = df.Define("Jet_order", "Reverse(Argsort(Jet_pt[Jet_good]))")
    for col in jet_cols:
        df = df.Redefine(f"Jet_{col}", f"Take(Jet_{col}[Jet_good], Jet_order)")

    df = run_vbf_selector(df, year)
    columns += ["vbf_jet_idx1", "vbf_jet_idx2", "vbf_mjj", "vbf_detajj"]

    df = run_btag(df, year)
    jet_cols += ["btag_M"]

    # # filter btagged jets
    # df = df.Filter("Sum(Jet_btagged) == 0")

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

    if not is_data:
        columns += [
            "genWeight",
            # # theory weights
            # "LHEScaleWeight",
            # "LHEPdfWeight",
            # "PSWeight",
            # # gen part
            # "GenPart_pt",
            # "GenPart_eta",
            # "GenPart_phi",
            # "GenPart_mass",
            # "GenPart_pdgId",
            # "GenPart_status",
            # "GenPart_statusFlags",
            # # gen jet
            # "GenJet_pt",
            # "GenJet_eta",
            # "GenJet_phi",
            # "GenJet_mass",
        ]

        columns += ["weight_sf_pu"]
        columns += ["weight_trigger_SF"]
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
        "is_data": is_data,
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


out_tmp = data["outfile"]
if "/eos/" in data["outfile"]:
    out_tmp = "output.root"

if not DEBUG:
    result = process_file(data["dataset"], data["file"][:], out_tmp, data["is_data"])
else:
    result = process_file(data["dataset"], data["file"][:1], out_tmp, data["is_data"])

if not DEBUG:
    if "/eos/" in data["outfile"]:
        cmd = f"xrdcp {out_tmp} root://eosuser.cern.ch/{data['outfile']}"
        # run cmd, if any error, remove output.root and raise exception
        proc = subprocess.run(cmd, shell=True)
        if proc.returncode != 0:
            os.remove(out_tmp)
            raise RuntimeError(f"Failed to copy output file: {cmd}")

    os.remove(out_tmp)

    with open(f"{job_folder}/output.json", "w") as f:
        json.dump(result, f, indent=2)
