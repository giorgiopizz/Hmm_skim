import argparse

import hist
import uproot
import matplotlib.pyplot as plt
import numpy as np
import os
import mplhep as hep
from config import get_config
from productions.lumis import lumis
import concurrent.futures

hep.style.use(hep.style.CMS)


parser = argparse.ArgumentParser()
parser.add_argument("--year", type=str, help="Year of the production", required=True)
parser.add_argument(
    "--ptll", action="store_true", help="Whether to apply ptll reweighting"
)
parser.add_argument(
    "--lin", action="store_true", help="Whether to use linear scale for the plots"
)
args = parser.parse_args()
year = args.year
apply_ptll = args.ptll
use_linear_scale = args.lin

datasets, variables, regions, _ = get_config(year, apply_ptll)


plots_folder = f"plots_{year}"
os.makedirs(plots_folder, exist_ok=True)

lumi = round(lumis[year], 2)

fname = f"roots/{year}.root"
if not apply_ptll:
    fname = f"roots/{year}_extract_ptll.root"
f = uproot.open(fname)

# f_old = uproot.open(f"roots/{year}_correct.root")
# f = uproot.open(f"roots/{year}_correct.root")

mcs = []
for ds in datasets:
    if ds != "data":
        mcs.append(ds)


def make_plot(region, var):
    histos = {}
    # if region != "baseline":
    #     return
    # if var != "mll":
    #     return

    mc_sum = 0
    for mc in mcs + ["data"]:
        # if mc == "data" or 'DY' in mc:
        #     histos[mc] = f_old[f"{region}/{var}/histo_{mc}"].to_hist()
        # else:
        #     histos[mc] = f[f"{region}/{var}/histo_{mc}"].to_hist()

        try:
            histos[mc] = f[f"{region}/{var}/histo_{mc}"].to_hist()
        except KeyError:
            print(f"Warning: histogram for {mc} not found in {region}/{var}")
            continue

    #     histos[mc] = histos[mc][hist.rebin(2)]
    #     histos[mc] = histos[mc][hist.loc(86) : hist.loc(96)]
    #     if mc != "data":
    #         mc_sum += histos[mc].values(True).sum()
    # a = histos["data"].view(True)
    # a[:] = a[:] / np.sum(a[:])
    # scale = 1 / mc_sum
    # for mc in mcs:
    #     a = histos[mc].view(True)
    #     # scale = 1 / a.value.sum()
    #     a.value = a.value * scale
    #     a.variance = a.variance * scale**2

    ds = list(histos.keys())[0]
    edges = histos[ds].axes[0].edges
    centers = histos[ds].axes[0].centers

    fig, ax = plt.subplots(
        2,
        1,
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
        dpi=150,
    )
    hep.cms.label(
        f"Preliminary {region}",
        data=True,
        lumi=lumi,
        ax=ax[0],
        year=year,
        com=13.6,
    )
    fig.tight_layout(pad=-0.5)

    if "data" in histos:
        integral = round(histos["data"].values(True).sum(), 2)
        ax[0].errorbar(
            centers,
            histos["data"].values(),
            yerr=np.sqrt(histos["data"].variances()),
            # yerr=0,
            fmt="o",
            label=f"Data [{integral}]",
            markersize=3,
            color="black",
        )

    hlast = 0
    i = 1
    for mc in mcs:
        scale = 1.0

        if mc == "DY":
            scale = 1.0
            # if year == "2025":
            #     scale = 0.9476613109

        if isinstance(hlast, int):
            hlast = scale * histos[mc].copy()
        else:
            hlast += scale * histos[mc]
        color = datasets[mc].get("color", None)
        integral = round(histos[mc].values(True).sum(), 2)
        if datasets[mc].get("is_signal", False):
            ax[0].stairs(
                histos[mc].values(),
                histos[mc].axes[0].edges,
                label=f"{mc} [{integral}]",
                zorder=i,
                linewidth=3,
                color=color,
            )
        else:
            ax[0].stairs(
                hlast.values(),
                hlast.axes[0].edges,
                label=f"{mc} [{integral}]",
                zorder=-i,
                fill=True,
                color=color,
            )
        i += 1

    ax[0].set_ylabel("Events")
    if not use_linear_scale:
        ax[0].set_yscale("log")
        ymin = 0.1
        ymax = min(1e3 * hlast.values().max(), 1e12)
        if ymax < ymin:
            ymax = 10 * ymin

        # ymin = 1e-5
        # ymax = 2

        ax[0].set_ylim(ymin, ymax)
    else:
        ymin = 0.0
        ymax = min(
            # 1.35 * max(histos["data"].values().max(), hlast.values().max()),
            1.35 * hlast.values().max(),
            1e12,
        )
        if ymax < ymin:
            ymax = 10 * ymin
        ax[0].set_ylim(ymin, ymax)
    ax[0].legend(loc="upper center", ncols=3, frameon=True)

    ax[0].set_xlim(edges[0], edges[-1])

    # if var == "ptl1" or var == "ptl2":
    #     ax[0].set_xlim(26, 100)
    # if var == "mll":
    #     ax[0].set_xlim(86, 96)
    # if var == "ptll":
    #     ax[0].set_xlim(0, 200)

    if "data" in histos:
        # ratio
        ratio = histos["data"].values() / hlast.values()
        ratio_err = np.sqrt((histos["data"].variances())) / hlast.values()
        ratio_err = np.where(ratio_err < 0.0, 1e-3, ratio_err)
        # ratio_err = np.zeros_like(ratio_err)
        ax[1].errorbar(
            centers,
            ratio,
            yerr=ratio_err,
            fmt="o",
            markersize=4,
            color="black",
        )
        ax[1].plot(edges, np.ones_like(edges), "--", color="gray")
        ax[1].set_xlabel(variables[var]["xlabel"])
        ax[1].set_ylabel("Data/MC")
        delta = 1
        delta = 0.2
        if "j" in var:
            delta = 0.5
        ax[1].set_ylim(1 - delta, 1 + delta)

    filename = f"{plots_folder}/{region}_{var}.png"
    if use_linear_scale:
        filename = f"{plots_folder}/lin_{region}_{var}.png"
    plt.savefig(filename, bbox_inches="tight", dpi=120)
    plt.close()


with concurrent.futures.ProcessPoolExecutor(max_workers=18) as executor:
    tasks = []
    for region in regions:
        if regions[region].get("skip_fill", False):
            continue
        for var in variables:
            tasks.append(executor.submit(make_plot, region, var))
    concurrent.futures.wait(tasks)
    for task in tasks:
        task.result()
