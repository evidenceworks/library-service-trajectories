"""Regenerate Figures 1–4 from reproduced scientific values."""

from pathlib import Path
import argparse, csv
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--preview", type=Path, help="Also write PNG previews to this directory."
)
args = parser.parse_args()
F = ROOT / "figures"
F.mkdir(exist_ok=True)
families = {font.name for font in font_manager.fontManager.ttflist}
font_family = next(
    name
    for name in ["Nimbus Roman", "Times New Roman", "Liberation Serif", "DejaVu Serif"]
    if name in families
)
plt.rcParams["svg.hashsalt"] = "library-service-trajectories"
plt.rcParams.update(
    {
        "font.family": font_family,
        "font.size": 9.3,
        "axes.titlesize": 10,
        "axes.labelsize": 9.3,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)
colors = {"declining": "#0072B2", "nondeclining": "#D55E00"}
labels = {"declining": "Prior contraction", "nondeclining": "Other population history"}


def read(n):
    mapping = {
        "annual_and_endpoint_changes.csv": ROOT / "figure-data/endpoint-changes.csv",
        "annual_national_domains.csv": ROOT / "results/annual-totals.csv",
        "denominator_decomposition.csv": ROOT
        / "figure-data/denominator-components.csv",
    }
    with mapping[n].open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if n != "annual_national_domains.csv":
        for row in rows:
            row["source_scenario"] = "published_accounting"
    return rows


def save(fig, name):
    name = name.lower().replace("_", "-")
    fig.savefig(F / (name + ".svg"), metadata={"Creator": None, "Date": None})
    if args.preview:
        args.preview.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            args.preview / (name + ".png"), dpi=150, metadata={"Software": None}
        )
    plt.close(fig)


handles = [
    Line2D(
        [0],
        [0],
        marker="o" if k == "declining" else "^",
        color="none",
        markerfacecolor=v,
        markeredgecolor=v,
        label=labels[k],
        markersize=5,
    )
    for k, v in colors.items()
]
C = read("annual_and_endpoint_changes.csv")
fig, axs = plt.subplots(1, 2, figsize=(6.7, 4.2), sharex=True, sharey=True)
fig.subplots_adjust(left=0.11, right=0.98, bottom=0.29, top=0.86, wspace=0.14)
for ax, year, panel in zip(axs, ["2022", "2023"], ["A", "B"]):
    rr = [
        r
        for r in C
        if r["source_scenario"] == "published_accounting"
        and r["start_year"] == year
        and r["end_year"] == "2025"
        and r["field"] in ["staff_service_hours", "total_hours"]
        and r["common_territory_id"] != "CRT_755"
    ]
    indexed = {(r["common_territory_id"], r["field"]): r for r in rr}
    for ctx in colors:
        ids = [
            r["common_territory_id"]
            for r in rr
            if r["field"] == "staff_service_hours" and r["population_context"] == ctx
        ]
        x = [float(indexed[(i, "total_hours")]["lower_per_1000_baseline"]) for i in ids]
        y = [
            float(indexed[(i, "staff_service_hours")]["lower_per_1000_baseline"])
            for i in ids
        ]
        ax.scatter(
            x,
            y,
            s=14,
            c=colors[ctx],
            marker="o" if ctx == "declining" else "^",
            alpha=0.65,
            linewidths=0.25,
            edgecolors="white",
        )
    ax.axhline(0, color="#555555", lw=0.7)
    ax.axvline(0, color="#555555", lw=0.7)
    ax.set(
        xlim=(-2200, 5100),
        ylim=(-750, 1450),
        xlabel="Total opening change",
        title=panel + ". " + year + "–2025",
    )
    ax.grid(alpha=0.12, linewidth=0.5)
axs[0].set_ylabel("Staffed-service change")
fig.legend(
    handles=handles,
    loc="upper center",
    ncol=2,
    frameon=False,
    bbox_to_anchor=(0.55, 0.99),
)
fig.text(
    0.5,
    0.15,
    "Both axes: hours per 1,000 fixed 2022 residents",
    ha="center",
    fontsize=9.3,
)
fig.text(
    0.1,
    0.07,
    "Siuntio: both endpoint changes have no finite upper bound.\nIts joint domain remains unresolved; it is not an origin point.",
    fontsize=8.8,
)
save(fig, "Figure_1")
A = read("annual_national_domains.csv")
names = {
    "staff_service_hours": "A. Staffed service (S)",
    "staff_present_no_service_hours": "B. Staff present without service (M)",
    "no_library_staff_hours": "C. Without library-paid staff (U)",
    "total_hours": "D. Total opening (T)",
}
fig, axs = plt.subplots(2, 2, figsize=(6.7, 5.25))
fig.subplots_adjust(
    left=0.11, right=0.97, bottom=0.21, top=0.89, hspace=0.6, wspace=0.29
)
for ax, (field, title) in zip(axs.flat, names.items()):
    vals = []
    for ctx in colors:
        rr = [
            r
            for r in A
            if r["source_scenario"] == "published_accounting"
            and r["population_context"] == ctx
            and r["field"] == field
        ]
        rr.sort(key=lambda r: r["year"])
        xs = [int(r["year"]) for r in rr]
        ys = [float(r["lower_sum"]) / 1000 for r in rr]
        vals.extend(ys)
        ax.plot(xs[:3], ys[:3], color=colors[ctx], lw=1, alpha=0.85)
        if rr[-1]["upper_sum"] != "unbounded":
            ax.plot(xs[-2:], ys[-2:], color=colors[ctx], lw=1)
        for x, y, r in zip(xs, ys, rr):
            symbol = (
                "v"
                if r["upper_sum"] == "unbounded"
                else ("o" if r["wholly_observed_sum"] else "s")
            )
            ax.plot(
                x,
                y,
                marker=symbol,
                ms=4.5,
                color=colors[ctx],
                mfc="white" if symbol == "s" else colors[ctx],
            )
            rel = next(
                t
                for t in A
                if t["source_scenario"] == "conservative_relaxation"
                and t["population_context"] == ctx
                and t["field"] == field
                and t["year"] == r["year"]
            )
            if rel["upper_sum"] != "unbounded" and rel["lower_sum"] != rel["upper_sum"]:
                lo = float(rel["lower_sum"]) / 1000
                up = float(rel["upper_sum"]) / 1000
                ax.plot([x + 0.06, x + 0.06], [lo, up], color=colors[ctx], ls=":", lw=2)
                vals.extend([lo, up])
    span = max(vals) - min(vals)
    top = max(vals) + max(span * 0.45, 8)
    bottom = max(0, min(vals) - max(span * 0.1, 3))
    ax.set_ylim(bottom, top)
    r = next(
        r
        for r in A
        if r["source_scenario"] == "published_accounting"
        and r["population_context"] == "nondeclining"
        and r["field"] == field
        and r["year"] == "2025"
    )
    y = float(r["lower_sum"]) / 1000
    ax.annotate(
        "unbounded",
        xy=(2025, y + max(span * 0.32, 6)),
        xytext=(2024.91, y + max(span * 0.12, 2)),
        color=colors["nondeclining"],
        ha="right",
        fontsize=8.8,
        arrowprops={"arrowstyle": "->", "color": colors["nondeclining"], "lw": 0.9},
    )
    ax.set(
        xlim=(2021.75, 2025.3),
        xticks=[2022, 2023, 2024, 2025],
        ylabel="Thousand service-location hours",
        title=title,
    )
    ax.grid(alpha=0.12, linewidth=0.5)
fig.legend(
    handles=handles,
    loc="upper center",
    ncol=2,
    frameon=False,
    bbox_to_anchor=(0.55, 0.99),
)
fig.text(
    0.1,
    0.105,
    "● observed sum    □ accounting-conditioned value\n▼ lower bound with no finite upper limit    dotted: conservative mode domain",
    fontsize=8.8,
)
fig.text(
    0.1,
    0.04,
    "Separate source domains are shown without pooling. All national 2025 hour\ntotals are unbounded above because the other-history context includes Siuntio.",
    fontsize=8.8,
)
save(fig, "Figure_2")
fig, ax = plt.subplots(figsize=(6.7, 2.9))
fig.subplots_adjust(left=0.12, right=0.97, bottom=0.22, top=0.81)
for ctx in colors:
    rr = sorted(
        [
            r
            for r in A
            if r["source_scenario"] == "published_accounting"
            and r["population_context"] == ctx
            and r["field"] == "paid_fte"
        ],
        key=lambda r: r["year"],
    )
    ax.plot(
        [int(r["year"]) for r in rr],
        [float(r["lower_sum"]) for r in rr],
        marker="o" if ctx == "declining" else "^",
        color=colors[ctx],
        lw=1.2,
        ms=5,
        label=labels[ctx],
    )
ax.set(xticks=[2022, 2023, 2024, 2025], ylabel="Library-paid worked FTE", xlabel="Year")
ax.grid(alpha=0.12, linewidth=0.5)
fig.legend(
    handles=handles,
    loc="upper center",
    ncol=2,
    frameon=False,
    bbox_to_anchor=(0.55, 0.99),
)
fig.text(
    0.12,
    0.025,
    "All FTE totals are observed. Both source scenarios give identical values.",
    fontsize=8.8,
)
save(fig, "Figure_3")
K = read("denominator_decomposition.csv")
fig, axs = plt.subplots(2, 2, figsize=(6.7, 5.4))
fig.subplots_adjust(
    left=0.12, right=0.97, bottom=0.24, top=0.88, hspace=0.45, wspace=0.3
)
for row, (field, lab) in enumerate(
    [("staff_service_hours", "Staffed service"), ("total_hours", "Total opening")]
):
    for col, year in enumerate(["2022", "2023"]):
        ax = axs[row, col]
        rr = [
            r
            for r in K
            if r["source_scenario"] == "published_accounting"
            and r["start_year"] == year
            and r["field"] == field
            and r["common_territory_id"] != "CRT_755"
        ]
        index = {(r["common_territory_id"], r["component"]): r for r in rr}
        for ctx in colors:
            ids = sorted(
                {
                    r["common_territory_id"]
                    for r in C
                    if r["start_year"] == year
                    and r["end_year"] == "2025"
                    and r["population_context"] == ctx
                    and r["field"] == field
                    and r["common_territory_id"] != "CRT_755"
                }
            )
            ax.scatter(
                [float(index[(i, "hours_component")]["lower_per_1000"]) for i in ids],
                [
                    float(index[(i, "population_component")]["lower_per_1000"])
                    for i in ids
                ],
                s=12,
                color=colors[ctx],
                marker="o" if ctx == "declining" else "^",
                alpha=0.65,
                linewidths=0.2,
                edgecolor="white",
            )
        ax.axhline(0, color="#555555", lw=0.7)
        ax.axvline(0, color="#555555", lw=0.7)
        ax.grid(alpha=0.12, linewidth=0.5)
        ax.set(
            title=chr(65 + row * 2 + col) + ". " + lab + ", " + year + "–2025",
            xlabel="Hours component",
            ylabel="Population component",
        )
        ax.set_xlim((-750, 1500) if row == 0 else (-2200, 5500))
        ax.set_ylim((-160, 160) if row == 0 else (-550, 550))
fig.legend(
    handles=handles,
    loc="upper center",
    ncol=2,
    frameon=False,
    bbox_to_anchor=(0.55, 0.99),
)
fig.text(
    0.5,
    0.135,
    "Both components: hours per 1,000 current residents; their sum is ratio change",
    ha="center",
    fontsize=8.8,
)
fig.text(
    0.1,
    0.045,
    "Siuntio retains one shared endpoint source domain. Components\nare linked by the same unknown hours; marginal limits are not independent.",
    fontsize=8.8,
)
save(fig, "Figure_4")
print("Regenerated Figures 1–4 using " + font_family + ".")
