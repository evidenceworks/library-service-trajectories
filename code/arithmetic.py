"""Extend accepted rational hour domains to unbounded national quantities."""

from fractions import Fraction as Q
from domains import text, exact


def lower_text(v):
    return "-unbounded" if v is None else text(v)


def lower_exact(v):
    return "-unbounded" if v is None else exact(v)


def upper_exact(v):
    return "unbounded" if v is None else exact(v)


def linear_domain(coefficients, domains):
    lo = hi = Q(0)
    low_inf = high_inf = False
    for c, (a, b) in zip(coefficients, domains):
        if c == 0:
            continue
        if c > 0:
            lo += c * a
            if b is None:
                high_inf = True
            else:
                hi += c * b
        else:
            hi += c * a
            if b is None:
                low_inf = True
            else:
                lo += c * b
    return (None if low_inf else lo, None if high_inf else hi)


def decomposition_bounds(h0, h1, n0, n1):
    k = (1 / n0 + 1 / n1) / 2
    b = (1 / n1 - 1 / n0) / 2
    return [linear_domain(cs, [h0, h1]) for cs in [(-1 / n0, 1 / n1), (-k, k), (b, b)]]


def compare(a, b, condition):
    """Sharp indicator bounds for linear quantities in independent endpoint domains."""
    lo0, hi0 = a
    lo1, hi1 = b
    if condition == "absolute_decrease":
        return int(hi1 is not None and hi1 < lo0), int(hi0 is None or lo1 < hi0)
    if condition == "absolute_increase":
        return int(hi0 is not None and lo1 > hi0), int(hi1 is None or hi1 > lo0)
    raise ValueError(condition)


def denominator_reversal_bounds(h0, h1, n0, n1, direction):
    # Scale invariance: characterize the shared endpoint state by r=H1/H0.
    # Known positive H0 in this accepted national frame avoids a guessed epsilon.
    assert h0[0] == h0[1] and h0[0] > 0
    a = h1[0] / h0[0]
    b = None if h1[1] is None else h1[1] / h0[0]
    ratio = n1 / n0
    low, high = (
        (ratio, Q(1))
        if direction == "absolute_decrease_per_resident_increase"
        else (Q(1), ratio)
    )
    if high <= low:
        return (0, 0)
    possible = a < high and (b is None or b > low)
    certain = a > low and b is not None and b < high
    return int(certain), int(possible)
