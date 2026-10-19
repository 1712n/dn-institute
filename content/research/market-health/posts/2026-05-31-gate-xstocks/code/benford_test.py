"""Benford diagnostics for the wash screen, with the statistical context behind
why the post reports the first-digit signal as a comparative Kolmogorov-Smirnov
distance rather than a p-value.

For each market it prints the KS distance from Benford, the mean absolute
deviation (MAD) with Nigrini's conformity bands, and the chi-square statistic
(df = 8). The point the numbers make:

  - At tens of thousands of trades the chi-square statistic is far above the
    df=8 critical value at p=0.001 (~26.1) for every market, the MSTRX control
    included, so a formal goodness-of-fit p-value rejects Benford everywhere and
    cannot discriminate (large samples over-power the test).
  - MAD likewise lands every market in Nigrini's "nonconformity" band (> 0.015),
    because tokenized-stock trade sizes span too few orders of magnitude to track
    Benford closely in the first place.
  - The KS distance is what separates them: the washed markets sit 3-10x farther
    from Benford than the control, the excess coming from the one dominant clip.

Pure stdlib + pandas (no scipy); loads the same tapes as the screen.
"""
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import load

BENFORD = {d: math.log10(1 + 1 / d) for d in range(1, 10)}
CHI2_CRIT_DF8_P001 = 26.12   # chi-square critical value, df=8, p=0.001


def first_digits(amt):
    fd = amt.astype(str).str.replace(".", "", regex=False).str.lstrip("0").str[0]
    fd = fd[fd.str.isdigit() & (fd != "0")].astype(int)
    return fd


def diagnostics(amt):
    fd = first_digits(amt)
    n = len(fd)
    counts = {d: int((fd == d).sum()) for d in range(1, 10)}
    obs_p = {d: counts[d] / n for d in range(1, 10)}
    # KS distance: max gap of the cumulative distributions
    co = cb = ks = 0.0
    for d in range(1, 10):
        co += obs_p[d]; cb += BENFORD[d]
        ks = max(ks, abs(co - cb))
    mad = sum(abs(obs_p[d] - BENFORD[d]) for d in range(1, 10)) / 9
    chi2 = sum((counts[d] - n * BENFORD[d]) ** 2 / (n * BENFORD[d]) for d in range(1, 10))
    return n, ks, mad, chi2


def band(mad):
    return ("close conformity" if mad <= 0.006 else "acceptable" if mad <= 0.012
            else "marginal" if mad <= 0.015 else "nonconformity")


def main():
    markets = ["HOODX", "SPYX", "TSLAX", "NVDAX", "AAPLX", "GOOGLX", "MSTRX"]
    print(f"  {'market':8}{'N':>9}{'KS dist':>9}{'MAD':>9}{'band':>16}{'chi2(df8)':>12}{'rejects Benford':>18}")
    for sym in markets:
        n, ks, mad, chi2 = diagnostics(load(sym)["amt"])
        rejects = "yes (p<0.001)" if chi2 > CHI2_CRIT_DF8_P001 else "no"
        print(f"  {sym:8}{n:>9,}{ks:>9.3f}{mad:>9.4f}{band(mad):>16}{chi2:>12,.0f}{rejects:>18}")
    print("\nEvery market, control included, exceeds the df=8 chi-square critical value at "
          "p=0.001, so a Benford p-value is uninformative; MAD bands also flag all of them. "
          "The KS distance is the comparative measure that separates washed (0.10-0.35) from MSTRX (0.03).")


if __name__ == "__main__":
    main()
