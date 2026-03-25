import argparse

import ROOT
import uproot
import numpy as np
import matplotlib.pyplot as plt
import hist
import correctionlib.convert
import rich
import correctionlib.schemav2 as cs
from config import get_config
import iminuit
from uncertainties import unumpy as unp

parser = argparse.ArgumentParser()
parser.add_argument("--year", type=str, help="Year of the production", required=True)
args = parser.parse_args()
year = args.year

datasets, variables, regions, _ = get_config(year, apply_ptll=True)

# -----------------------------------------------------------------------------
# Region configuration
# -----------------------------------------------------------------------------
# Adapt these names if the folders in your ROOT file are named differently.
# Assumption:
#   - ggF_Z is split in 0j / 1j / 2j(>=2j)
#   - VBF_Z is a >=2j category only
REGION_MAP = {
    "ggF": {
        0: "ggF_Z_0j",
        1: "ggF_Z_1j",
        2: "ggF_Z_2j",   # interpreted as >=2j
    },
    "VBF": {
        2: "VBF_Z",      # interpreted as >=2j only
    },
}

var = "ptll"

f = uproot.open(f"roots/{year}_extract_ptll.root")

mcs = [ds for ds in datasets if ds != "data"]

edges = None
big_histos = {}
data = {}

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def rebin_ptll_with_unc(unvals):
    # first 150 bins untouched, then groups of 10
    return np.concatenate(
        [
            unvals[:150],
            unvals[150:].reshape(-1, 10).sum(axis=1),
        ]
    )


def get_rebinned_edges(h):
    edges = h.axes[0].edges
    return np.concatenate(
        [
            [edges[i] for i in range(0, 151, 1)],
            [edges[i] for i in range(150, len(edges) - 1, 10)],
        ]
    )


def read_region_hists(region_name):
    global edges

    histos = {}
    for mc in mcs + ["data"]:
        h = f[f"{region_name}/{var}/histo_{mc}"].to_hist()

        vals = h.values(True)
        vals[1] += vals[0]  # underflow -> first bin
        vals = vals[1:-1]

        variances = h.variances(True)
        variances[1] += variances[0]  # underflow -> first bin
        variances = variances[1:-1]

        unvals = unp.uarray(vals, np.sqrt(variances))
        histos[mc] = rebin_ptll_with_unc(unvals)

        if edges is None:
            edges = get_rebinned_edges(h)

    return histos


def old_func(x, x1, x2, A1, A2, mu1, mu2, sigma1, sigma2, shift, a, b, c, d):
    exp = np.exp
    pow = np.power
    from scipy.special import erf

    return (
        (A1 * exp(-0.5 * pow(((x - mu1) / sigma1), 2)) + shift)
        * (erf(-999 * (x - x1)) + 1)
        / 2
        + (
            A1 * exp(-0.5 * pow(((x1 - mu1) / sigma1), 2))
            + shift
            + A2 * exp(-0.5 * pow(((x - mu2) / sigma2), 2))
            - A2 * exp(-0.5 * pow(((x1 - mu2) / sigma2), 2))
        )
        * (erf(999 * (x - x1)) + 1)
        / 2
        * (erf(-999 * (x - x2)) + 1)
        / 2
        + (
            A1 * exp(-0.5 * pow(((x1 - mu1) / sigma1), 2))
            + shift
            + A2 * exp(-0.5 * pow(((x2 - mu2) / sigma2), 2))
            - A2 * exp(-0.5 * pow(((x1 - mu2) / sigma2), 2))
            + a * (x - x2)
            + d * pow((x - x2), 2)
        )
        * (erf(999 * (x - x2)) + 1)
        / 2
        * b
        + c * (erf(999 * (x - x2)) + 1)
    )


def get_string_fit(names, values):
    expr = """(
        (A1 * exp(-0.5 * pow(((x - mu1) / sigma1), 2)) + shift)
        * (erf(-999 * (x - x1)) + 1)
        / 2
        + (
            A1 * exp(-0.5 * pow(((x1 - mu1) / sigma1), 2))
            + shift
            + A2 * exp(-0.5 * pow(((x - mu2) / sigma2), 2))
            - A2 * exp(-0.5 * pow(((x1 - mu2) / sigma2), 2))
        )
        * (erf(999 * (x - x1)) + 1)
        / 2
        * (erf(-999 * (x - x2)) + 1)
        / 2
        + (
            A1 * exp(-0.5 * pow(((x1 - mu1) / sigma1), 2))
            + shift
            + A2 * exp(-0.5 * pow(((x2 - mu2) / sigma2), 2))
            - A2 * exp(-0.5 * pow(((x1 - mu2) / sigma2), 2))
            + a * (x - x2)
            + d * pow((x - x2), 2)
        )
        * (erf(999 * (x - x2)) + 1)
        / 2
        * b
        + c * (erf(999 * (x - x2)) + 1)
    )
    """
    expr = expr.replace(" ", "").replace("\n", "")
    for param in names:
        expr = expr.replace(param, f"({values[param]:.8f})")
    return expr


def fit(x, y, yerr, region):
    from iminuit.cost import LeastSquares

    pars = [
        15.326779716529904,
        48.98982871467474,
        -0.20521759318476512,
        -0.27080334546635754,
        4.919694893153201,
        39.93516347442004,
        2.8927030952074255,
        16.713413742339167,
        1.1223000047822258,
        -0.000211926613930679,
        1.0,
        0,
        0,
    ]

    mask = x < 200
    ls = LeastSquares(x[mask], y[mask], yerr[mask], old_func)
    m = iminuit.Minuit(ls, *pars)

    m.fixed["b"] = True
    m.fixed["c"] = True

    if "1J" in region:
        m.fixed["d"] = True
        m.migrad()
        m.hesse()
        m.fixed["d"] = False

    m.migrad()
    m.hesse()
    print(region)
    print(m)
    return m.parameters, m.values


# -----------------------------------------------------------------------------
# Build reweighting targets separately for ggF and VBF
# -----------------------------------------------------------------------------
for category, category_regions in REGION_MAP.items():
    data[category] = {}
    big_histos[category] = {}

    for njet, region_name in category_regions.items():
        histos = read_region_hists(region_name)

        if len(mcs) != 1:
            num = histos["data"] - np.sum([histos[mc] for mc in mcs if mc != "DY"], axis=0)
        else:
            num = histos["data"]

        den = histos["DY"]

        num = num / np.sum(num)
        den = den / np.sum(den)
        rwgt = num / den

        data[category][njet] = rwgt
        big_histos[category][njet] = histos

centers = 0.5 * (edges[:-1] + edges[1:])

# -----------------------------------------------------------------------------
# Fit each category / njet
# -----------------------------------------------------------------------------
formula_map = {}
corr_values = {}

for category, category_data in data.items():
    formula_map[category] = {}
    corr_values[category] = {}

    for njet, rwgt in category_data.items():
        region_label = f"{category}_{njet}J"
        params, values = fit(
            centers,
            unp.nominal_values(rwgt),
            unp.std_devs(rwgt),
            region_label,
        )

        formula_map[category][njet] = get_string_fit(params, values)
        popt = values[:]

        fig, ax = plt.subplots(2, 1, figsize=(8, 8), dpi=150, sharex=True)

        ax[0].errorbar(
            centers,
            unp.nominal_values(rwgt),
            yerr=unp.std_devs(rwgt),
            xerr=0.5 * (edges[1:] - edges[:-1]),
            color="black",
            marker="o",
            markersize=4,
        )
        ax[0].plot(
            centers,
            old_func(centers, *popt),
            color="red",
            label="Fit",
        )
        ax[0].set_ylim(0.5, 1.5)
        ax[0].set_ylabel("Data / DY")
        ax[0].set_title(f"Reweighting factor {category}, {njet}J")

        # closure before / after correction
        if len(mcs) != 1:
            den_old = (
                np.sum([big_histos[category][njet][mc] for mc in mcs if mc != "DY"], axis=0)
                + big_histos[category][njet]["DY"]
            )
        else:
            den_old = big_histos[category][njet]["DY"]

        old_ratio = big_histos[category][njet]["data"] / den_old

        ax[1].errorbar(
            centers,
            unp.nominal_values(old_ratio),
            yerr=unp.std_devs(old_ratio),
            xerr=0.5 * (edges[1:] - edges[:-1]),
            color="black",
            marker="o",
            markersize=4,
            label="Before",
        )

        correction = old_func(centers, *popt)
        corr_values[category][njet] = correction

        if len(mcs) != 1:
            den_new = (
                np.sum([big_histos[category][njet][mc] for mc in mcs if mc != "DY"], axis=0)
                + big_histos[category][njet]["DY"] * correction
            )
        else:
            den_new = big_histos[category][njet]["DY"] * correction

        new_ratio = big_histos[category][njet]["data"] / den_new

        ax[1].errorbar(
            centers,
            unp.nominal_values(new_ratio),
            yerr=unp.std_devs(new_ratio),
            xerr=0.5 * (edges[1:] - edges[:-1]),
            color="red",
            marker="o",
            markersize=4,
            label="After",
        )
        ax[1].set_ylim(0.8, 1.2)
        ax[1].set_xlabel(var)
        ax[1].set_ylabel("Reweighted Data / MC")
        ax[1].legend()

        plt.savefig(f"plots_{year}/rwgt_ptll_{category}_{njet}j.png")
        plt.close()

# -----------------------------------------------------------------------------
# Build correctionlib correction
# -----------------------------------------------------------------------------
# The evaluator will accept:
#   evaluate(category, njet, ptll)
#
# For ggF:
#   njet is binned as 0, 1, >=2
#
# For VBF:
#   one single formula is used (the >=2j VBF region), so njet is ignored there.
ptll_rwgt = cs.Correction(
    name="ptll_rwgt",
    description=(
        f"Weights to be applied on DY MC samples for era {year}. "
        "Derived separately in ggF_Z and VBF_Z regions. "
        "ggF uses 0j/1j/>=2j categories; VBF uses the >=2j category."
    ),
    version=1,
    inputs=[
        cs.Variable(
            name="category",
            type="string",
            description='Production category: "ggF" or "VBF"',
        ),
        cs.Variable(
            name="njet",
            type="int",
            description="Number of reco level jets > 25 GeV",
        ),
        cs.Variable(
            name="ptll",
            type="real",
            description="Reco pTll",
        ),
    ],
    output=cs.Variable(name="sf", type="real", description=""),
    data=cs.Category(
        nodetype="category",
        input="category",
        content=[
            cs.CategoryItem(
                key="ggF",
                value=cs.Binning(
                    nodetype="binning",
                    input="njet",
                    edges=[-0.5, 0.5, 1.5, 999],
                    flow="clamp",
                    content=[
                        cs.Formula(
                            nodetype="formula",
                            variables=["ptll"],
                            parser="TFormula",
                            expression=formula_map["ggF"][0],
                        ),
                        cs.Formula(
                            nodetype="formula",
                            variables=["ptll"],
                            parser="TFormula",
                            expression=formula_map["ggF"][1],
                        ),
                        cs.Formula(
                            nodetype="formula",
                            variables=["ptll"],
                            parser="TFormula",
                            expression=formula_map["ggF"][2],
                        ),
                    ],
                ),
            ),
            cs.CategoryItem(
                key="VBF",
                value=cs.Formula(
                    nodetype="formula",
                    variables=["ptll"],
                    parser="TFormula",
                    expression=formula_map["VBF"][2],
                ),
            ),
        ],
    ),
)

rich.print(ptll_rwgt)

# -----------------------------------------------------------------------------
# Closure plots from correctionlib
# -----------------------------------------------------------------------------
evaluator = ptll_rwgt.to_evaluator()

for category, category_data in data.items():
    for njet, rwgt in category_data.items():
        corrs = evaluator.evaluate(category, njet, centers)

        plt.errorbar(
            centers,
            unp.nominal_values(rwgt),
            yerr=unp.std_devs(rwgt),
            color="black",
            marker="o",
            markersize=4,
            label=f"{category} {njet}J",
        )
        plt.plot(centers, corrs, color="red", label="correctionlib")

        tformula = ROOT.TFormula(f"test_{category}_{njet}J", formula_map[category][njet])
        corrs_tformula = np.zeros_like(centers)
        for i, center in enumerate(centers):
            corrs_tformula[i] = tformula.Eval(float(center))

        plt.plot(centers, corrs_tformula, color="green", label="TFormula")
        plt.legend()
        plt.savefig(f"plots_{year}/closure_ptll_{category}_{njet}j.png")
        plt.close()

# -----------------------------------------------------------------------------
# njet correction (left unchanged; baseline DY -> data)
# -----------------------------------------------------------------------------
var = "njet"
histos = {}
region = "baseline"

edges_njet = None
for mc in mcs + ["data"]:
    h = f[f"{region}/{var}/histo_{mc}"].to_hist()
    vals = h.values(True)
    vals[1] += vals[0]
    vals[-2] += vals[-1]
    vals = vals[1:-1]
    histos[mc] = vals

    if edges_njet is None:
        edges_njet = h.axes[0].edges - 0.5

if len(mcs) != 1:
    num = histos["data"] - np.sum([histos[mc] for mc in mcs if mc != "DY"], axis=0)
else:
    num = histos["data"]

den = histos["DY"]

num = num / np.sum(num)
den = den / np.sum(den)
rwgt = num / den

assert len(rwgt) == len(edges_njet) - 1

centers_njet = 0.5 * (edges_njet[:-1] + edges_njet[1:])
plt.figure(figsize=(8, 6), dpi=150)
plt.errorbar(
    centers_njet,
    rwgt,
    xerr=0.5 * (edges_njet[1:] - edges_njet[:-1]),
    color="black",
    marker="o",
    markersize=4,
)
plt.ylim(0.5, 1.5)
plt.xlabel(var)
plt.ylabel("Data / DY")
plt.savefig(f"plots_{year}/rwgt_njet.png")
plt.close()

h_corr = hist.Hist(
    hist.axis.Variable(edges_njet, name="njet"),
    data=np.array(rwgt),
)
h_corr.name = "njet_rwgt"
h_corr.label = "out"

njet_rwgt = correctionlib.convert.from_histogram(h_corr)
njet_rwgt.description = "Reweights njet distribution from DY to match data"
njet_rwgt.data.flow = "clamp"
rich.print(njet_rwgt)

# -----------------------------------------------------------------------------
# Write correction set
# -----------------------------------------------------------------------------
cset = cs.CorrectionSet(
    schema_version=2,
    description="Custom DY corrections",
    corrections=[
        ptll_rwgt,
        njet_rwgt,
    ],
)

with open(f"rwgts/{year}.json", "w") as fout:
    fout.write(cset.model_dump_json(exclude_unset=True))