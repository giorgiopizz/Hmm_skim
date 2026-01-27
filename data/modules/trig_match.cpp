
using LorentzVectorM = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double>>;
using RVecLV = ROOT::VecOps::RVec<LorentzVectorM>;

int FindMatching(const LorentzVectorM &target_p4, const RVecLV &ref_p4, const float deltaR_thr) {
    double deltaR_min = deltaR_thr;
    int current_idx = -1;
    for (int refIdx = 0; refIdx < ref_p4.size(); refIdx++) {
        auto dR_targetRef = ROOT::Math::VectorUtil::DeltaR(target_p4, ref_p4.at(refIdx));
        if (dR_targetRef < deltaR_min) {
            deltaR_min = dR_targetRef;
            current_idx = refIdx;
        }
    }
    return current_idx;
}