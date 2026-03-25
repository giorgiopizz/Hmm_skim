from array import array
from utils.utils import parse_samples_datasets


def get_config(year, apply_ptll):
    datasets = {}
    datasets["data"] = {
        "names": [],
        "is_data": True,
    }
    if year == "2025":
        datasets, _ = parse_samples_datasets(year)
        tag = "v3"
        base_folder = f"/eos/user/g/gpizzati/hmm_skim/{tag}/{year}"
        base_folder = f"/home/gpizzati/ntuples/{tag}/{year}"

    if year == "2024":
        datasets, _ = parse_samples_datasets(year)
        # tag = "v1"
        tag = "v3"
        base_folder = f"/eos/user/g/gpizzati/hmm_skim/{tag}/{year}"
        base_folder = f"/home/gpizzati/ntuples/{tag}/{year}"

    if year == "2023":
        datasets, _ = parse_samples_datasets(year)
        tag = "v2"
        base_folder = f"/eos/user/g/gpizzati/hmm_skim/{tag}/{year}"

    if year == "2022EE":
        for ds in ["Muon"]:
            datasets["data"]["names"].extend(
                [
                    f"{ds}_Run2022E_v1",
                    f"{ds}_Run2022F_v1",
                    f"{ds}_Run2022G_v1",
                ]
            )

        datasets["WJets"] = {
            "names": [
                # "WToLNu_amcatnloFXFX",
                "WToLNu_0J_amcatnloFXFX",
                "WToLNu_1J_amcatnloFXFX",
                "WToLNu_2J_amcatnloFXFX",
            ],
            "color": cmap_petroff[5],
        }

        # datasets["TW"] = {
        #     "names": [
        #         "TWminusto2L2Nu",
        #         "TbarWplusto2L2Nu",
        #         "TWminustoLNu2Q",
        #         "TbarWplustoLNu2Q",
        #         "TWminusto4Q",
        #         "TbarWplusto4Q",
        #     ],
        #     "color": cmap_petroff[2],
        # }

        # datasets["TTbar"] = {
        #     "names": [
        #         "TTto2L2Nu",
        #         "TTtoLNu2Q",
        #         "TTto4Q",
        #     ],
        #     "color": cmap_petroff[1],
        # }

        # datasets["VV"] = {
        #     "names": [
        #         "WWto2L2Nu_powheg",
        #         "WWto4Q_powheg",
        #         "WWtoLNu2Q_powheg",
        #         "WZto3LNu_powheg",
        #         "WZto2L2Q_powheg",
        #         "WZtoLNu2Q_powheg",
        #         "ZZto2L2Nu_powheg",
        #         "ZZto2L2Q_powheg",
        #         "ZZto2Nu2Q_powheg",
        #         "ZZto4L_powheg",
        #     ],
        #     "color": cmap_petroff[3],
        # }

        # datasets["EWKZ"] = {
        #     "names": [
        #         "EWK_2L2J_madgraph_herwig",
        #     ],
        #     "color": cmap_petroff[4],
        # }

        datasets["VBFHto2Mu"] = {
            "names": [
                "VBFHto2Mu",
            ],
            "is_signal": True,
            "color": cmap_pastel[0],
        }

        datasets["ggHto2Mu"] = {
            "names": [
                "GluGluHto2Mu",
            ],
            "is_signal": True,
            "color": cmap_pastel[1],
        }

        datasets["DY"] = {
            "names": [
                "DYto2L_M_50_0J_amcatnloFXFX",
                "DYto2L_M_50_1J_amcatnloFXFX",
                "DYto2L_M_50_2J_amcatnloFXFX",
            ],
            "color": cmap_petroff[0],
        }

    variables = {}
    variables["ptl1"] = {
        "axis": (100, 26, 200),
        # "axis": (20, 26, 200),
        "xlabel": "$p^T_{\\mu1}$ [GeV]",
    }
    variables["ptl2"] = {
        "axis": (100, 15, 150),
        "xlabel": "$p^T_{\\mu2}$ [GeV]",
    }
    variables["etal1"] = {
        "axis": (100, -2.5, 2.5),
        "xlabel": "$\\eta_{\\mu1}$",
    }
    variables["etal2"] = {
        "axis": (100, -2.5, 2.5),
        "xlabel": "$\\eta_{\\mu2}$",
    }
    variables["mll"] = {
        "axis": (400, 70, 110),
        "xlabel": "$m_{\\mu\\mu}$ [GeV]",
    }
    variables["mll_H"] = {
        "variable": "mll",
        "axis": (100, 110, 150),
        "xlabel": "$m_{\\mu\\mu}$ [GeV]",
    }
    # variables["mll_all"] = {
    #     "variable": "mll",
    #     "axis": (400, 70, 150),
    #     "xlabel": "$m_{\\mu\\mu}$ [GeV]",
    # }

    variables["ptll"] = {
        "axis": (300, 0, 200),
        "xlabel": "$p^T_{\\mu\\mu}$ [GeV]",
    }

    variables["njet"] = {
        "axis": (10, 0, 10),
        "xlabel": "$N_{jets}$",
    }

    # variables["ptj1"] = {
    #     "axis": (100, 25, 200),
    #     "xlabel": "$p^T_{j1}$ [GeV]",
    # }
    # variables["ptj2"] = {
    #     "axis": (100, 25, 200),
    #     "xlabel": "$p^T_{j2}$ [GeV]",
    # }
    # variables["etaj1"] = {
    #     "axis": (100, -4.7, 4.7),
    #     "xlabel": "$\\eta_{j1}$",
    # }
    # variables["etaj2"] = {
    #     "axis": (100, -4.7, 4.7),
    #     "xlabel": "$\\eta_{j2}$",
    # }
    # variables["mjj"] = {
    #     "axis": (20, 400, 2000),
    #     "xlabel": "$m_{jj}$ [GeV]",
    # }
    # variables["detajj"] = {
    #     "axis": (30, 2.5, 8),
    #     "xlabel": "$\\Delta\\eta_{jj}$",
    # }

    # variables["sigma_res"] = {
    #     "axis": (100, 5e-3, 40e-3),
    #     "xlabel": "$\\sigma_{res}$",
    # }

    # # NN for mumu system
    # variables["etall"] = {
    #     "axis": (100, -2.5, 2.5),
    #     "xlabel": "$\\eta_{\\mu\\mu}$",
    # }
    # variables["phi_cs"] = {
    #     "axis": (100, -3.15, 3.15),
    #     "xlabel": "$\\phi_{CS}$",
    # }
    # variables["cos_theta_cs"] = {
    #     "axis": (100, -1, 1),
    #     "xlabel": "$\\cos(\\theta_{CS})$",
    # }

    # # NN for dijet system
    # variables["dphijj"] = {
    #     "axis": (100, 0, 3.15),
    #     "xlabel": "$\\Delta\\phi_{jj}$",
    # }
    # variables["ptjj"] = {
    #     "axis": (30, 0, 200),
    #     "xlabel": "$p^T_{jj}$ [GeV]",
    # }
    # variables["zeppenfeld"] = {
    #     "axis": (100, -5, 5),
    #     "xlabel": "Zeppenfeld variable",
    # }
    # variables["min_dphi_lljj"] = {
    #     "axis": (100, 0, 3.15),
    #     "xlabel": "min $\\Delta\\phi_{ll,j}$",
    # }
    # variables["min_deta_lljj"] = {
    #     "axis": (100, 0, 8),
    #     "xlabel": "min $\\Delta\\eta_{ll,j}$",
    # }

    # variables["ptl1_etal1"] = {
    #     "variable": ["etal1", "ptl1"],
    #     # "axis": (50, -2.4, 2.4, 50, 26, 200),
    #     "axis": (
    #         13,
    #         array(
    #             "d",
    #             [
    #                 -2.4,
    #                 -2.1,
    #                 -1.6,
    #                 -1.2,
    #                 -0.9,
    #                 -0.3,
    #                 -0.2,
    #                 0.2,
    #                 0.3,
    #                 0.9,
    #                 1.2,
    #                 1.6,
    #                 2.1,
    #                 2.4,
    #             ],
    #         ),
    #         6,
    #         array("d", [26.0, 30.0, 40.0, 50.0, 60.0, 120.0, 200]),
    #     ),
    #     "xlabel": "$\\sigma_{res}$",
    # }

    if not apply_ptll:
        if "ptll" not in variables:
            raise Exception("ptll variable must be defined if extracting ptll")
        if "njet" not in variables:
            raise Exception("njet variable must be defined if extracting ptll")

    regions = {}

    regions["baseline"] = {
        "mask": "mll > 70 && mll < 110",
        # "skip_fill": True,
    }
    regions["baseline_H"] = {
        "mask": "mll > 110 && mll < 150",
        # "skip_fill": True,
    }
    regions["baseline_sideband"] = {
        "mask": "(mll > 110 && mll < 120) || (mll > 130 && mll < 150)",
        "skip_fill": True,
    }
    regions["baseline_all"] = {
        "mask": "mll > 70 && mll < 150",
        "skip_fill": True,
    }

    # if not apply_ptll:
    #     njet_ptll_bins = 3
    #     for ijet in range(njet_ptll_bins):
    #         if ijet == njet_ptll_bins - 1:
    #             mask = f"njet >= {ijet}"
    #         else:
    #             mask = f"njet == {ijet}"
    #         regions[f"baseline_{ijet}j"] = {
    #             "mask": f"baseline && {mask} && bveto",
    #         }

    regions["VBF_Z"] = {
        "mask": "baseline && is_vbf && bveto",
    }
    regions["VBF_SB_H"] = {
        "mask": "baseline_sideband && is_vbf && bveto",
    }
    regions["VBF_H"] = {
        "mask": "baseline_H && is_vbf && bveto",
        "skip_fill": True,
    }

    regions["ggF_Z"] = {
        "mask": "baseline && !is_vbf && bveto",
        # "skip_fill": True,
    }
    # regions["ggF_SB_H"] = {
    #     "mask": "baseline_sideband && !is_vbf && bveto",
    #     "skip_fill": True,
    # }
    regions["ggF_H"] = {
        "mask": "baseline_H && !is_vbf && bveto",
        # "skip_fill": True,
    }

    for region in ["ggF_Z", "VBF_Z"]:
        njet_ptll_bins = 3
        for ijet in range(njet_ptll_bins):
            if ijet == njet_ptll_bins - 1:
                mask = f"njet >= {ijet}"
            else:
                mask = f"njet == {ijet}"
            regions[f"{region}_{ijet}j"] = {
                "mask": f"{region} && {mask}",
            }

    if not apply_ptll:
        if "baseline" not in regions or regions["baseline"].get("skip_fill", False):
            raise Exception("baseline region must be defined if extracting ptll")

    return datasets, variables, regions, base_folder
