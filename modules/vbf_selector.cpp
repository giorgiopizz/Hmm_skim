
std::tuple<int, int, float, float> GetVBFJetIndices(const RVecF &Jet_pt, const RVecF &Jet_eta,
                                                    const RVecF &Jet_phi, const RVecF &Jet_mass)
{
    std::tuple<int, int, float, float> result(-1, -1, 0, 0);
    // make PtEtaPhiMVector of jets
    std::vector<ROOT::Math::PtEtaPhiMVector> jets;
    for (size_t i = 0; i < Jet_pt.size(); ++i)
    {
        jets.emplace_back(Jet_pt[i], Jet_eta[i], Jet_phi[i], Jet_mass[i]);
    }

    // loop over jets and find the two jets with highest invariant mass
    float maxMjj = -1;
    for (size_t i = 0; i < jets.size(); ++i)
    {
        // if (!Jet_mask[i])
        //     continue;

        for (size_t j = i + 1; j < jets.size(); ++j)
        {
            // if (!Jet_mask[j])
            //     continue;

            const float mjj = (jets[i] + jets[j]).M();
            const float detajj = std::abs(jets[i].Eta() - jets[j].Eta());

            if (!((mjj > 400) && (detajj > 2.5) && (jets[i].Pt() > 35) && (jets[j].Pt() > 25)))
                continue;

            if (mjj > maxMjj)
            {
                maxMjj = mjj;
                result = std::make_tuple(i, j, mjj, detajj);
            }
        }
    }

    return result;
}