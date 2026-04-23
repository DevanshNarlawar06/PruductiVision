"""
train.py — v5.0
Trains all three classifiers + linear regression on the generated dataset.
Returns models, metrics, and generates all plots to the given plots_dir.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    ConfusionMatrixDisplay, accuracy_score
)

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

LABEL_ORDER = ["Low", "Medium", "High"]
PAL = {"Low": "#e74c3c", "Medium": "#f39c12", "High": "#2ecc71"}
NUM_FEATS = ["edu_sm_hours", "ent_sm_hours", "self_study_hours",
             "sleep_hours", "leisure_hours", "productivity_score"]
FEATURES = ["edu_sm_hours", "ent_sm_hours", "self_study_hours",
            "sleep_hours", "leisure_hours", "platform_enc"]

ASSUMED_BETAS = {
    "β₁ edu_sm":     +0.55,
    "β₂ ent_sm":     -0.50,
    "β₃ self_study": +0.65,
    "β₄ sleep−7":   +0.30,
    "β₅ leisure":    -0.10,
}


# ── Dummy Label Encoder to prevent sci-kit sorting ────────────────────────
class DummyLabelEncoder:
    def __init__(self, classes):
        self.classes_ = np.array(classes)
    def transform(self, y):
        mapping = {val: idx for idx, val in enumerate(self.classes_)}
        return np.array([mapping[val] for val in y])


def train_pipeline(df: pd.DataFrame, plots_dir: str) -> dict:
    os.makedirs(plots_dir, exist_ok=True)

    df = df.copy()
    df["productivity_label"] = pd.Categorical(
        df["productivity_label"], categories=LABEL_ORDER, ordered=True
    )

    # ── Plot 0: 24-hr Pie + SM Split ──────────────────────────────────────
    untracked = max(0, 24 - df["sleep_hours"].mean() - 6.0 - 2.0
                    - df["edu_sm_hours"].mean() - df["ent_sm_hours"].mean()
                    - df["self_study_hours"].mean() - df["leisure_hours"].mean())
    time_means = {
        f"Sleep\n({df['sleep_hours'].mean():.1f}h)":            df["sleep_hours"].mean(),
        "College\n(6.0h)":                                       6.0,
        "Personal\nCare\n(2.0h)":                                2.0,
        f"Edu SM\n({df['edu_sm_hours'].mean():.1f}h)":          df["edu_sm_hours"].mean(),
        f"Ent SM\n({df['ent_sm_hours'].mean():.1f}h)":          df["ent_sm_hours"].mean(),
        f"Self-Study\n({df['self_study_hours'].mean():.1f}h)":  df["self_study_hours"].mean(),
        f"Leisure\n({df['leisure_hours'].mean():.1f}h)":        df["leisure_hours"].mean(),
        f"Untracked\n({untracked:.1f}h)":                       untracked,
    }
    colors = ["#3498db","#9b59b6","#1abc9c","#27ae60","#e74c3c","#f39c12","#bdc3c7","#ecf0f1"]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    wedges, texts, autotexts = axes[0].pie(
        time_means.values(), labels=time_means.keys(), colors=colors,
        autopct="%1.1f%%", startangle=130, pctdistance=0.78,
        wedgeprops=dict(edgecolor="white", linewidth=1.5))
    for t in autotexts:
        t.set_fontsize(8)
    axes[0].set_title("Research-Grounded 24-Hour Budget\n(college student, India)",
                      fontsize=12, fontweight="bold")
    bars = axes[1].bar(
        ["Educational SM\n(YouTube, LinkedIn,\nDiscord)",
         "Entertainment SM\n(Instagram, Snapchat)"],
        [df["edu_sm_hours"].mean(), df["ent_sm_hours"].mean()],
        color=["#27ae60", "#e74c3c"], edgecolor="black", width=0.4)
    axes[1].set_ylabel("Average Hours / Day")
    axes[1].set_ylim(0, 4.0)
    axes[1].set_title("Social Media — Educational vs Entertainment Split",
                      fontsize=12, fontweight="bold")
    total_sm_avg = df["edu_sm_hours"].mean() + df["ent_sm_hours"].mean()
    for bar in bars:
        h = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width() / 2, h + 0.05,
                     f"{h:.2f}h\n({h/total_sm_avg*100:.0f}% of SM)",
                     ha="center", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "0_budget_sm_split.png"), dpi=150)
    plt.close()

    # ── Plot 1: Pearson Heatmap ────────────────────────────────────────────
    corr_df = df[NUM_FEATS].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_df, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.6, vmin=-1, vmax=1, annot_kws={"size": 10})
    plt.title("Pearson Correlation Heatmap", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "1_pearson_heatmap.png"), dpi=150)
    plt.close()

    # ── Plot 2: EDA ───────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    scatter_pairs = [("edu_sm_hours", "Educational SM Hours"),
                     ("ent_sm_hours", "Entertainment SM Hours"),
                     ("self_study_hours", "Self-Study Hours")]
    for ax, (feat, lbl) in zip(axes[0], scatter_pairs):
        for lab in LABEL_ORDER:
            sub = df[df["productivity_label"] == lab]
            ax.scatter(sub[feat], sub["productivity_score"],
                       c=PAL[lab], label=lab, alpha=0.45, s=22)
        ax.set_xlabel(lbl)
        ax.set_ylabel("Productivity Score")
        ax.set_title(f"{lbl} vs Productivity")
        ax.legend(fontsize=8)
    box_pairs = [("sleep_hours", "Sleep Hours"), ("leisure_hours", "Leisure Hours")]
    for ax, (feat, lbl) in zip(axes[1, :2], box_pairs):
        sns.boxplot(data=df, x="productivity_label", y=feat,
                    palette=PAL, order=LABEL_ORDER, ax=ax)
        ax.set_title(f"{lbl} by Productivity Class")
        ax.set_xlabel("")
        ax.set_ylabel(lbl)
    plat_prod = df.groupby("platform")["productivity_score"].mean().sort_values()
    bar_c = ["#e74c3c" if v < df["productivity_score"].mean() else "#2ecc71"
             for v in plat_prod.values]
    axes[1, 2].barh(plat_prod.index, plat_prod.values, color=bar_c, edgecolor="black")
    axes[1, 2].axvline(df["productivity_score"].mean(), ls="--", color="gray",
                       alpha=0.7, label="overall avg")
    axes[1, 2].set_xlabel("Avg Productivity Score")
    axes[1, 2].set_title("Platform vs Avg Productivity")
    axes[1, 2].legend()
    plt.suptitle("EDA — Feature Relationships with Productivity (v5.0)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "2_eda.png"), dpi=150)
    plt.close()

    # ── Plot 2b: Inter-feature correlations ───────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].scatter(df["ent_sm_hours"], df["self_study_hours"],
                    alpha=0.4, s=20, color="#9b59b6")
    m, b = np.polyfit(df["ent_sm_hours"], df["self_study_hours"], 1)
    x_ = np.linspace(df["ent_sm_hours"].min(), df["ent_sm_hours"].max(), 100)
    axes[0].plot(x_, m * x_ + b, color="#e74c3c", lw=2)
    r1, _ = pearsonr(df["ent_sm_hours"], df["self_study_hours"])
    axes[0].set_xlabel("Entertainment SM Hours")
    axes[0].set_ylabel("Self-Study Hours")
    axes[0].set_title(f"Ent SM vs Self-Study\n(r = {r1:+.3f} — time competition effect)")
    axes[1].scatter(df["ent_sm_hours"], df["sleep_hours"],
                    alpha=0.4, s=20, color="#e67e22")
    m2, b2 = np.polyfit(df["ent_sm_hours"], df["sleep_hours"], 1)
    axes[1].plot(x_, m2 * x_ + b2, color="#e74c3c", lw=2)
    r2, _ = pearsonr(df["ent_sm_hours"], df["sleep_hours"])
    axes[1].set_xlabel("Entertainment SM Hours")
    axes[1].set_ylabel("Sleep Hours")
    axes[1].set_title(f"Ent SM vs Sleep\n(r = {r2:+.3f} — late-night scrolling effect)")
    plt.suptitle("Realistic Inter-Feature Correlations (Changes 1 & 2)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "2b_inter_feature_correlations.png"), dpi=150)
    plt.close()

    # ── Linear Regression — Beta Learning ─────────────────────────────────
    df["sleep_dev"] = df["sleep_hours"] - 7.0
    lin_feats = ["edu_sm_hours", "ent_sm_hours", "self_study_hours",
                 "sleep_dev", "leisure_hours"]
    lin = LinearRegression().fit(df[lin_feats], df["productivity_score"])
    r2_score = lin.score(df[lin_feats], df["productivity_score"])
    learned_betas = dict(zip(ASSUMED_BETAS.keys(), lin.coef_))

    # ── Plot 3: Beta comparison ────────────────────────────────────────────
    names = [k.split(" ", 1)[1] for k in ASSUMED_BETAS]
    x = np.arange(len(names))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    b1 = ax.bar(x - w / 2, list(ASSUMED_BETAS.values()), w,
                label="Phase 1 — Assumed (literature)", color="#3498db", alpha=0.85, edgecolor="k")
    b2 = ax.bar(x + w / 2, list(learned_betas.values()), w,
                label="Phase 2 — Learned by ML", color="#e67e22", alpha=0.85, edgecolor="k")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=10)
    ax.set_ylabel("Beta Coefficient Value")
    ax.set_title("Assumed vs Dynamically Learned Beta Values\n"
                 "Direction agreement validates the dataset approach", fontsize=11)
    ax.legend()
    for bar in list(b1) + list(b2):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (0.01 if bar.get_height() >= 0 else -0.05),
                f"{bar.get_height():+.2f}", ha="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "3_beta_comparison.png"), dpi=150)
    plt.close()

    # ── Encode + Split ────────────────────────────────────────────────────
    le_p = LabelEncoder()
    df["platform_enc"] = le_p.fit_transform(df["platform"])
    y_raw = df["productivity_label"].astype(str)
    # Use the global DummyLabelEncoder to maintain compatibility without pickling errors
    le_t = DummyLabelEncoder(LABEL_ORDER)
    y_enc = le_t.transform(y_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        df[FEATURES], y_enc, test_size=0.2, random_state=42, stratify=y_enc)
    sc = StandardScaler()
    Xtr_s = sc.fit_transform(X_train)
    Xte_s = sc.transform(X_test)

    # ── Plot 4: Train/test class proportion check ──────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, (split_y, title) in zip(axes, [
        (y_enc, "Full Dataset"),
        (y_train, "Train Split"),
        (y_test, "Test Split"),
    ]):
        counts = [np.sum(split_y == i) for i in range(3)]
        total = len(split_y)
        bars_ = ax.bar(LABEL_ORDER, counts,
                       color=[PAL[l] for l in LABEL_ORDER], edgecolor="black")
        ax.set_title(f"{title}\n(n={total})")
        ax.set_ylabel("Count")
        ax.set_ylim(0, max(counts) * 1.2)
        for bar_, cnt in zip(bars_, counts):
            ax.text(bar_.get_x() + bar_.get_width() / 2, bar_.get_height() + 2,
                    f"{cnt}\n({cnt/total*100:.0f}%)", ha="center", fontsize=9)
    plt.suptitle("Class Proportions Preserved Across Train/Test Split (stratified)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "4_train_test_class_check.png"), dpi=150)
    plt.close()

    # ── Train classifiers ─────────────────────────────────────────────────
    models_def = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000, random_state=42, class_weight="balanced"),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
        "Random Forest": RandomForestClassifier(
            n_estimators=150, random_state=42, class_weight="balanced"),
    }
    results = {}
    for name, mdl in models_def.items():
        Xtr = Xtr_s if "Logistic" in name else X_train
        Xte = Xte_s if "Logistic" in name else X_test
        mdl.fit(Xtr, y_train)
        yp = mdl.predict(Xte)
        cv = cross_val_score(mdl, Xtr, y_train, cv=5, scoring="accuracy").mean()
        report = classification_report(
            y_test, yp, target_names=LABEL_ORDER, output_dict=True)
        results[name] = {
            "acc":    accuracy_score(y_test, yp),
            "cv":     float(cv),
            "cm":     confusion_matrix(y_test, yp).tolist(),
            "report": report,
            "model":  mdl,
        }

    # ── Plot 5: Confusion matrices ─────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, (name, res) in zip(axes, results.items()):
        ConfusionMatrixDisplay(
            np.array(res["cm"]), display_labels=LABEL_ORDER
        ).plot(ax=ax, colorbar=False, cmap="Blues")
        ax.set_title(f"{name}\nAcc: {res['acc']*100:.1f}%")
    plt.suptitle("Confusion Matrices (class_weight=balanced)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "5_confusion.png"), dpi=150)
    plt.close()

    # ── Plot 6: Model comparison ───────────────────────────────────────────
    mnames = list(results.keys())
    ta = [results[m]["acc"] for m in mnames]
    cv_scores = [results[m]["cv"] for m in mnames]
    x = np.arange(3)
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    b1_ = ax.bar(x - w / 2, ta, w, label="Test Acc", color="#3498db", edgecolor="k")
    b2_ = ax.bar(x + w / 2, cv_scores, w, label="5-Fold CV", color="#9b59b6", edgecolor="k")
    ax.set_xticks(x)
    ax.set_xticklabels(mnames)
    ax.set_ylim(0, 1.1)
    ax.set_title("Model Comparison — Test vs Cross-Validation Accuracy")
    ax.legend()
    for bar in list(b1_) + list(b2_):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{bar.get_height():.2f}", ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "6_model_comparison.png"), dpi=150)
    plt.close()

    # ── Plot 7: Feature importances ───────────────────────────────────────
    rf = results["Random Forest"]["model"]
    imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=True)
    fc = ["#27ae60" if f in ["edu_sm_hours", "self_study_hours", "sleep_hours"]
          else "#e74c3c" for f in imp.index]
    plt.figure(figsize=(9, 5))
    imp.plot(kind="barh", color=fc, edgecolor="k")
    plt.title("Feature Importances — Random Forest\n"
              "(green = positive driver  |  red = negative driver)")
    plt.xlabel("Importance Score")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "7_feature_importances.png"), dpi=150)
    plt.close()

    # ── Plot 8: Decision tree ─────────────────────────────────────────────
    dt = results["Decision Tree"]["model"]
    fig, ax = plt.subplots(figsize=(22, 9))
    plot_tree(dt, feature_names=FEATURES, class_names=LABEL_ORDER,
              filled=True, rounded=True, fontsize=7, ax=ax)
    plt.title("Decision Tree (max_depth=6)")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "8_decision_tree.png"), dpi=100)
    plt.close()

    # ── Plot sanity: Score histogram ──────────────────────────────────────
    plt.figure(figsize=(8, 4))
    plt.hist(df["productivity_score"], bins=30, color="#3498db",
             edgecolor="white", alpha=0.85)
    plt.axvline(5.5, color="#e74c3c", ls="--", lw=2, label="Low/Med boundary (5.5)")
    plt.axvline(7.5, color="#2ecc71", ls="--", lw=2, label="Med/High boundary (7.5)")
    plt.xlabel("Productivity Score")
    plt.ylabel("Count")
    plt.title("Productivity Score Distribution — Sanity Check")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "sanity_score_hist.png"), dpi=150)
    plt.close()

    # ── Pearson correlations ──────────────────────────────────────────────
    pearson_results = {}
    for feat in NUM_FEATS[:-1]:
        r, p = pearsonr(df[feat], df["productivity_score"])
        pearson_results[feat] = {"r": round(float(r), 4), "p": round(float(p), 6)}

    best_model_name = max(results, key=lambda m: results[m]["acc"])

    return {
        "models":        results,
        "scaler":        sc,
        "le_platform":   le_p,
        "le_target":     le_t,
        "lin_model":     lin,
        "lin_r2":        float(r2_score),
        "lin_intercept": float(lin.intercept_),
        "assumed_betas": ASSUMED_BETAS,
        "learned_betas": {k: round(float(v), 4) for k, v in learned_betas.items()},
        "pearson":       pearson_results,
        "label_dist":    {
            "Low":    int(np.sum(y_enc == 0)),
            "Medium": int(np.sum(y_enc == 1)),
            "High":   int(np.sum(y_enc == 2)),
        },
        "best_model":    best_model_name,
        "features":      FEATURES,
        "label_order":   LABEL_ORDER,
        "dataset_shape": list(df.shape),
    }
