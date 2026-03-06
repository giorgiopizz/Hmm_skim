import json
import gzip
import correctionlib

f1 = "ScaleFactors_Muon_ID_ISO_2025_schemaV2.json"
with open(f1) as file:
    d1 = json.load(file)

f2 = "ScaleFactors_Muon_Z_HLT_2025_eta_pt_schemaV2.json"
with open(f2) as file:
    d2 = json.load(file)

for correction in d2["corrections"]:
    if correction["name"] == "NUM_IsoMu24_DEN_CutBasedIdMedium_and_PFIsoMedium":
        d1["corrections"].append(correction)
        break

with gzip.open("muon_Z.json.gz", "wt") as file:
    json.dump(d1, file)

ceval_trg = correctionlib.CorrectionSet.from_file("muon_Z.json.gz")[
    "NUM_IsoMu24_DEN_CutBasedIdMedium_and_PFIsoMedium"
]

ceval_id = correctionlib.CorrectionSet.from_file("muon_Z.json.gz")[
    "NUM_MediumID_DEN_TrackerMuons"
]


ceval_trg.evaluate(2.3, 26.0, "nominal")
ceval_id.evaluate(2.3, 26.0, "nominal")
