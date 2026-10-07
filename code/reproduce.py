"""Reproduce reported results from deposited analytic records."""

from pathlib import Path
from tempfile import TemporaryDirectory
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import argparse, json, time
from support import read, write, dump
from domains import FIELDS, MODES, OBSERVED, q, text, row_domain, add
from analysis import (
    SCENARIOS,
    trajectories,
    aggregates,
    reporting,
    projections,
    observed,
)

ROOT = Path(__file__).resolve().parents[1]


def assemble(root, out):
    """Keep documentary territories fixed; aggregate each source record once."""
    frame = {r["common_territory_id"]: r for r in read(root / "data/territories.csv")}
    panel = read(root / "data/territory-panel.csv.gz")
    records = read(root / "data/source-records.csv.gz")
    byid = {r["record_id"]: r for r in records}
    assert (
        len(frame) == 268 and len(panel) == 1340 and len(byid) == len(records) == 1384
    )
    contexts, annual, domains, identities, fte = {}, {}, [], [], []
    seen = set()
    for row in panel:
        sid, year = row["common_territory_id"], int(row["year"])
        row["year"] = year
        ids = row["source_record_ids"].split("|")
        assert ids == frame[sid][f"source_records_{year}"].split("|")
        rs = [byid[rid] for rid in ids]
        for r in rs:
            assert r["record_id"] not in seen and r["common_territory_id"] == sid
            assert r["year"] == str(year) and r["level"] == "system_row"
            seen.add(r["record_id"])
        n17, n22 = (
            q(row["population_2017_accepted"]),
            q(row["population_2022_accepted"]),
        )
        assert min(n17, n22) > 0
        with localcontext() as ctx:
            ctx.prec = 60
            growth = (
                Decimal(n22.numerator)
                * Decimal(n17.denominator)
                / Decimal(n22.denominator)
                / Decimal(n17.numerator)
            ).ln() / 5
        group = "declining" if n22 < n17 else "nondeclining"
        assert row["population_context"] == group and row[
            "prior_annualized_population_change"
        ] == str(growth)
        contexts[sid] = {
            "population_2017": n17,
            "population_2022": n22,
            "g": str(growth),
            "population_context": group,
            "frame": frame[sid],
        }
        nraw, _ = observed(rs, "population")
        assert nraw is not None and q(row["population_raw_source_sum"]) == nraw
        population = n17 if year == 2017 else n22 if year == 2022 else nraw
        assert q(row["population_accepted"]) == population
        if year == 2017:
            assert all(row[field] == "" for field in (*FIELDS, "paid_fte"))
            continue
        for field in (*FIELDS, "paid_fte"):
            value, known = observed(rs, field)
            assert row[field] == (text(value) if value is not None else "")
            row[field + "_state"] = (
                "observed_source_sum" if value is not None else "contains_source_blank"
            )
        complete = all(row[k] != "" for k in FIELDS)
        residual = (
            q(row["total_hours"]) - sum((q(row[k]) for k in MODES), Q(0))
            if complete
            else None
        )
        if complete:
            assert residual == 0
        identities.append(
            {
                "common_territory_id": sid,
                "year": year,
                "status": "observed_exact_equality"
                if complete
                else "incomplete_source_vector",
                "residual_hours": text(residual) if residual is not None else "",
                "unknown_fields": "|".join(k for k in FIELDS if row[k] == ""),
                "source_record_ids": "|".join(ids),
                "baseline_population_2022": text(n22),
                "population_context": group,
            }
        )
        fv = q(row["paid_fte"])
        fte.append(
            {
                "common_territory_id": sid,
                "year": year,
                "paid_fte": text(fv),
                "paid_fte_per_1000_baseline": text(fv * 1000 / n22),
                "availability": "observed",
                "source_record_ids": "|".join(ids),
                "meaning": "library-paid worked FTE, not an hours imputation",
            }
        )
        for scenario in SCENARIOS:
            ds = [row_domain(r, scenario) for r in rs]
            bounds = {field: add(d[0][field] for d in ds) for field in FIELDS}
            bounds["paid_fte"] = (fv, fv)
            constraints = {r["record_id"]: d[1] for r, d in zip(rs, ds)}
            annual[(sid, year, scenario)] = {
                "domains": bounds,
                "population": population,
                "row": row,
                "joint": constraints,
            }
            for field in FIELDS:
                lo, hi = bounds[field]
                domains.append(
                    {
                        "common_territory_id": sid,
                        "year": year,
                        "source_scenario": scenario,
                        "field": field,
                        "observed_value": row[field],
                        "observation_state": row[field + "_state"],
                        "lower_hours": text(lo),
                        "upper_hours": text(hi),
                        "lower_per_1000_baseline": text(lo * 1000 / n22),
                        "upper_per_1000_baseline": text(hi * 1000 / n22)
                        if hi is not None
                        else "unbounded",
                        "joint_constraints": json.dumps(constraints, sort_keys=True),
                        "meaning": "domain, not a filled native observation",
                    }
                )
    assert seen == set(byid)
    assert len(annual) == 2144
    write(out / "outputs/annual_domains.csv", domains)
    write(out / "outputs/annual_identities.csv", identities)
    write(out / "outputs/fte_trajectories.csv", fte)
    coverage = []
    for year in (2022, 2023, 2024, 2025):
        rs = [r for r in panel if r["year"] == year]
        for field in (*FIELDS, "paid_fte", "population_accepted"):
            unknown = [r for r in rs if r[field] == ""]
            coverage.append(
                {
                    "year": year,
                    "field": field,
                    "frame_territories": 268,
                    "observed_territories": 268 - len(unknown),
                    "unresolved_territories": len(unknown),
                    "unresolved_baseline_population_2022": text(
                        sum((q(r["population_2022_accepted"]) for r in unknown), Q(0))
                    ),
                    "unresolved_current_population": text(
                        sum((q(r["population_accepted"]) for r in unknown), Q(0))
                    ),
                    "unresolved_ids": "|".join(
                        r["common_territory_id"] for r in unknown
                    ),
                    "marker": "source blank; not zero",
                }
            )
    write(out / "outputs/coverage_and_unresolved_footprints.csv", coverage)
    return frame, contexts, annual, records


RESULT_FILES = {
    "context_differences.csv": "event-differences.csv",
    "event_prevalence.csv": "event-prevalence.csv",
    "annual_national_domains.csv": "annual-totals.csv",
    "denominator_reversal_counts.csv": "denominator-reversals.csv",
    "fte_event_diagnostic.csv": "event-staffing.csv",
    "region_leave_one_out_differences.csv": "region-omission-differences.csv",
    "projection_coefficient_domains.csv": "projection-domains.csv",
    "projection_models.json": "projection-models.json",
    "projection_region_support.csv": "projection-support.csv",
    "unknown_event_witnesses.json": "unknown-event-witnesses.json",
}


def export_results(root, out):
    for source, destination in RESULT_FILES.items():
        (root / "results" / destination).write_bytes(
            (out / "outputs" / source).read_bytes()
        )
    patterns = read(out / "outputs/trajectory_patterns.csv")
    categories = [field + "_direction" for field in (*FIELDS, "paid_fte")]
    categories += [
        "staffed_and_unstaffed_both_increase",
        "staffed_and_total_both_decline",
    ]
    counts = Counter()
    for r in patterns:
        if (r["start_year"], r["end_year"]) not in [("2022", "2025"), ("2023", "2025")]:
            continue
        for group in (r["population_context"], "all"):
            for category in categories:
                counts[
                    (
                        r["source_scenario"],
                        r["start_year"],
                        r["end_year"],
                        group,
                        category,
                        r[category],
                    )
                ] += 1
    write(
        root / "results/trajectory-summary.csv",
        [
            dict(
                zip(
                    [
                        "source_scenario",
                        "start_year",
                        "end_year",
                        "population_context",
                        "category",
                        "value",
                    ],
                    key,
                ),
                territories=count,
            )
            for key, count in sorted(counts.items())
        ],
    )
    changes = [
        {
            k: r[k]
            for k in [
                "common_territory_id",
                "start_year",
                "end_year",
                "field",
                "population_context",
                "lower_per_1000_baseline",
                "upper_per_1000_baseline",
                "baseline_population_2022",
            ]
        }
        for r in read(out / "outputs/annual_and_endpoint_changes.csv")
        if r["source_scenario"] == "published_accounting"
        and r["start_year"] in ["2022", "2023"]
        and r["end_year"] == "2025"
        and r["field"] in ["staff_service_hours", "total_hours"]
    ]
    write(root / "figure-data/endpoint-changes.csv", changes)
    components = [
        {
            k: r[k]
            for k in [
                "common_territory_id",
                "start_year",
                "end_year",
                "field",
                "component",
                "lower_per_1000",
                "upper_per_1000",
                "lower_exact_per_resident",
                "upper_exact_per_resident",
                "population_start",
                "population_end",
                "joint_constraint",
            ]
        }
        for r in read(out / "outputs/denominator_decomposition.csv")
        if r["source_scenario"] == "published_accounting"
    ]
    write(root / "figure-data/denominator-components.csv", components)


def reproduce(root=ROOT):
    from check import check_inputs, compare_calculations, check_results

    root = Path(root)
    start = time.perf_counter()
    check_inputs(root)
    with TemporaryDirectory(prefix="library-trajectories-") as directory:
        out = Path(directory)
        frame, contexts, annual, records = assemble(root, out)
        events, patterns = trajectories(out, frame, contexts, annual)
        aggregates(out, contexts, annual, events, patterns)
        reporting(records, out, frame)
        projections(out, contexts, annual)
        parity = compare_calculations(root, out)
        export_results(root, out)
    check_results(root)
    print(f"Reproduced reported results in {time.perf_counter() - start:.2f} seconds.")
    return parity


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    reproduce(args.root)
