
import numpy as np
import pandas as pd

COLLEGE_HOURS = 6.0
PERSONAL_CARE = 2.0

B0    =  5.8
B_EDU = +0.55
B_ENT = -0.50
B_STU = +0.65
B_SLP = +0.30
B_LEI = -0.10

PLATFORMS = {
    "YouTube":   (0.60, 0.10),
    "Instagram": (0.08, 0.06),
    "TikTok":    (0.10, 0.07),
    "LinkedIn":  (0.88, 0.06),
    "Discord":   (0.45, 0.10),
}
P_NAMES   = list(PLATFORMS.keys())
P_WEIGHTS = [0.33, 0.30, 0.22, 0.08, 0.07]

ASSUMED_BETAS = {
    "β₁ edu_sm":    B_EDU,
    "β₂ ent_sm":    B_ENT,
    "β₃ self_study": B_STU,
    "β₄ sleep−7":   B_SLP,
    "β₅ leisure":   B_LEI,
}


def compute_productivity(edu, ent, study, sleep, lei):
    noise = np.random.normal(0, 0.55)
    score = (B0
             + B_EDU * edu
             + B_ENT * ent
             + B_STU * study
             + B_SLP * (sleep - 7.0)
             + B_LEI * lei
             + noise)
    return float(np.clip(score, 0, 10))


def label(score):
    if score < 5.5:
        return "Low"
    elif score < 7.5:
        return "Medium"
    else:
        return "High"


def generate(n: int = 600, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    records = []
    for _ in range(n):
        base_sleep = float(np.clip(np.random.normal(7.0, 1.0), 5.0, 9.5))
        free = max(24.0 - base_sleep - COLLEGE_HOURS - PERSONAL_CARE, 1.0)

        platform        = np.random.choice(P_NAMES, p=P_WEIGHTS)
        edu_mu, edu_std = PLATFORMS[platform]
        edu_frac        = float(np.clip(np.random.normal(edu_mu, edu_std), 0.03, 0.97))

        total_sm = float(np.clip(np.random.lognormal(np.log(3.8), 0.4), 1.0, 7.0))
        edu_sm   = round(total_sm * edu_frac, 2)
        ent_sm   = round(total_sm * (1 - edu_frac), 2)

        sleep_penalty = max(0, (ent_sm - 2.0) * 0.20)
        sleep = round(float(np.clip(base_sleep - sleep_penalty, 4.5, 9.5)), 2)

        remaining   = max(free - total_sm, 0.3)
        study_bias  = float(np.clip(0.55 - ent_sm * 0.06, 0.10, 0.50))
        self_study  = round(float(np.clip(
            np.random.normal(remaining * study_bias, 0.35),
            0.2, remaining * 0.85)), 2)

        leisure = round(float(np.clip(np.random.exponential(0.8), 0.1, 2.5)), 2)
        p_score = compute_productivity(edu_sm, ent_sm, self_study, sleep, leisure)

        records.append({
            "sleep_hours":        sleep,
            "college_hours":      COLLEGE_HOURS,
            "edu_sm_hours":       edu_sm,
            "ent_sm_hours":       ent_sm,
            "self_study_hours":   self_study,
            "leisure_hours":      leisure,
            "platform":           platform,
            "productivity_score": round(p_score, 2),
            "productivity_label": label(p_score),
        })

    return pd.DataFrame(records)
