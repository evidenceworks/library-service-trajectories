"""Event prevalence under population and equal-territory weighting."""

from collections import defaultdict
from fractions import Fraction as Q
from domains import text, exact


def summarize(events, context, omitted_region=""):
    grouped = defaultdict(list)
    for e in events:
        if omitted_region and omitted_region in context[e["common_territory_id"]][
            "frame"
        ]["regions_2022"].split("|"):
            continue
        key = (
            e["source_scenario"],
            e["start_year"],
            e["end_year"],
            e["decline_threshold_percent"],
        )
        grouped[key].append(e)
    summaries, differences = [], []
    for key, rows in sorted(grouped.items()):
        scenario, start, end, percent = key
        for weight in ("population_2022", "equal_territory"):
            bounds = {}
            for group in ("declining", "nondeclining"):
                rs = [e for e in rows if e["population_context"] == group]
                applicable = [e for e in rs if e["event_lower"] != ""]
                # Keep original group footprints visible even in a percent
                # sensitivity with an undefined zero baseline.
                n = len(rs)
                pop = sum(
                    (context[e["common_territory_id"]]["population_2022"] for e in rs),
                    Q(0),
                )
                denom = sum(
                    (
                        context[e["common_territory_id"]]["population_2022"]
                        if weight == "population_2022"
                        else Q(1)
                        for e in applicable
                    ),
                    Q(0),
                )
                nums = [
                    sum(
                        (
                            Q(e[k])
                            * (
                                context[e["common_territory_id"]]["population_2022"]
                                if weight == "population_2022"
                                else Q(1)
                            )
                            for e in applicable
                        ),
                        Q(0),
                    )
                    for k in ("event_lower", "event_upper")
                ]
                pair = (nums[0] / denom, nums[1] / denom) if denom else None
                bounds[group] = pair
                summaries.append(
                    {
                        "source_scenario": scenario,
                        "start_year": start,
                        "end_year": end,
                        "decline_threshold_percent": percent,
                        "weight": weight,
                        "population_context": group,
                        "omitted_region": omitted_region,
                        "original_frame_territories": n,
                        "original_baseline_population": text(pop),
                        "applicable_territories": len(applicable),
                        "zero_baseline_separate_territories": n - len(applicable),
                        "denominator_weight": text(denom),
                        "numerator_weight_lower": text(nums[0]),
                        "numerator_weight_upper": text(nums[1]),
                        "event_count_lower": sum(
                            int(e["event_lower"]) for e in applicable
                        ),
                        "event_count_upper": sum(
                            int(e["event_upper"]) for e in applicable
                        ),
                        "proportion_lower": text(pair[0]) if pair else "",
                        "proportion_upper": text(pair[1]) if pair else "",
                        "proportion_lower_exact": exact(pair[0]) if pair else "",
                        "proportion_upper_exact": exact(pair[1]) if pair else "",
                        "status": "identified_source_domain"
                        if pair and pair[0] == pair[1]
                        else "source_uncertainty"
                        if pair
                        else "empty_group",
                        "interpretation": "national frame descriptive quantity; source-identification envelope, not sampling confidence interval",
                    }
                )
            x, y = bounds["declining"], bounds["nondeclining"]
            lower, upper = (x[0] - y[1], x[1] - y[0]) if x and y else (None, None)
            differences.append(
                {
                    "source_scenario": scenario,
                    "start_year": start,
                    "end_year": end,
                    "decline_threshold_percent": percent,
                    "weight": weight,
                    "omitted_region": omitted_region,
                    "difference_lower": text(lower) if lower is not None else "",
                    "difference_upper": text(upper) if upper is not None else "",
                    "difference_lower_exact": exact(lower) if lower is not None else "",
                    "difference_upper_exact": exact(upper) if upper is not None else "",
                    "direction": "declining minus nondeclining",
                    "interpretation": "national frame descriptive quantity; source-identification envelope, not causal or sampling inference",
                }
            )
    return summaries, differences
