#include <tuple>

using RVecF = ROOT::VecOps::RVec<Float_t>;
using RVecI = ROOT::VecOps::RVec<Int_t>;

class Result_pt_mass
{
public:
    Result_pt_mass(std::size_t n) : pt(n, 0.0f), mass(n, 0.0f) {}
    Result_pt_mass() = default;

    RVecF get_pt() const { return pt; }     // <- by value
    RVecF get_mass() const { return mass; } // <- by value

    void set(std::size_t i, float p, float m)
    {
        pt[i] = p;
        mass[i] = m;
    }

private:
    RVecF pt;
    RVecF mass;
};

// using Result_pt_mass = std::tuple<RVecF, RVecF>;

Result_pt_mass
sf_jec(
    const std::shared_ptr<const correction::CompoundCorrection> &cset_jec,
    const RVecF &jet_pt,
    const RVecF &jet_eta,
    const RVecF &jet_phi,
    const RVecF &jet_mass,
    const RVecF &jet_rawFactor,
    const RVecF &jet_area,
    const float rho)
{
    Result_pt_mass res(jet_pt.size());

    for (size_t i = 0; i < jet_pt.size(); i++)
    {
        auto sf = cset_jec->evaluate({jet_area[i], jet_eta[i],
                                      jet_pt[i] * (1.f - jet_rawFactor[i]),
                                      rho, jet_phi[i]});
        if (sf >= 0.f)
        {
            res.set(i, jet_pt[i] * (1.f - jet_rawFactor[i]) * sf, jet_mass[i] * (1.f - jet_rawFactor[i]) * sf);
        }
        else
        {
            res.set(i, jet_pt[i], jet_mass[i]);
        }
    }
    return res;
}

Result_pt_mass
sf_jec_data(
    const std::shared_ptr<const correction::Correction> &cset_jec_l1,
    const std::shared_ptr<const correction::Correction> &cset_jec_l2,
    const std::shared_ptr<const correction::Correction> &cset_jec_l3,
    const std::shared_ptr<const correction::Correction> &cset_jec_l2l3res,
    const RVecF &jet_pt,
    const RVecF &jet_eta,
    const RVecF &jet_phi,
    const RVecF &jet_mass,
    const RVecF &jet_rawFactor,
    const RVecF &jet_area,
    const float rho,
    const int run)
{
    Result_pt_mass res(jet_pt.size());

    for (size_t i = 0; i < jet_pt.size(); i++)
    {
        // workaround for 2024 issue

        double pt_l1 = jet_pt[i] * cset_jec_l1->evaluate({jet_area[i], jet_eta[i],
                                                          jet_pt[i] * (1.f - jet_rawFactor[i]),
                                                          rho});

        double pt_l2 = pt_l1 * cset_jec_l2->evaluate({jet_eta[i], jet_phi[i],
                                                      pt_l1});

        double pt_l3 = pt_l2 * cset_jec_l3->evaluate({jet_eta[i],
                                                      pt_l2});

        double pt_for_corr = pt_l3;
        if (pt_for_corr < 30 && abs(jet_eta[i]) >= 2.0 && abs(jet_eta[i]) <= 2.5)
            pt_for_corr = 30;

        double pt_l2l3res = pt_l3 * cset_jec_l2l3res->evaluate({(float)run, jet_eta[i], pt_for_corr});

        double sf = pt_l2l3res / (jet_pt[i] * (1.f - jet_rawFactor[i]));

        if (sf >= 0.f)
        {
            res.set(i, jet_pt[i] * (1.f - jet_rawFactor[i]) * sf, jet_mass[i] * (1.f - jet_rawFactor[i]) * sf);
        }
        else
        {
            res.set(i, jet_pt[i], jet_mass[i]);
        }
    }
    return res;
}

template <typename T>
T phi_mpi_pi(T angle)
{
    if (angle <= M_PI && angle > -M_PI)
    {
        return angle;
    }
    if (angle > 0)
    {
        const int n = static_cast<int>(.5 * (angle * M_1_PI + 1.));
        angle -= 2 * n * M_PI;
    }
    else
    {
        const int n = static_cast<int>(-.5 * (angle * M_1_PI - 1.));
        angle += 2 * n * M_PI;
    }
    return angle;
}

const float m_genMatch_dR2max = 2;
const float m_genMatch_dPtmax = -1;

std::size_t findGenMatch(
    const double pt, const float eta, const float phi,
    const std::size_t genJetIdx, const RVecF &gen_pt,
    const RVecF &gen_eta, const RVecF &gen_phi,
    const double resolution)
{
    auto get_dr2 = [](float phi, float eta, float gen_phi, float gen_eta) -> float
    {
        const auto dphi = phi_mpi_pi(gen_phi - phi);
        const auto deta = gen_eta - eta;
        return dphi * dphi + deta * deta;
    };
    auto check_resolution = [resolution](float pt, float gen_pt) -> bool
    {
        return std::abs(gen_pt - pt) < m_genMatch_dPtmax * resolution;
    };

    // First check if matched genJet from NanoAOD is acceptable
    if (genJetIdx >= 0)
    {
        const float dr2 = get_dr2(phi, eta, gen_phi[genJetIdx], gen_eta[genJetIdx]);
        if ((dr2 < m_genMatch_dR2max) && check_resolution(pt, gen_pt[genJetIdx]))
        {
            return genJetIdx;
        }
    }

    std::size_t igBest{gen_pt.size()};
    auto dr2Min = std::numeric_limits<float>::max();
    for (std::size_t ig{0}; ig != gen_pt.size(); ++ig)
    {
        const auto dr2 = get_dr2(phi, eta, gen_phi[ig], gen_eta[ig]);
        if ((dr2 < dr2Min) && (dr2 < m_genMatch_dR2max))
        {
            if (check_resolution(pt, gen_pt[ig]))
            {
                dr2Min = dr2;
                igBest = ig;
            }
        }
    }
    return igBest;
}

std::tuple<Result_pt_mass, Result_pt_mass, Result_pt_mass> sf_jer(
    const std::shared_ptr<const correction::Correction> &cset_jer,
    const std::shared_ptr<const correction::Correction> &cset_jer_ptres,
    const std::shared_ptr<const correction::Correction> &cset_jer_smear,
    const RVecF &jet_pt,
    const RVecF &jet_eta,
    const RVecF &jet_phi,
    const RVecF &jet_mass,
    const RVecF &jet_genJetIdx,
    const double jet_seed,
    const RVecF &GenJet_pt,
    const RVecF &GenJet_eta,
    const RVecF &GenJet_phi,
    const float rho)
{
    std::tuple<Result_pt_mass, Result_pt_mass, Result_pt_mass> res = std::make_tuple(Result_pt_mass(jet_pt.size()), Result_pt_mass(jet_pt.size()), Result_pt_mass(jet_pt.size()));

    for (size_t i = 0; i < jet_pt.size(); i++)
    {
        auto pt_res = cset_jer_ptres->evaluate({jet_eta[i], jet_pt[i], rho});
        float genPt = -1;
        auto iGen = findGenMatch(jet_pt[i], jet_eta[i], jet_phi[i], jet_genJetIdx[i], GenJet_pt, GenJet_eta, GenJet_phi, pt_res * jet_pt[i]);
        if (iGen < GenJet_pt.size())
        {
            genPt = GenJet_pt[iGen];
        }

        auto smear_nom = cset_jer_smear->evaluate({jet_pt[i], jet_eta[i], genPt, rho, int(jet_seed), pt_res, cset_jer->evaluate({jet_eta[i], jet_pt[i], "nom"})});
        auto smear_down = cset_jer_smear->evaluate({jet_pt[i], jet_eta[i], genPt, rho, int(jet_seed), pt_res, cset_jer->evaluate({jet_eta[i], jet_pt[i], "down"})});
        auto smear_up = cset_jer_smear->evaluate({jet_pt[i], jet_eta[i], genPt, rho, int(jet_seed), pt_res, cset_jer->evaluate({jet_eta[i], jet_pt[i], "up"})});

        // mitigate horns, apply JER to matched genJets only in 2.5-3.0 eta region
        if (abs(jet_eta[i]) > 2.5 && abs(jet_eta[i]) < 3.0 && iGen >= GenJet_pt.size())
        {
            smear_nom = 1.f;
            smear_down = 1.f;
            smear_up = 1.f;
        }

        std::get<0>(res).set(i, jet_pt[i] * smear_nom, jet_mass[i] * smear_nom);

        std::get<1>(res).set(i, jet_pt[i] * smear_down, jet_mass[i] * smear_down);

        std::get<2>(res).set(i, jet_pt[i] * smear_up, jet_mass[i] * smear_up);
    }
    return res;
}

std::tuple<Result_pt_mass, Result_pt_mass> sf_jes(
    const std::shared_ptr<const correction::Correction> &cset_jes,
    const RVecF &jet_eta,
    const RVecF &jet_pt,
    const RVecF &jet_mass)
{
    std::tuple<Result_pt_mass, Result_pt_mass> res = std::make_tuple(Result_pt_mass(jet_pt.size()), Result_pt_mass(jet_pt.size()));

    for (size_t i = 0; i < jet_pt.size(); i++)
    {
        auto delta = cset_jes->evaluate({jet_eta[i], jet_pt[i]});

        std::get<0>(res).set(i, jet_pt[i] * (1 - delta), jet_mass[i] * (1 - delta));
        std::get<1>(res).set(i, jet_pt[i] * (1 + delta), jet_mass[i] * (1 + delta));
    }
    return res;
}