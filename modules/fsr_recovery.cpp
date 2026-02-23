#include "jet_id_veto.cpp"

std::pair<bool, ROOT::Math::PtEtaPhiMVector> fsr_corrected_p4(float mu_pt, float mu_eta, float mu_phi, float mu_mass, int mu_fsrIdx, const RVecF &fsr_pt, const RVecF &fsr_eta, const RVecF &fsr_phi, const RVecF &fsr_dROverEt2, const RVecF &fsr_relIso03, const RVecF &fsr_electronIdx)
{
    ROOT::Math::PtEtaPhiMVector res{mu_pt, mu_eta, mu_phi, mu_mass};

    if (mu_fsrIdx == -1)
    {
        return {false, res};
    }

    float deltaR_mu_fsr = SPRITZ::DeltaR(mu_eta, mu_phi, fsr_eta[mu_fsrIdx], fsr_phi[mu_fsrIdx]);

    if (!((deltaR_mu_fsr > 0.0001) && (deltaR_mu_fsr < 0.5)))
    {
        return {false, res};
    }

    if (fsr_electronIdx[mu_fsrIdx] != -1)
    {
        return {false, res};
    }

    if (fsr_pt[mu_fsrIdx] / mu_pt > 0.4)
    {
        return {false, res};
    }

    if (fsr_dROverEt2[mu_fsrIdx] > 0.012)
    {
        return {false, res};
    }

    if (fsr_relIso03[mu_fsrIdx] / mu_pt > 1.8)
    {
        return {false, res};
    }

    res += ROOT::Math::PtEtaPhiMVector{fsr_pt[mu_fsrIdx], fsr_eta[mu_fsrIdx], fsr_phi[mu_fsrIdx], 0.0};

    return {true, res};
}