Samples = {}

## Data

Samples["Muon_Run2022C_v1"] = {
    "nanoAOD": "/Muon/Run2022C-22Sep2023-v1/NANOAOD",
    "is_data": True,
}
Samples["Muon_Run2022D_v1"] = {
    "nanoAOD": "/Muon/Run2022D-22Sep2023-v1/NANOAOD",
    "is_data": True,
}


mc_pattern_year = "Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic"

## DY samples, probably the only ones we can use for now
## for the future DYto2Mu should be jet binned, the others may not

Samples["DYto2L_M_50_amcatnloFXFX"] = {
    "pattern": f"/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/{mc_pattern_year}*/NANOAODSIM",
}

Samples["DYto2L_M_50_0J_amcatnloFXFX"] = {
    "pattern": f"/DYto2L-2Jets_MLL-50_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/{mc_pattern_year}*/NANOAODSIM"
}
Samples["DYto2L_M_50_1J_amcatnloFXFX"] = {
    "pattern": f"/DYto2L-2Jets_MLL-50_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/{mc_pattern_year}*/NANOAODSIM"
}
Samples["DYto2L_M_50_2J_amcatnloFXFX"] = {
    "pattern": f"/DYto2L-2Jets_MLL-50_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/{mc_pattern_year}*/NANOAODSIM"
}


Samples["WToLNu_0J_amcatnloFXFX"] = {
    "pattern": f"/WtoLNu-2Jets_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/{mc_pattern_year}*/NANOAODSIM"
}
Samples["WToLNu_1J_amcatnloFXFX"] = {
    "pattern": f"/WtoLNu-2Jets_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/{mc_pattern_year}*/NANOAODSIM"
}
Samples["WToLNu_2J_amcatnloFXFX"] = {
    "pattern": f"/WtoLNu-2Jets_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/{mc_pattern_year}*/NANOAODSIM"
}


## TT samples
Samples["TTto2L2Nu"] = {
    "pattern": f"/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}
Samples["TTtoLNu2Q"] = {
    "pattern": f"/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["TTto4Q"] = {
    "pattern": f"/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

## WW, WZ, ZZ samples
Samples["WWto2L2Nu_powheg"] = {
    "pattern": f"/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["WWtoLNu2Q_powheg"] = {
    "pattern": f"/WWtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["WWto4Q_powheg"] = {
    "pattern": f"/WWto4Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["WZto3LNu_powheg"] = {
    "pattern": f"/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["WZto2L2Q_powheg"] = {
    "pattern": f"/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["WZtoLNu2Q_powheg"] = {
    "pattern": f"/WZtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["ZZto2L2Nu_powheg"] = {
    "pattern": f"/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["ZZto4L_powheg"] = {
    "pattern": f"/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["ZZto2L2Q_powheg"] = {
    "pattern": f"/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["ZZto2Nu2Q_powheg"] = {
    "pattern": f"/ZZto2Nu2Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}


## Single Top samples

Samples["TbarBtoLminusNuB_s_channel_4FS"] = {
    "pattern": f"/TbarBtoLminusNuB-s-channel-4FS_TuneCP5_13p6TeV_amcatnlo-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["TBbartoLplusNuBbar_s_channel_4FS"] = {
    "pattern": f"/TBbartoLplusNuBbar-s-channel-4FS_TuneCP5_13p6TeV_amcatnlo-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["TbarBQ_t_channel_4FS"] = {
    "pattern": f"/TbarBQ_t-channel_4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["TBbarQ_t_channel_4FS"] = {
    "pattern": f"/TBbarQ_t-channel_4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

## ST W

Samples["TWminusto2L2Nu"] = {
    "pattern": f"/TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["TbarWplusto2L2Nu"] = {
    "pattern": f"/TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["TWminustoLNu2Q"] = {
    "pattern": f"/TWminustoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["TbarWplustoLNu2Q"] = {
    "pattern": f"/TbarWplustoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}

Samples["TWminusto4Q"] = {
    "pattern": f"/TWminusto4Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM",
}

Samples["TbarWplusto4Q"] = {
    "pattern": f"/TbarWplusto4Q_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM",
}

Samples["EWK_2L2J_madgraph_herwig"] = {
    "pattern": f"/EWK_2L2J_TuneCH3_13p6TeV_madgraph-herwig7/{mc_pattern_year}*/NANOAODSIM"
}

# ## Signal samples

# VBFH
Samples["VBFHto2Mu"] = {
    "pattern": f"/VBFHto2Mu_M-125_TuneCP5_withDipoleRecoil_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM",
}

# ggH
Samples["GluGluHto2Mu"] = {
    "pattern": f"/GluGluHto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM",
}

# VH
Samples["WplusHto2Mu"] = {
    "pattern": f"/WplusH_Hto2Mu_M-125_TuneCP5_13p6TeV_powheg-minlo-pythia8/{mc_pattern_year}*/NANOAODSIM"
}
Samples["WminusHto2Mu"] = {
    "pattern": f"/WminusH_Hto2Mu_M-125_TuneCP5_13p6TeV_powheg-minlo-pythia8/{mc_pattern_year}*/NANOAODSIM"
}
##ZH
# qqH
Samples["ZHto2Mu"] = {
    "pattern": f"/ZH_Hto2Mu_M-125_TuneCP5_13p6TeV_powheg-minlo-pythia8/{mc_pattern_year}*/NANOAODSIM"
}
# #ggH
# # FIXME missing sample
# Samples["ggZHto2Mu"] = {
#     "nanoAOD": "/GluGluZH_Zto2L_Hto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM"
# }

Samples["TTHto2Mu"] = {
    "pattern": f"/TTH_Hto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/{mc_pattern_year}*/NANOAODSIM"
}


# # # bbH
# # # FIXME missing sample
# # # Samples["bbHto2Mu"] = {
# # #     "nanoAOD": "/BBH-Zto2L-Hto2Mu_Par-M-125_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM"
# # # }

# # # THQ
# # # FIXME missing sample
# # # Samples["THQto2Mu"] = {
# # #     "nanoAOD": "/THQ-ctcvcp-Hto2Mu-4FS_Par-M-125_TuneCP5_13p6TeV_madgraph-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM"
# # # }

# # # THW
# # # FIXME missing sample
# # # Samples["THWto2Mu"] = {
# # #     "nanoAOD": "/THW-ctcvcp-Hto2Mu-5FS_Par-M-125_TuneCP5_13p6TeV_madgraph-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM"
# # # }