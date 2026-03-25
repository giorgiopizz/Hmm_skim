from utils.utils import cmap_pastel, cmap_petroff

datasets = {}

datasets["data"] = {
    "names": [],
    "is_data": True,
}
for ds in ["Muon0", "Muon1"]:
    datasets["data"]["names"].extend(
        [
            f"{ds}_Run2024C_v1",
            f"{ds}_Run2024D_v1",
            f"{ds}_Run2024E_v1",
            f"{ds}_Run2024F_v1",
            f"{ds}_Run2024G_v1",
            f"{ds}_Run2024H_v1",
            f"{ds}_Run2024I_v1",
            f"{ds}_Run2024I_v2",
        ]
    )

datasets["WJets"] = {
    "names": [
        "WToENu_amcatnloFXFX",
        "WToMuNu_amcatnloFXFX",
        "WToTauNu_amcatnloFXFX",
    ],
    "color": cmap_petroff[5],
}


datasets["VV"] = {
    "names": [
        # WW
        "WWto2L2Nu_powheg",
        "WWto4Q_powheg",
        "WWtoLNu2Q_powheg",
        # WZ
        "WZto3LNu_powheg",
        "WZto2L2Q_powheg",
        "WZtoLNu2Q_powheg",
        # WZto4Q?
        # ZZ
        "ZZto2L2Nu_powheg",
        "ZZto2L2Q_powheg",
        "ZZto2Nu2Q_powheg",
        "ZZto4L_powheg",
        # ZZto4Q?
    ],
    "color": cmap_petroff[3],
}

datasets["Top"] = {
    "names": [
        # TTbar
        "TTto2L2Nu",
        "TTtoLNu2Q",
        "TTto4Q",
        # # TW
        # "TWminusto2L2Nu",
        # "TbarWplusto2L2Nu",
        # "TWminustoLNu2Q",
        # "TbarWplustoLNu2Q",
        # "TWminusto4Q",
        # "TbarWplusto4Q",
        # # Single top
        # "TbarBtoLminusNuB_s_channel_4FS",
        # "TBbartoLplusNuBbar_s_channel_4FS",
        # "TbarBQtoLNu_t_channel_4FS",
        # "TbarBQto2Q_t_channel_4FS",
        # "TBbarQtoLNu_t_channel_4FS",
        # "TBbarQto2Q_t_channel_4FS",
    ],
    "color": cmap_petroff[1],
}

# datasets["EWK_Z"] = {
#     "names": [
#         "EWK_2L2J_madgraph_herwig",
#     ],
#     "color": cmap_petroff[4],
# }

# datasets["ttH"] = {
#     "names": [
#         "TTHto2Mu",
#     ],
#     "is_signal": True,
#     "color": cmap_pastel[3],
# }

# datasets["VH"] = {
#     "names": [
#         "WplusHto2Mu",
#         "WminusHto2Mu",
#         "ZHto2Mu",
#     ],
#     "is_signal": True,
#     "color": cmap_pastel[2],
# }

datasets["VBF_H"] = {
    "names": [
        "VBFHto2Mu",
    ],
    "is_signal": True,
    "color": cmap_pastel[0],
}

datasets["ggF_H"] = {
    "names": [
        "GluGluHto2Mu",
    ],
    "is_signal": True,
    "color": cmap_pastel[1],
}

datasets["DY"] = {
    "names": [
        # Inclusive
        "DYto2E_M_50_amcatnloFXFX",
        "DYto2Mu_M_50_amcatnloFXFX",
        "DYto2Tau_M_50_amcatnloFXFX",
        # # Jet binned
        # # e
        # "DYto2E_M_50_0J_amcatnloFXFX",
        # "DYto2E_M_50_1J_amcatnloFXFX",
        # "DYto2E_M_50_2J_amcatnloFXFX",
        # # mu
        # "DYto2Mu_M_50_0J_amcatnloFXFX",
        # "DYto2Mu_M_50_1J_amcatnloFXFX",
        # "DYto2Mu_M_50_2J_amcatnloFXFX",
        # # tau
        # "DYto2Tau_M_50_0J_amcatnloFXFX",
        # "DYto2Tau_M_50_1J_amcatnloFXFX",
        # "DYto2Tau_M_50_2J_amcatnloFXFX",
    ],
    "color": cmap_petroff[0],
}
