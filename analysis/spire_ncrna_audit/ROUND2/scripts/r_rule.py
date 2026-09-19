"""The Round-2 candidate rule (DESIGN §6–7). Shared by DEV calibration and HELDOUT evaluation.
Uses only discovery outputs (motif features); never references."""
import pandas as pd


def candidate(runm, ranking, k):
    ok = runm[runm.status == 'OK'] if 'status' in runm else runm.iloc[:0]
    if ok.empty:
        return None
    if ranking == 'R_A':
        return ok.sort_values(['score_sum', 'n_inst'], ascending=False).iloc[0]
    ok = ok[ok.coding_frac <= k]
    if ok.empty:
        return None
    return ok.assign(_r=ok.coverage * ok.score_mean).sort_values(['_r', 'n_inst'], ascending=False).iloc[0]


def passes(m, c, s, k, b):
    return bool(m is not None and m.coverage >= c and (m.centre_sd <= s if pd.notna(m.centre_sd) else False)
                and m.coding_frac <= k and m.score_mean >= b and m.cov_state != 'POWERED_ABSENT')


def concordant(full, sub_runm, rule, tol=50):
    """Sub-run (half / leave-cluster-out) reproduces the full candidate: its candidate under the same rule
    (minus stability) passes and its centre lies within tol nt of the full candidate's centre."""
    if full is None:
        return False
    m = candidate(sub_runm, rule['ranking'], rule['k'])
    return bool(passes(m, rule['c'], rule['s'], rule['k'], rule['b'])
                and abs(m.centre_median - full.centre_median) <= tol)
