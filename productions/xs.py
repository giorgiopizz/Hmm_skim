# all in pb
xs = {}

xs["DYto2L_M_50_amcatnloFXFX"] = 2094.2 * 3
xs["DYto2L_M_50_0J_amcatnloFXFX"] = 5378.0
xs["DYto2L_M_50_1J_amcatnloFXFX"] = 1017.0
xs["DYto2L_M_50_2J_amcatnloFXFX"] = 385.5

for lep in ["E", "Mu", "Tau"]:
    xs[f"DYto2{lep}_M_50_amcatnloFXFX"] = 2094.2

    xs[f"DYto2{lep}_M_50_0J_amcatnloFXFX"] = 5378.0 / 3
    xs[f"DYto2{lep}_M_50_1J_amcatnloFXFX"] = 1017.0 / 3
    xs[f"DYto2{lep}_M_50_2J_amcatnloFXFX"] = 385.5 / 3

for lep in ["E", "Mu", "Tau"]:
    xs[f"WTo{lep}Nu_amcatnloFXFX"] = 9013.3 + 12128.4

xs["TTto2L2Nu"] = 923.6 * (1 - 0.6741) * (1 - 0.6741)
xs["TTto4Q"] = 923.6 * 0.6741 * 0.6741
xs["TTtoLNu2Q"] = 923.6 * 0.6741 * (1 - 0.6741) * 2

xs["WWto2L2Nu_powheg"] = 11.79
xs["WWtoLNu2Q_powheg"] = 15.87
xs["WWto4Q_powheg"] = 50.79

xs["WZto3LNu_powheg"] = 4.924
xs["WZto2L2Q_powheg"] = 7.568
xs["WZtoLNu2Q_powheg"] = 15.87

xs["ZZto2L2Nu_powheg"] = 1.031
xs["ZZto4L_powheg"] = 1.39
xs["ZZto2L2Q_powheg"] = 6.788
xs["ZZto2Nu2Q_powheg"] = 4.826

xs["TbarBtoLminusNuB_s_channel_4FS"] = 4.534 * (1 - 0.6741)
xs["TBbartoLplusNuBbar_s_channel_4FS"] = 7.244 * (1 - 0.6741)
xs["TbarBQtoLNu_t_channel_4FS"] = 23.34
xs["TbarBQto2Q_t_channel_4FS"] = 46.73
xs["TBbarQtoLNu_t_channel_4FS"] = 38.6
xs["TBbarQto2Q_t_channel_4FS"] = 77.26

xs["TWminusto2L2Nu"] = 87.9 * (0.4995) * (1 - 0.6741) * (1 - 0.6741)
xs["TbarWplusto2L2Nu"] = 87.9 * (0.5005) * (1 - 0.6741) * (1 - 0.6741)
xs["TWminustoLNu2Q"] = (
    87.9 * (0.4995) * (((1 - 0.6741) * (0.6741)) + ((0.6741) * (1 - 0.6741)))
)
xs["TbarWplustoLNu2Q"] = (
    87.9 * (0.5005) * (((1 - 0.6741) * (0.6741)) + ((0.6741) * (1 - 0.6741)))
)
xs["TWminusto4Q"] = 87.9 * (0.4995) * (0.6741) * (0.6741)
xs["TbarWplusto4Q"] = 87.9 * (0.5005) * (0.6741) * (0.6741)

xs["EWK_2L2J_madgraph_herwig"] = 1.418

xs["VBFHto2Mu"] = 4.078 * (0.0002176)
xs["GluGluHto2Mu"] = 52.23 * (0.0002176)

# FIXME it should be ttH
xs["ttZHto2Mu"] = 0.57 * (0.0002176)

xs["WplusHto2Mu"] = 0.8889 * (0.0002176)
xs["WminusHto2Mu"] = 0.5677 * (0.0002176)
xs["ZHto2Mu"] = 0.9439 * (0.0002176)
