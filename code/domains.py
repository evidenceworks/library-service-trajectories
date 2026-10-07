"""Exact published-value domains. None as an upper endpoint means unbounded."""

from fractions import Fraction as Q
from decimal import Decimal, localcontext

FIELDS = (
    "staff_service_hours",
    "staff_present_no_service_hours",
    "no_library_staff_hours",
    "total_hours",
)
MODES = FIELDS[:3]
OBSERVED = {"observed_numeric", "observed_zero"}


def q(value):
    return Q(Decimal(str(value)))


def text(value):
    if value is None:
        return "unbounded"
    value = Q(value)
    with localcontext() as ctx:
        ctx.prec = 60
        d = Decimal(value.numerator) / Decimal(value.denominator)
        return format(d, "f")


def exact(value):
    return str(Q(value))


def row_domain(record, scenario):
    assert scenario in ("published_accounting", "conservative_relaxation")
    observed = {
        f: q(record[f + "_raw"]) if record[f + "_state"] in OBSERVED else None
        for f in FIELDS
    }
    unknown = [f for f in FIELDS if observed[f] is None]
    assert all(record[f + "_state"] == "blank" for f in unknown), (
        "Unadjudicated hour marker"
    )
    if not unknown:
        assert observed["total_hours"] == sum((observed[f] for f in MODES), Q(0))
        return {
            f: (observed[f], observed[f]) for f in FIELDS
        }, "observed exact category identity"
    t = observed["total_hours"]
    if t is None:
        assert len(unknown) == 4, (
            "Unknown total with partial vector requires source adjudication"
        )
        constraints = (
            "T=S+M+U; S,M,U>=0; no finite cap"
            if scenario == "published_accounting"
            else "S,M,U,T independently nonnegative; identity relaxed; no finite cap"
        )
        return {f: (Q(0), None) for f in FIELDS}, constraints
    missing_modes = [f for f in MODES if observed[f] is None]
    residual = t - sum((observed[f] for f in MODES if observed[f] is not None), Q(0))
    assert residual >= 0, "Negative incomplete-record accounting residual"
    result = {}
    for f in FIELDS:
        if observed[f] is not None:
            result[f] = (observed[f], observed[f])
        elif scenario == "published_accounting":
            result[f] = (residual if len(missing_modes) == 1 else Q(0), residual)
        else:
            result[f] = (Q(0), t)
    constraint = (
        "+".join(missing_modes)
        + "="
        + exact(residual)
        + "; nonnegative; observed cells fixed"
        if scenario == "published_accounting"
        else "unknown modes separately in [0,T]; incomplete-row identity relaxed; observed cells fixed"
    )
    return result, constraint


def add(bounds):
    bounds = list(bounds)
    return (
        sum((lo for lo, hi in bounds), Q(0)),
        None
        if any(hi is None for lo, hi in bounds)
        else sum((hi for lo, hi in bounds), Q(0)),
    )


def change(a, b):
    return (
        None if a[1] is None else b[0] - a[1],
        None if b[1] is None else b[1] - a[0],
    )


def min_upper(*values):
    finite = [v for v in values if v is not None]
    return min(finite) if finite else None


def upper_ge(upper, value):
    return upper is None or upper >= value


def upper_gt(upper, value):
    return upper is None or upper > value


def event_bounds(t0, t1, s0, s1, percent=0):
    """Sharp projected bounds for rectangular intervals with within-year S<=T.

    Additional accounting restrictions must be kept at source-record level.
    Endpoint S/T domains must also satisfy their source-record accounting
    restrictions. A completely unknown vector is handled jointly by the analysis.
    """
    for lo, hi in (t0, t1, s0, s1):
        assert lo >= 0 and (hi is None or hi >= lo)
    assert upper_ge(t0[1], s0[0]) and upper_ge(t1[1], s1[0])
    assert percent in (0, 2, 5)
    minimum_t0 = max(t0[0], s0[0])
    minimum_t1 = max(t1[0], s1[0])
    largest_s0_for_event = min_upper(s0[1], t0[1], t1[1])
    largest_s1 = min_upper(s1[1], t1[1])
    total_possible = upper_ge(t1[1], minimum_t0)
    total_certain = t0[1] is not None and minimum_t1 >= t0[1]
    if percent == 0:
        staffed_possible = upper_gt(largest_s0_for_event, s1[0])
        staffed_certain = largest_s1 is not None and largest_s1 < s0[0]
    else:
        a = Q(100 - percent, 100)
        staffed_possible = upper_gt(largest_s0_for_event, Q(0)) and (
            largest_s0_for_event is None or s1[0] <= a * largest_s0_for_event
        )
        staffed_certain = (
            s0[0] > 0 and largest_s1 is not None and largest_s1 <= a * s0[0]
        )
    return int(total_certain and staffed_certain), int(
        total_possible and staffed_possible
    )


def decomposition(h0, h1, n0, n1):
    h0, h1, n0, n1 = map(Q, (h0, h1, n0, n1))
    assert min(h0, h1) >= 0 and min(n0, n1) > 0
    total = h1 / n1 - h0 / n0
    hours = (h1 - h0) * (1 / n0 + 1 / n1) / 2
    population = (1 / n1 - 1 / n0) * (h0 + h1) / 2
    assert total == hours + population
    return total, hours, population


def decomposition_domain(h0, h1, n0, n1):
    """Linear extrema and a shared formula, never independent component draws."""
    n0, n1 = Q(n0), Q(n1)
    assert n0 > 0 and n1 > 0
    if h0[1] is None or h1[1] is None:
        return None
    corners = [decomposition(a, b, n0, n1) for a in h0 for b in h1]
    return [(min(x[j] for x in corners), max(x[j] for x in corners)) for j in range(3)]
