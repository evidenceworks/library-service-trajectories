"""Territory trajectories, logical source domains and descriptive comparisons."""

from pathlib import Path
from collections import defaultdict, Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import json
import numpy as np
from support import read, write, dump, sha, YEARS
from domains import (
    FIELDS,
    MODES,
    OBSERVED,
    q,
    text,
    exact,
    row_domain,
    add,
    change,
    event_bounds,
)
from arithmetic import (
    lower_text,
    lower_exact,
    upper_exact,
    decomposition_bounds,
    denominator_reversal_bounds,
)
from summaries import summarize

SCENARIOS = ("published_accounting", "conservative_relaxation")
ENDPOINTS = ((2022, 2025), (2023, 2025))
CHANGES = ((2022, 2023), (2023, 2024), (2024, 2025), *ENDPOINTS)


def observed(rows, f):
    known = [q(r[f + "_raw"]) for r in rows if r[f + "_state"] in OBSERVED]
    return (sum(known, Q(0)) if len(known) == len(rows) else None, sum(known, Q(0)))


def direction(bs):
    lo, hi = bs
    return (
        "increase"
        if lo is not None and lo > 0
        else "decrease"
        if hi is not None and hi < 0
        else "unchanged"
        if lo == hi == 0
        else "source_unidentified"
    )


def trajectories(out, frame, context, annual):
    changes = []
    decomp = []
    events = []
    patterns = []
    witnesses = []
    reversals = []
    for scenario in SCENARIOS:
        for start, end in CHANGES:
            for sid in sorted(frame):
                a, b = annual[(sid, start, scenario)], annual[(sid, end, scenario)]
                nbase = context[sid]["population_2022"]
                deltas = {}
                for field in (*FIELDS, "paid_fte"):
                    lo, hi = change(a["domains"][field], b["domains"][field])
                    deltas[field] = (lo, hi)
                    changes.append(
                        {
                            "common_territory_id": sid,
                            "start_year": start,
                            "end_year": end,
                            "source_scenario": scenario,
                            "field": field,
                            "lower_absolute_change": lower_text(lo),
                            "upper_absolute_change": text(hi),
                            "lower_exact": lower_exact(lo),
                            "upper_exact": upper_exact(hi),
                            "lower_per_1000_baseline": lower_text(
                                lo * 1000 / nbase if lo is not None else None
                            ),
                            "upper_per_1000_baseline": text(hi * 1000 / nbase)
                            if hi is not None
                            else "unbounded",
                            "direction": direction((lo, hi)),
                            "population_context": context[sid]["population_context"],
                            "baseline_population_2022": text(nbase),
                        }
                    )
                patterns.append(
                    {
                        "common_territory_id": sid,
                        "start_year": start,
                        "end_year": end,
                        "source_scenario": scenario,
                        "population_context": context[sid]["population_context"],
                        **{
                            f + "_direction": direction(deltas[f])
                            for f in (*FIELDS, "paid_fte")
                        },
                        "staffed_and_unstaffed_both_increase": str(
                            direction(deltas["staff_service_hours"])
                            == direction(deltas["no_library_staff_hours"])
                            == "increase"
                        ).lower(),
                        "staffed_and_total_both_decline": str(
                            direction(deltas["staff_service_hours"])
                            == direction(deltas["total_hours"])
                            == "decrease"
                        ).lower(),
                    }
                )
                if (start, end) not in ENDPOINTS:
                    continue
                for field in ("staff_service_hours", "total_hours"):
                    h0, h1 = a["domains"][field], b["domains"][field]
                    n0, n1 = a["population"], b["population"]
                    for component, (lo, hi) in zip(
                        (
                            "total_per_resident_change",
                            "hours_component",
                            "population_component",
                        ),
                        decomposition_bounds(h0, h1, n0, n1),
                    ):
                        decomp.append(
                            {
                                "common_territory_id": sid,
                                "start_year": start,
                                "end_year": end,
                                "source_scenario": scenario,
                                "field": field,
                                "component": component,
                                "lower_per_1000": lower_text(
                                    lo * 1000 if lo is not None else None
                                ),
                                "upper_per_1000": text(hi * 1000)
                                if hi is not None
                                else "unbounded",
                                "lower_exact_per_resident": lower_exact(lo),
                                "upper_exact_per_resident": upper_exact(hi),
                                "population_start": text(n0),
                                "population_end": text(n1),
                                "joint_constraint": "all components use the same H0,H1 state; total=hours+population; marginals not independent",
                            }
                        )
                    for definition in (
                        "absolute_decrease_per_resident_increase",
                        "absolute_increase_per_resident_decrease",
                    ):
                        assert h0[0] == h0[1] and h0[0] > 0
                        lo, hi = denominator_reversal_bounds(h0, h1, n0, n1, definition)
                        reversals.append(
                            {
                                "common_territory_id": sid,
                                "start_year": start,
                                "end_year": end,
                                "source_scenario": scenario,
                                "field": field,
                                "definition": definition,
                                "lower": lo,
                                "upper": hi,
                                "source_uncertainty": str(lo != hi).lower(),
                            }
                        )
                t0, t1 = a["domains"]["total_hours"], b["domains"]["total_hours"]
                s0, s1 = (
                    a["domains"]["staff_service_hours"],
                    b["domains"]["staff_service_hours"],
                )
                assert t0[0] == t0[1] and s0[0] == s0[1]
                for percent in (0, 2, 5):
                    zero = percent > 0 and s0[0] == 0
                    if zero:
                        lo = hi = None
                    elif t1[1] is None or s1[1] is None:
                        # The only actual nonpoint S/T endpoint is the accepted complete unknown
                        # Siuntio vector. Construct both feasible event states under each domain.
                        assert (
                            sid == "CRT_755"
                            and t1 == s1 == (Q(0), None)
                            and t0[0] > 0
                            and s0[0] > 0
                        )
                        lo, hi = 0, 1
                        witnesses.append(
                            {
                                "common_territory_id": sid,
                                "start_year": start,
                                "source_scenario": scenario,
                                "decline_threshold_percent": percent,
                                "event_true_endpoint": {
                                    "T": text(t0[0]),
                                    "S": "0",
                                    "M": "0",
                                    "U": text(t0[0]),
                                },
                                "event_false_endpoint": {
                                    "T": "0",
                                    "S": "0",
                                    "M": "0",
                                    "U": "0",
                                },
                                "meaning": "feasible joint source-domain witnesses, not imputed observations",
                            }
                        )
                    else:
                        lo, hi = event_bounds(t0, t1, s0, s1, percent)
                    events.append(
                        {
                            "common_territory_id": sid,
                            "start_year": start,
                            "end_year": end,
                            "source_scenario": scenario,
                            "decline_threshold_percent": percent,
                            "event_lower": lo if lo is not None else "",
                            "event_upper": hi if hi is not None else "",
                            "classification": "not_applicable_zero_baseline"
                            if zero
                            else "definite_event"
                            if lo == hi == 1
                            else "definite_non_event"
                            if lo == hi == 0
                            else "source_unidentified",
                            "staffed_start_hours": text(s0[0]),
                            "staffed_end_observed_hours": b["row"][
                                "staff_service_hours"
                            ],
                            "total_start_hours": text(t0[0]),
                            "total_end_observed_hours": b["row"]["total_hours"],
                            "baseline_population_2022": text(nbase),
                            "population_context": context[sid]["population_context"],
                            "interpretation": "full-frame logical source-identification bounds; not confidence intervals",
                        }
                    )
    write(out / "outputs/annual_and_endpoint_changes.csv", changes)
    write(out / "outputs/denominator_decomposition.csv", decomp)
    write(out / "outputs/event_cases.csv", events)
    write(out / "outputs/trajectory_patterns.csv", patterns)
    write(out / "outputs/denominator_reversal_cases.csv", reversals)
    dump(out / "outputs/unknown_event_witnesses.json", witnesses)
    grouped = defaultdict(list)
    for r in reversals:
        grouped[
            (r["start_year"], r["source_scenario"], r["field"], r["definition"])
        ].append(r)
    write(
        out / "outputs/denominator_reversal_counts.csv",
        [
            {
                "start_year": y,
                "end_year": 2025,
                "source_scenario": sc,
                "field": f,
                "definition": de,
                "frame_territories": 268,
                "count_lower": sum(r["lower"] for r in rs),
                "count_upper": sum(r["upper"] for r in rs),
            }
            for (y, sc, f, de), rs in sorted(grouped.items())
        ],
    )
    return events, patterns


def aggregates(out, context, annual, events, patterns):
    sums, diffs = summarize(events, context)
    write(out / "outputs/event_prevalence.csv", sums)
    write(out / "outputs/context_differences.csv", diffs)
    loo, ld = [], []
    for region in sorted(
        {r for c in context.values() for r in c["frame"]["regions_2022"].split("|")}
    ):
        a, b = summarize(events, context, region)
        loo += a
        ld += b
    write(out / "outputs/region_leave_one_out.csv", loo)
    write(out / "outputs/region_leave_one_out_differences.csv", ld)
    totals = []
    for scenario in SCENARIOS:
        for year in (2022, 2023, 2024, 2025):
            for group in ("declining", "nondeclining", "all"):
                ids = [
                    sid
                    for sid, c in context.items()
                    if group == "all" or c["population_context"] == group
                ]
                pop = sum((context[sid]["population_2022"] for sid in ids), Q(0))
                for field in (*FIELDS, "paid_fte"):
                    lo, hi = add(
                        annual[(sid, year, scenario)]["domains"][field] for sid in ids
                    )
                    missing = [
                        sid
                        for sid in ids
                        if annual[(sid, year, scenario)]["row"][field] == ""
                    ]
                    known = sum(
                        (
                            q(annual[(sid, year, scenario)]["row"][field])
                            for sid in ids
                            if sid not in missing
                        ),
                        Q(0),
                    )
                    totals.append(
                        {
                            "year": year,
                            "source_scenario": scenario,
                            "population_context": group,
                            "field": field,
                            "frame_territories": len(ids),
                            "baseline_population_2022": text(pop),
                            "wholly_observed_sum": text(known) if not missing else "",
                            "partial_observed_sum": text(known),
                            "source_missing_territories": len(missing),
                            "lower_sum": text(lo),
                            "upper_sum": text(hi),
                            "lower_sum_per_1000_baseline": text(lo * 1000 / pop),
                            "upper_sum_per_1000_baseline": text(hi * 1000 / pop)
                            if hi is not None
                            else "unbounded",
                            "meaning": "bounds on aggregate provision; missing source values not observed zeros",
                        }
                    )
    write(out / "outputs/annual_national_domains.csv", totals)
    pmap = {
        (r["common_territory_id"], r["start_year"], r["source_scenario"]): r
        for r in patterns
    }
    counter = Counter()
    for e in events:
        if e["start_year"] == 2022 and e["decline_threshold_percent"] == 0:
            pat = pmap[(e["common_territory_id"], 2022, e["source_scenario"])]
            counter[
                (
                    e["source_scenario"],
                    e["population_context"],
                    e["classification"],
                    pat["paid_fte_direction"],
                )
            ] += 1
    write(
        out / "outputs/fte_event_diagnostic.csv",
        [
            {
                "source_scenario": sc,
                "population_context": g,
                "event_status": ev,
                "paid_fte_direction": d,
                "territories": n,
                "meaning": "descriptive staffing association; no substitution mechanism",
            }
            for (sc, g, ev, d), n in sorted(counter.items())
        ],
    )


def reporting(records, out, frame):
    native = {r["record_id"]: r for r in records}
    members = {
        r["record_id"]: set(r["documentary_member_codes"].split("|")) for r in records
    }
    rows = []
    for sid, f in sorted(frame.items()):
        for start, end in ((2017, 2022), *CHANGES):
            a, b = [f[f"source_records_{y}"].split("|") for y in (start, end)]
            sa, sb = [
                sorted(tuple(sorted(members[rid])) for rid in ids) for ids in (a, b)
            ]
            na, nb = [
                "|".join(native[rid]["system_name"] for rid in ids) for ids in (a, b)
            ]
            rows.append(
                {
                    "common_territory_id": sid,
                    "start_year": start,
                    "end_year": end,
                    "records_start": "|".join(a),
                    "records_end": "|".join(b),
                    "record_count_start": len(a),
                    "record_count_end": len(b),
                    "member_partition_start": json.dumps(sa),
                    "member_partition_end": json.dumps(sb),
                    "reporting_partition_changed": str(sa != sb).lower(),
                    "labels_changed": str(na != nb).lower(),
                    "names_start": na,
                    "names_end": nb,
                    "common_historical_codes": f["historical_codes"],
                    "meaning": "documentary reporting change, not mechanically a policy change",
                }
            )
    write(out / "outputs/reporting_changes.csv", rows)


def projections(out, context, annual):
    rows = []
    for sid, c in sorted(context.items()):
        a, b = (
            annual[(sid, 2022, "published_accounting")],
            annual[(sid, 2025, "published_accounting")],
        )
        n = c["population_2022"]
        s0 = a["domains"]["staff_service_hours"][0]
        s1 = b["domains"]["staff_service_hours"]
        rows.append(
            {
                "common_territory_id": sid,
                "g": c["g"],
                "baseline_population": text(n),
                "baseline_staffed_intensity": text(s0 * 1000 / n),
                "rural_share": c["frame"]["group_3_population_share_2022"],
                "regions_2022": c["frame"]["regions_2022"],
                "cross_region": c["frame"]["cross_region_2022"],
                "response_observed": text((s1[0] - s0) * 1000 / n)
                if s1[0] == s1[1]
                else "",
                "response_lower": text((s1[0] - s0) * 1000 / n),
                "response_upper": text((s1[1] - s0) * 1000 / n)
                if s1[1] is not None
                else "unbounded",
            }
        )
    write(out / "outputs/continuous_diagnostics.csv", rows)
    models = []
    coeffs = []
    support = []
    for name, rs in [
        ("g_only", rows),
        ("context_and_region", [r for r in rows if r["cross_region"] == "false"]),
    ]:
        columns = ["intercept", "prior_g"]
        reference = ""
        if name == "g_only":
            X = [[1, float(r["g"])] for r in rs]
        else:
            regions = sorted({r["regions_2022"] for r in rs})
            reference = regions[0]
            columns += [
                "baseline_population_per10000",
                "baseline_staffed_intensity",
                "rural_share",
            ] + ["region_" + r for r in regions[1:]]
            X = [
                [
                    1,
                    float(r["g"]),
                    float(r["baseline_population"]) / 10000,
                    float(r["baseline_staffed_intensity"]),
                    float(r["rural_share"]),
                    *[int(r["regions_2022"] == region) for region in regions[1:]],
                ]
                for r in rs
            ]
        X = np.array(X, dtype=float)
        y = np.array([float(r["response_lower"]) for r in rs])
        anchor, _, rank, singular = np.linalg.lstsq(X, y, rcond=None)
        missing = [i for i, r in enumerate(rs) if r["response_observed"] == ""]
        observed = [i for i, r in enumerate(rs) if r["response_observed"] != ""]
        assert [rs[i]["common_territory_id"] for i in missing] == ["CRT_755"]
        unit = np.zeros(len(rs))
        unit[missing[0]] = 1
        loading, _, _, _ = np.linalg.lstsq(X, unit, rcond=None)
        partial, _, partial_rank, _ = np.linalg.lstsq(
            X[observed], y[observed], rcond=None
        )
        for column, a, l, obs in zip(columns, anchor, loading, partial):
            coeffs.append(
                {
                    "model": name,
                    "coefficient": column,
                    "domain_lower": format(float(a), ".15g")
                    if l >= 0
                    else "-unbounded",
                    "domain_upper": format(float(a), ".15g") if l <= 0 else "unbounded",
                    "anchor_at_unknown_response_lower": format(float(a), ".15g"),
                    "loading_per_unit_unobserved_response_increase": format(
                        float(l), ".15g"
                    ),
                    "observed_response_sensitivity_coefficient": format(
                        float(obs), ".15g"
                    ),
                    "interpretation": "full-support coefficient source domain; lower-anchor is not an imputed estimate; observed-response fit is a sensitivity only",
                }
            )
        models.append(
            {
                "model": name,
                "design_support": len(rs),
                "response_observed": len(observed),
                "response_unknown": len(missing),
                "rank": int(rank),
                "columns": columns,
                "full_column_rank": bool(rank == len(columns)),
                "observed_response_rank": int(partial_rank),
                "region_reference": reference,
                "cross_region_exclusions": [
                    r["common_territory_id"] for r in rows if r not in rs
                ],
                "unresolved_response_ids": [
                    rs[i]["common_territory_id"] for i in missing
                ],
                "response": "2022-2025 staffed change per1000 baseline residents",
                "weight": "equal territory",
                "source_domain": "beta=anchor+loading*z, z>=0 with no finite upper bound; shared z across all coefficients",
                "significance_tests": False,
                "causal_interpretation": False,
                "precision": "floating linear algebra for projection coefficients only",
            }
        )
    for region in sorted(
        {r["regions_2022"] for r in rows if r["cross_region"] == "false"}
    ):
        rs = [r for r in rows if r["regions_2022"] == region]
        support.append(
            {
                "single_region_2022": region,
                "territories": len(rs),
                "observed_response": sum(r["response_observed"] != "" for r in rs),
                "g_min": str(min(float(r["g"]) for r in rs)),
                "g_max": str(max(float(r["g"]) for r in rs)),
                "baseline_population_min": min(
                    int(r["baseline_population"]) for r in rs
                ),
                "baseline_population_max": max(
                    int(r["baseline_population"]) for r in rs
                ),
            }
        )
    write(out / "outputs/projection_coefficient_domains.csv", coeffs)
    dump(out / "outputs/projection_models.json", models)
    write(out / "outputs/projection_region_support.csv", support)
