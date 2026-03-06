def run_per_event_mass_res(df):
    df = df.Define(
        "mu1_bs_up_p4",
        "ROOT::Math::PtEtaPhiMVector(mu1_pt + mu1_ptErr, mu1_eta, mu1_phi, mu1_mass)",
    )
    df = df.Define(
        "mu1_bs_down_p4",
        "ROOT::Math::PtEtaPhiMVector(mu1_pt - mu1_ptErr, mu1_eta, mu1_phi, mu1_mass)",
    )
    df = df.Define(
        "mu2_bs_up_p4",
        "ROOT::Math::PtEtaPhiMVector(mu2_pt + mu2_ptErr, mu2_eta, mu2_phi, mu2_mass)",
    )
    df = df.Define(
        "mu2_bs_down_p4",
        "ROOT::Math::PtEtaPhiMVector(mu2_pt - mu2_ptErr, mu2_eta, mu2_phi, mu2_mass)",
    )

    df = df.Define("mll_mu1_bs_up", "(mu1_bs_up_p4 + mu2_p4).M()")
    df = df.Define("mll_mu1_bs_down", "(mu1_bs_down_p4 + mu2_p4).M()")
    df = df.Define("mll_mu2_bs_up", "(mu1_p4 + mu2_bs_up_p4).M()")
    df = df.Define("mll_mu2_bs_down", "(mu1_p4 + mu2_bs_down_p4).M()")

    df = df.Define(
        "per_event_mass_res_up",
        "sqrt(pow(mll_mu1_bs_up - mll, 2) + pow(mll_mu2_bs_up - mll, 2))",
    )
    df = df.Define(
        "per_event_mass_res_down",
        "sqrt(pow(mll_mu1_bs_down - mll, 2) + pow(mll_mu2_bs_down - mll, 2))",
    )
    df = df.Define(
        "per_event_mass_res",
        "0.5 * (per_event_mass_res_up + per_event_mass_res_down)",
    )
    return df
