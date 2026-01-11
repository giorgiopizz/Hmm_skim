import ROOT
import time

import json
import correctionlib
import subprocess
import os

correctionlib.register_pyroot_binding()

ROOT.gROOT.SetBatch(True)

# ROOT.EnableImplicitMT(True)


def load_cpp_utils(data_folder):
    line = """
    #include "DATAFOLDER/trig_match.cpp"
    #include "DATAFOLDER/lumi.h"

    auto cset = correction::CorrectionSet::from_file("FILENAME");
    auto puweight = cset->at("JSONNAME");

    float getWeight(float Pileup_nTrueInt) {
    return puweight->evaluate({Pileup_nTrueInt, "nominal"});
    }

    auto lumi_filter = LumiFilter("DATAFOLDER/Cert_Collisions2024_378981_386951_Golden.json");

    """

    line = (
        line.replace("FILENAME", f"{data_folder}/puWeights_BCDEFGHI.json.gz")
        .replace("JSONNAME", "Collisions24_BCDEFGHI_goldenJSON")
        .replace("DATAFOLDER", data_folder)
    )
    ROOT.gInterpreter.Declare(line)


# exit(0)


def process_file(dataset, file, outfile, is_data):
    df = ROOT.RDataFrame("Events", file)
    if not is_data:
        sumw = df.Sum("genWeight")
    else:
        sumw = df.Define("genWeight", "1").Sum("genWeight")
    nevents = df.Count()
    df = df.Define(
        "good_ele",
        "Electron_pt > 20 && abs(Electron_eta) < 2.5 && Electron_mvaIso_WP90",
    )
    df = df.Filter("Electron_pt[good_ele].size() == 0")

    df = df.Define(
        "good_mu",
        "Muon_pt > 15 && abs(Muon_eta) < 2.4 && Muon_mediumId && Muon_pfIsoId >= 3",
    )
    df = df.Filter("Muon_pt[good_mu].size() == 2")

    df = df.Filter("HLT_IsoMu24")

    if is_data:
        df = df.Filter("lumi_filter.Pass(run, luminosityBlock)")

    mu_cols = [
        "pt",
        "ptErr",
        "bsConstrainedPt",
        "bsConstrainedPtErr",
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
    df = df.Filter("mll > 50 && mll < 170")

    df = df.Define("TrigObj_mask", "TrigObj_id == 13 && (TrigObj_filterBits&8)!=0")

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

    if not is_data:
        df = df.Define(
            "pu_weight",
            "getWeight(Pileup_nTrueInt)",
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
            "pu_weight",
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

    columns += [f"mu{idx}_{col}" for col in mu_cols for idx in [1, 2]]

    jet_cols = [
        "pt",
        "eta",
        "phi",
        "mass",
        "btagPNetB",
        "chHEF",
        "neHEF",
        "chEmEF",
        "neEmEF",
        "muEF",
        "chMultiplicity",
        "neMultiplicity",
        "area",
        "rawFactor",
    ]

    columns += [f"Jet_{col}" for col in jet_cols]

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


data_folder = "data/"
job_folder = "."

# # FIXME comment
# data_folder = "../data/"
# job_folder = "../condor_jobs/job_217/"

with open(f"{job_folder}/input.json") as f:
    data = json.load(f)

out_tmp = data["outfile"]
if "/eos/" in data["outfile"]:
    out_tmp = "output.root"

load_cpp_utils(data_folder)
result = process_file(data["dataset"], data["file"][:], out_tmp, data["is_data"])

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
