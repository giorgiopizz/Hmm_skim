std::pair<double, double> compute_cs_variables_old(
    float mu1_pt, float mu1_eta, float mu1_phi, float mu1_mass, int mu1_charge,
    float mu2_pt, float mu2_eta, float mu2_phi, float mu2_mass)
{
    TLorentzVector m1, m2, mm;
    m1.SetPtEtaPhiM(mu1_pt, mu1_eta, mu1_phi, mu1_mass);
    m2.SetPtEtaPhiM(mu2_pt, mu2_eta, mu2_phi, mu2_mass);
    mm = m1 + m2;

    TLorentzVector h1s, h2s;
    h1s.SetPxPyPzE(0., 0., 1.0, 1.0);
    h2s.SetPxPyPzE(0., 0., -1.0, 1.0);

    m1.Boost(-mm.BoostVector());
    m2.Boost(-mm.BoostVector());
    h1s.Boost(-mm.BoostVector());
    h2s.Boost(-mm.BoostVector());

    TVector3 zaxisCS = (h1s.Vect().Unit() - h2s.Vect().Unit()).Unit();
    TVector3 yaxisCS = (h1s.Vect().Unit().Cross(h2s.Vect().Unit())).Unit();
    TVector3 xaxisCS = (yaxisCS.Cross(zaxisCS)).Unit();
    TLorentzVector l1v = (mu1_charge > 0 ? m1 : m2);
    double vmmphics = TMath::ATan2(l1v.Vect().Dot(yaxisCS), l1v.Vect().Dot(xaxisCS));
    double vmmthetacs = l1v.Vect().Unit().Dot(zaxisCS);

    return {vmmphics, vmmthetacs};
}

using LV_M = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double>>;
using LV_PxPyPzE = ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double>>;

std::pair<double, double> compute_cs_variables(
    float mu1_pt, float mu1_eta, float mu1_phi, float mu1_mass, int mu1_charge,
    float mu2_pt, float mu2_eta, float mu2_phi, float mu2_mass)
{
    LV_M m1, m2, mm;
    m1.SetCoordinates(mu1_pt, mu1_eta, mu1_phi, mu1_mass);
    m2.SetCoordinates(mu2_pt, mu2_eta, mu2_phi, mu2_mass);
    mm = m1 + m2;

    LV_PxPyPzE h1s, h2s;
    h1s.SetCoordinates(0., 0., 1.0, 1.0);
    h2s.SetCoordinates(0., 0., -1.0, 1.0);

    auto betaCM = mm.BoostToCM();

    m1 = ROOT::Math::VectorUtil::boost(m1, betaCM);
    m2 = ROOT::Math::VectorUtil::boost(m2, betaCM);
    h1s = ROOT::Math::VectorUtil::boost(h1s, betaCM);
    h2s = ROOT::Math::VectorUtil::boost(h2s, betaCM);

    auto zaxisCS = (h1s.Vect().Unit() - h2s.Vect().Unit()).Unit();
    auto yaxisCS = (h1s.Vect().Unit().Cross(h2s.Vect().Unit())).Unit();
    auto xaxisCS = (yaxisCS.Cross(zaxisCS)).Unit();
    LV_M l1v = (mu1_charge > 0 ? m1 : m2);
    double vmmphics = TMath::ATan2(l1v.Vect().Dot(yaxisCS), l1v.Vect().Dot(xaxisCS));
    double vmmthetacs = l1v.Vect().Unit().Dot(zaxisCS);

    return {vmmphics, vmmthetacs};
}

// Zeppenfeld, min_dphi, min_deta
std::tuple<double, double, double> compute_NN_variables(
    LV_M mm,
    LV_M &j1_p4, LV_M &j2_p4, int njet)
{
    double min_dphi = -999;
    double min_deta = -999;
    if (njet == 1)
    {
        min_dphi = abs(ROOT::Math::VectorUtil::DeltaPhi(mm, j1_p4));
        min_deta = abs(mm.Eta() - j1_p4.Eta());
    }
    else if (njet >= 2)
    {
        min_dphi = std::min(
            abs(ROOT::Math::VectorUtil::DeltaPhi(mm, j1_p4)),
            abs(ROOT::Math::VectorUtil::DeltaPhi(mm, j2_p4)));
        min_deta = std::min(
            abs(mm.Eta() - j1_p4.Eta()),
            abs(mm.Eta() - j2_p4.Eta()));
    }

    double zepp = -999;

    if (njet >= 2)
    {
        double detajj = std::max((double)1e-4, abs(j1_p4.Eta() - j2_p4.Eta()));
        zepp = (mm.Eta() - 0.5 * (j1_p4.Eta() + j2_p4.Eta())) / detajj;
    }

    return {zepp, min_dphi, min_deta};
}