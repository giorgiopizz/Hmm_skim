def run_btag(df, year):
    btag_WPs = {
        "2025": {
            "col": "btagUParTAK4B",
            "M": 0.1272,
        },
        "2024": {
            "col": "btagUParTAK4B",
            "M": 0.1272,
        },
        "2023BPix": {
            "col": "btagPNetB",
            "M": 0.1919,
        },
        "2023": {
            "col": "btagPNetB",
            "M": 0.1917,
        },
        "2022EE": {
            "col": "btagPNetB",
            "M": 0.2605,
        },
        "2022": {
            "col": "btagPNetB",
            "M": 0.245,
        },
    }
    wps = ["M"]
    for wp in wps:
        df = df.Define(
            f"Jet_btag_{wp}",
            f"Jet_{btag_WPs[year]['col']} >= {btag_WPs[year][wp]} && abs(Jet_eta) < 2.5",
        )
    return df
