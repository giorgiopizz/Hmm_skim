#include <tuple>

using RVecB = ROOT::VecOps::RVec<Bool_t>;
using RVecI = ROOT::VecOps::RVec<Int_t>;
using RVecF = ROOT::VecOps::RVec<Float_t>;

namespace v15
{
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
}

namespace v12
{
    std::tuple<RVecI, RVecI> jet_id(
        const RVecF &Jet_eta,
        const RVecF &Jet_neHEF,
        const RVecF &Jet_chEmEF,
        const RVecF &Jet_neEmEF,
        const RVecF &Jet_muEF,
        const RVecI &Jet_jetId)
    {
        auto res = std::make_tuple<RVecI, RVecI>(RVecI(Jet_eta.size(), 0), RVecI(Jet_eta.size(), 0));
        for (size_t i = 0; i < Jet_eta.size(); i++)
        {
            bool Jet_passJetIdTight = false;
            if (fabs(Jet_eta[i]) <= 2.7)
                Jet_passJetIdTight = Jet_jetId[i] & (1 << 1);
            else if (fabs(Jet_eta[i]) > 2.7 && fabs(Jet_eta[i]) <= 3.0)
                Jet_passJetIdTight = (Jet_jetId[i] & (1 << 1)) && (Jet_neHEF[i] < 0.99);
            else if (fabs(Jet_eta[i]) > 3.0)
                Jet_passJetIdTight = (Jet_jetId[i] & (1 << 1)) && (Jet_neEmEF[i] < 0.4);

            bool Jet_passJetIdTightLepVeto = false;
            if (fabs(Jet_eta[i]) <= 2.7)
                Jet_passJetIdTightLepVeto = Jet_passJetIdTight && (Jet_muEF[i] < 0.8) && (Jet_chEmEF[i] < 0.8);
            else
                Jet_passJetIdTightLepVeto = Jet_passJetIdTight;

            std::get<0>(res)[i] = int(Jet_passJetIdTight);
            std::get<1>(res)[i] = int(Jet_passJetIdTightLepVeto);
        }
        return res;
    }
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

namespace SPRITZ
{
    float DeltaPhi(float phi1, float phi2)
    {
        float dPhi = phi1 - phi2;
        if (dPhi > M_PI)
            dPhi -= 2 * M_PI;
        else if (dPhi < -M_PI)
            dPhi += 2 * M_PI;
        return dPhi;
    }

    RVecF DeltaR(const RVecF &eta1, const RVecF &phi1, const float eta2, const float phi2)
    {
        RVecF result(eta1.size(), 0);
        for (size_t i = 0; i < eta1.size(); i++)
        {
            float dEta = eta1[i] - eta2;
            float dPhi = DeltaPhi(phi1[i], phi2);
            result[i] = sqrt(dEta * dEta + dPhi * dPhi);
        }
        return result;
    }
}