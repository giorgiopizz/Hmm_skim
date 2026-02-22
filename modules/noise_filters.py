import ROOT


def run_noise_filters(df, is_data=False):
    flags = [
        "Flag_goodVertices",
        "Flag_globalSuperTightHalo2016Filter",
        "Flag_EcalDeadCellTriggerPrimitiveFilter",
        "Flag_BadPFMuonFilter",
        "Flag_BadPFMuonDzFilter",
        "Flag_hfNoisyHitsFilter",
        "Flag_eeBadScFilter",
        "Flag_ecalBadCalibFilter",
    ]

    df = df.Define(
        "good_event",
        " && ".join([f"{flag} == 1" for flag in flags]),
    )
    return df
