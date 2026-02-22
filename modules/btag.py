def run_btag(df, year):
    btag_WPs = {
        "2024": {
            "col": "btagUParTAK4B",
            "M": 0.1272,  # DeepCSV medium WP
        },
        "2023": {
            "col": "btagPNetB",
            "M": 0.1917,  # DeepCSV medium WP
        },
    }
    wps = ["M"]
    for wp in wps:
        df = df.Define(
            f"Jet_btag_{wp}",
            f"Jet_{btag_WPs[year]['col']} >= {btag_WPs[year][wp]} && abs(Jet_eta) < 2.5",
        )
    return df
