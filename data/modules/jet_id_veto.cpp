#include <tuple>

using RVecB = ROOT::VecOps::RVec<Bool_t>;
using RVecI = ROOT::VecOps::RVec<Int_t>;
using RVecF = ROOT::VecOps::RVec<Float_t>;

std::tuple<RVecI, RVecI> jet_id(
    const std::unique_ptr<correction::CorrectionSet> &ceval_jetid,
    const RVecF &Jet_eta,
    const RVecF &Jet_chHEF,
    const RVecF &Jet_neHEF,
    const RVecF &Jet_chEmEF,
    const RVecF &Jet_neEmEF,
    const RVecF &Jet_muEF,
    const RVecI &Jet_chMultiplicity,
    const RVecI &Jet_neMultiplicity)
{
    auto res = std::make_tuple<RVecI, RVecI>(RVecI(Jet_eta.size(), 0), RVecI(Jet_eta.size(), 0));

    for (size_t i = 0; i < Jet_eta.size(); i++)
    {
        std::get<0>(res)[i] = int(ceval_jetid->at("AK4PUPPI_Tight")->evaluate({
            Jet_eta[i],
            Jet_chHEF[i],
            Jet_neHEF[i],
            Jet_chEmEF[i],
            Jet_neEmEF[i],
            Jet_muEF[i],
            Jet_chMultiplicity[i],
            Jet_neMultiplicity[i],
            Jet_chMultiplicity[i] + Jet_neMultiplicity[i],
        }));

        std::get<1>(res)[i] = int(ceval_jetid->at("AK4PUPPI_TightLeptonVeto")->evaluate({
            Jet_eta[i],
            Jet_chHEF[i],
            Jet_neHEF[i],
            Jet_chEmEF[i],
            Jet_neEmEF[i],
            Jet_muEF[i],
            Jet_chMultiplicity[i],
            Jet_neMultiplicity[i],
            Jet_chMultiplicity[i] + Jet_neMultiplicity[i],
        }));

    }
    return res;
}

RVecF jet_veto(const std::shared_ptr<const correction::Correction> &ceval_jetveto, const RVecF &Jet_eta, const RVecF &Jet_phi)
{
    RVecF Jet_veto(Jet_eta.size(), 0);

    for (size_t i = 0; i < Jet_eta.size(); i++)
    {
        Jet_veto[i] = ceval_jetveto->evaluate({"jetvetomap", Jet_eta[i], Jet_phi[i]});
    }
    return Jet_veto;
}
