import numpy as np
import pandas as pd


def t_score(hours):
    if hours is None or hours != hours or hours < 0:
        return 0
    if hours < 5 / 60:
        return 5
    if hours < 15 / 60:
        return 4
    if hours < 1:
        return 3
    if hours < 6:
        return 2
    if hours < 24:
        return 1
    return 0


def v_score(ratio):
    if ratio != ratio:
        return 0
    if ratio < 2:
        return 0
    if ratio < 3:
        return 1
    if ratio < 5:
        return 2
    if ratio < 10:
        return 3
    return 4


def p_score(vwap_entry):
    # information edge = got in cheap (long odds) on the eventual winner
    if vwap_entry != vwap_entry:
        return 0
    if vwap_entry <= 0.15:
        return 4
    if vwap_entry <= 0.25:
        return 3
    if vwap_entry <= 0.40:
        return 2
    if vwap_entry <= 0.55:
        return 1
    return 0


def a_score(ratio):
    if ratio != ratio:
        return 0
    s = 0
    if ratio >= 2:
        s = 1
    if ratio >= 3:
        s = 2
    if ratio >= 5:
        s = 3
    if ratio > 3:
        s += 1
    return min(s, 4)


def r_score(wins, attempts):
    if attempts < 2:
        return 0
    ratio = wins / attempts
    if wins >= 7 and ratio >= 0.70:
        return 5
    if wins >= 5 and ratio >= 0.80:
        return 4
    if wins >= 4 and ratio >= 0.80:
        return 3
    if wins >= 3 and ratio >= 0.75:
        return 2
    if wins >= 2 and ratio >= 0.66:
        return 1
    return 0


def score_row(r):
    T = t_score(r["t_hours"])
    V = v_score(r["v_ratio"])
    P = p_score(r["vwap_entry"])
    A = a_score(r["a_ratio"])
    R = r_score(r["wins"], r["attempts"])
    S = 2 * T + 2 * V + P + 2 * A + R
    return pd.Series({"T": T, "V": V, "P": P, "A": A, "R": R, "S": S})
