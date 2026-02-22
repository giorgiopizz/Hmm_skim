
using LorentzVectorM = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double>>;
using RVecLV = ROOT::VecOps::RVec<LorentzVectorM>;

int FindMatching(const LorentzVectorM &target_p4, const RVecLV &ref_p4, const float deltaR_thr)
{
    double deltaR_min = deltaR_thr;
    int current_idx = -1;
    for (int refIdx = 0; refIdx < ref_p4.size(); refIdx++)
    {
        auto dR_targetRef = ROOT::Math::VectorUtil::DeltaR(target_p4, ref_p4.at(refIdx));
        if (dR_targetRef < deltaR_min)
        {
            deltaR_min = dR_targetRef;
            current_idx = refIdx;
        }
    }
    return current_idx;
}

// trigger matching
UInt_t trg_match_ind(
    Float_t eta,
    Float_t phi,
    ROOT::VecOps::RVec<UShort_t> &TrigObj_id,
    ROOT::VecOps::RVec<Float_t> &TrigObj_eta,
    ROOT::VecOps::RVec<Float_t> &TrigObj_phi,
    Int_t match1)
{
    Int_t index = -99;
    Float_t dRmin = 1000;
    Float_t dR, dEta, dPhi;
    for (int i = 0; i < TrigObj_id.size(); i++)
    {
        if (TrigObj_id[i] != 13)
            continue;
        if (TrigObj_id[i] == match1)
            continue;
        dEta = eta - TrigObj_eta[i];
        dPhi = (phi - TrigObj_phi[i]);
        if (dPhi > M_PI)
            dPhi -= 2 * M_PI;
        else if (dPhi < -M_PI)
            dPhi += 2 * M_PI;
        dR = sqrt(dEta * dEta + dPhi * dPhi);
        if (dR > 0.1)
            continue;
        if (index > -1)
        {
            if (dR < dRmin)
            {
                dRmin = dR;
                index = i;
            }
            else
                continue;
        }
        else
            index = i;
    }
    return index;
}
