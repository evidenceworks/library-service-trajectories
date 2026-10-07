"""Check stable inputs and the reported scientific quantities."""

from pathlib import Path
from collections import Counter
from decimal import Decimal
import argparse, json, math
from support import read, sha
from domains import FIELDS, q, row_domain

ROOT = Path(__file__).resolve().parents[1]


def check_inputs(root=ROOT):
    root = Path(root)
    lines = (root / "checksums.sha256").read_text(encoding="utf-8").splitlines()
    names = set()
    for line in lines:
        digest, name = line.split("  ", 1)
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or name in names:
            raise ValueError(f"Invalid checksum path: {name}")
        names.add(name)
        if not path.is_file() or sha(path) != digest:
            raise ValueError(f"Scientific input missing or changed: {name}")
    expected = {
        p.relative_to(root).as_posix()
        for p in (root / "data").iterdir()
        if p.suffix != ".md"
    }
    assert names == expected, "Scientific input checksum coverage differs"
    panel = read(root / "data/territory-panel.csv.gz")
    records = read(root / "data/source-records.csv.gz")
    territories = read(root / "data/territories.csv")
    assert len(territories) == 268 and len(panel) == 1340 and len(records) == 1384
    assert len({(r["common_territory_id"], r["year"]) for r in panel}) == 1340
    assert Counter(r["year"] for r in panel) == {
        str(y): 268 for y in [2017, 2022, 2023, 2024, 2025]
    }
    assert Counter(r["year"] for r in records) == {
        "2017": 277,
        "2022": 275,
        "2023": 276,
        "2024": 278,
        "2025": 278,
    }
    byid = {r["record_id"]: r for r in records}
    assert len(byid) == len(records)
    for year, count in [
        (2017, 295),
        (2022, 293),
        (2023, 293),
        (2024, 293),
        (2025, 292),
    ]:
        codes = [
            code
            for r in records
            if r["year"] == str(year)
            for code in r["documentary_member_codes"].split("|")
        ]
        assert len(codes) == len(set(codes)) == count, (
            f"Municipal coverage or overlap in {year}"
        )
    blanks = [
        (r["record_id"], field)
        for r in records
        if r["year"] != "2017"
        for field in FIELDS
        if r[field + "_state"] == "blank"
    ]
    assert len(blanks) == 16
    missing = read(root / "data/missing-hour-domains.csv")
    assert {(r["record_id"], r["field"]) for r in missing} == set(blanks)
    for r in missing:
        assert r["raw"] == "" and r["state"] == "blank"
        for scenario, prefixes in [
            ("published_accounting", ("lower", "upper")),
            ("conservative_relaxation", ("relaxed_lower", "relaxed_upper")),
        ]:
            pair = row_domain(byid[r["record_id"]], scenario)[0][r["field"]]
            assert all(
                (value is None and r[key] == "unbounded")
                or (value is not None and value == q(r[key]))
                for value, key in zip(pair, prefixes)
            )
    corrections = read(root / "data/source-corrections.csv")
    assert len(corrections) == 8 and all(
        r["raw_changed"] == "false" for r in corrections
    )
    alavus = next(
        r
        for r in panel
        if r["common_territory_id"] == "CRT_010" and r["year"] == "2017"
    )
    assert (
        alavus["population_raw_source_sum"] == "11097"
        and alavus["population_accepted"] == "11907"
    )
    for r in corrections[1:7]:
        source = byid[r["record_id"]]
        assert source["native_municipality_code_raw"] == r["raw_value"]
        assert source["documentary_member_codes"] == r["accepted_value"]
    assert byid["2023:ALL:29"]["paid_fte_raw"] == "451"
    print(
        f"Checked {len(names)} stable scientific inputs, 268 territories and 16 raw hour blanks."
    )
    return {"stable_inputs": len(names), "territories": 268, "raw_hour_blanks": 16}


def compare_projection(actual, reference):
    assert len(actual) == len(reference)
    numeric = {
        "domain_lower",
        "domain_upper",
        "anchor_at_unknown_response_lower",
        "loading_per_unit_unobserved_response_increase",
        "observed_response_sensitivity_coefficient",
    }
    maximum = 0.0
    for a, b in zip(actual, reference):
        assert a.keys() == b.keys()
        for key in a:
            if (
                key in numeric
                and "unbounded" not in a[key]
                and "unbounded" not in b[key]
            ):
                error = abs(float(a[key]) - float(b[key]))
                maximum = max(maximum, error)
                assert math.isclose(
                    float(a[key]), float(b[key]), rel_tol=1e-10, abs_tol=1e-10
                ), (a["model"], a["coefficient"], key)
            else:
                assert a[key] == b[key], (a["model"], a["coefficient"], key)
    return maximum


def compare_calculations(root, out):
    expected = json.loads(
        (root / "data/expected-results.json").read_text(encoding="utf-8")
    )
    receipt = {}
    for name, reference in expected.items():
        path = out / "outputs" / name
        digest = sha(path)
        equal = digest == reference["sha256"]
        detail = {"sha256": digest, "exact_bytes": equal}
        if not equal and name == "projection_coefficient_domains.csv":
            detail["maximum_absolute_difference"] = compare_projection(
                read(path), read(root / "data/projection-reference.csv")
            )
            detail["numeric_parity"] = True
        else:
            assert equal, f"Recomputed result differs from reference: {name}"
        receipt[name] = detail
    print(
        f"Verified {len(receipt)} recomputed result objects against their scientific references."
    )
    return receipt


def rounded_percent(value):
    return format((Decimal(value) * 100).quantize(Decimal(".01")), "f")


def check_results(root=ROOT):
    root = Path(root)
    expected = json.loads(
        (root / "data/public-results-reference.json").read_text(encoding="utf-8")
    )
    for name, digest in expected.items():
        if not (root / name).is_file() or sha(root / name) != digest:
            raise ValueError(
                f"Result missing or changed: {name}; run code/reproduce.py"
            )
    compare_projection(
        read(root / "results/projection-domains.csv"),
        read(root / "data/projection-reference.csv"),
    )
    differences = read(root / "results/event-differences.csv")
    for start, weight, limits in [
        ("2022", "population_2022", ("9.97", "10.16")),
        ("2022", "equal_territory", ("1.58", "3.58")),
        ("2023", "population_2022", ("-2.98", "-2.80")),
        ("2023", "equal_territory", ("-0.35", "1.65")),
    ]:
        row = next(
            r
            for r in differences
            if r["start_year"] == start
            and r["weight"] == weight
            and r["source_scenario"] == "published_accounting"
            and r["decline_threshold_percent"] == "0"
        )
        pair = tuple(
            rounded_percent(row[k]) for k in ["difference_lower", "difference_upper"]
        )
        assert pair == limits
        print(f"{start}-2025, {weight}: [{pair[0]}, {pair[1]}] percentage points.")
    events = [
        r
        for r in read(root / "results/event-prevalence.csv")
        if r["start_year"] == "2022"
        and r["decline_threshold_percent"] == "0"
        and r["weight"] == "equal_territory"
        and r["source_scenario"] == "published_accounting"
    ]
    assert [
        (
            r["original_frame_territories"],
            r["event_count_lower"],
            r["event_count_upper"],
        )
        for r in events
    ] == [("218", "95", "95"), ("50", "20", "21")]
    print(
        "115 definite focal-event territories; one additional source-unidentified territory."
    )
    totals = read(root / "results/annual-totals.csv")
    for scenario in ["published_accounting", "conservative_relaxation"]:
        rows = [
            r
            for r in totals
            if r["source_scenario"] == scenario
            and r["year"] == "2025"
            and r["population_context"] == "all"
            and r["field"] in FIELDS
        ]
        assert len(rows) == 4 and all(r["upper_sum"] == "unbounded" for r in rows)
    t = {
        r["year"]: r
        for r in totals
        if r["source_scenario"] == "published_accounting"
        and r["population_context"] == "all"
        and r["field"] == "total_hours"
    }
    assert q(t["2025"]["lower_sum"]) - q(t["2022"]["lower_sum"]) == q("207403.29")
    print("All four national 2025 hour totals retain unbounded upper limits.")
    return {
        "definite_events": 115,
        "central_comparisons": 4,
        "national_upper_limits": "unbounded",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--inputs-only", action="store_true")
    args = parser.parse_args()
    check_inputs(args.root)
    if not args.inputs_only:
        check_results(args.root)
