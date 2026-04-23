# Project Q&A Documentation
## Social Media vs Student Productivity (ML Pipeline v5.0)

This document summarizes the questions and doubts raised during the project development, along with the detailed explanations provided.

---

### 1. Backend Components and Files
**Question: Explain all the components/files in the backend with their purpose.**

The FastAPI backend is strictly modularized to separate Machine Learning business logic from API routing logic.

**Core Backend Files:**
*   **`main.py`**: The main entry point. It manages the `lifespan` event (creating/training models at startup if absent), configures CORS for React, and registers route modules.
*   **`schemas.py`**: Contains `pydantic` classes that validate Data Transfer Objects (DTOs), ensuring strict typing for incoming user frontend data.
*   **`requirements.txt`**: Declares Python package dependencies.
*   **`models/`**: Storage directory where `.joblib` Machine Learning models are serialized and saved so they do not have to be retrained on every boot.
*   **`plots/`**: Stores static `.png` images generated during the training pipeline (heatmaps, EDA distributions).

**Machine Learning Logic (`ml/`):**
*   **`generate_dataset.py`**: Programmatically generates a synthetic dataset based on strict statistical bounds (N=600).
*   **`train.py`**: Pre-processes data, trains algorithms (Logistic Regression, Decision Trees, Random Forest), calculates scores, and generates Seaborn/Matplotlib graphs.
*   **`model_artifacts.py`**: Handles safely serializing/deserializing the scikit-learn models from disk via joblib.
*   **`model_store.py`**: A Singleton holding the trained models in RAM so endpoints can predict instantly.

**API Routes (`routes/`):**
*   **`predict.py`**: Exposes `POST /api/predict`. Accepts model inputs, runs inference (`predict_proba`), and returns productivity classifications.
*   **`metrics.py`**: Exposes `GET /api/metrics`. Returns cross-validation and accuracy scores for dynamic dashboards.
*   **`plots.py`**: Exposes `GET /api/plots/list`. Returns generated ML charts over HTTP.

---

### 2. Replacing TikTok with Snapchat
**Action: Replace "TikTok" with "Snapchat" everywhere.**

TikTok was successfully refactored out of the application and replaced with Snapchat. This required updates across:
*   The React frontend form variables (`PredictorForm.jsx`).
*   FastAPI request validation schemas (`schemas.py`).
*   The data generation platform dictionary (`generate_dataset.py`).
*   The labels generated in our plotting system (`train.py`).

Because the underlying data logic was changed, the old `models/trained_bundle.joblib` was deleted to trigger the backend's `lifespan` event to freshly synthesize data and retrain using "Snapchat".

---

### 3. Beta Assumed Values and Mathematical Implications
**Question: In generating the dataset, how did we assume the Beta (β) values, and what is the mathematical implication?**

The Beta values (`B_EDU = +0.55`, `B_ENT = -0.50`, etc.) dictate how different features impact the final productivity score before random noise is applied. These were chosen for mathematical data stability:

1.  **Preventing Class Imbalance (Centering the Bell Curve):** By keeping the baseline `B0 = 5.8`, an average student lands mathematically near the middle of the "Medium" (5.5 - 7.5) category. If the intercept were too high (e.g., 8.0), 90% of students would be classified as "High", breaking the ML models.
2.  **Bounding the Extrema:** The weights restrict the maximum positive/negative pull to ~4.0 points. This keeps absolute worst-case students from dropping below a 0/10 score, and best-case students from exceeding a 10/10 score.
3.  **Tuning the Decision Boundary Difficulty:** Positive study weight (`+0.65`) outpaces the negative entertainment penalty (`-0.50`). This prevents linear separation and ensures the model finds nuanced overlap points (e.g. high social media + high study = high productivity), forcing Random Forest to do actual work.
4.  **Injecting Noise (`np.random.normal(0, 0.55)`):** Adds mathematical fuzziness across the boundaries so $R^2$ is not a perfectly flat, fake `1.0`.

---

### 4. Correlation in the Model
**Question: Where and how have we used correlation (inter-feature) in our model?**

Correlation exists fundamentally in generating the data, and analytically in evaluating it.

**Data Generation (Zero-Sum Inter-Feature Correlation):**
Instead of randomly picking behaviors, we mathematically force independent variables to relate to each other.
*   **Late-Night Effect:** `sleep_penalty = max(0, (ent_sm - 2.0) * 0.20)`. Forces Entertainment social media to aggressively correlate with sleep loss.
*   **Time-Competition:** Higher screen time dynamically lowers the statistical probability that a student will self-study in the data generator.

**Validation & Analysis:**
*   **Pearson Heatmap (Plot 1):** Pandas `.corr()` builds an exhaustive feature vs. feature matrix to visualize correlation strength across all inputs.
*   **Scatter Validations (Plot 2b):** SciPy’s `pearsonr` proves the synthesized data worked, outputting explicit negative "$r$" coefficients on the charts (e.g., Ent SM vs Sleep).
*   **API Export:** The backend calculates $r$ and $p$ values for every feature against productivity and serves them to the React frontend via `/api/metrics` so you have dynamic, real-world metric cards.

---

### 5. Models Trained and Logistic Regression Logic
**Question: What models did we train, how many epochs/iterations, and what is the logic behind Logistic Regression?**

The pipeline utilizes traditional `scikit-learn` Machine Learning, meaning we iterate upon mathematical gradients rather than Deep Learning "epochs".

**Models Trained:**
1.  **Decision Tree (`max_depth=6`):** Captures multi-variable boundaries perfectly mimicking human logic. Depth is capped to prevent infinite leafing/overfitting.
2.  **Random Forest (`n_estimators=150`):** An ensemble architecture taking a majority vote of 150 separate decision trees to prevent single-tree instability and to extract definitive "Feature Importances" (Plot 7).
3.  **Logistic Regression (`max_iter=2000`):** Provides a mathematical probability baseline.

**The Logic behind Logistic Regression:**
Despite the name, it is a *classifier*.
*   **Probability:** It computes the linear dot-product sum of inputs and squashes the result through a Sigmoid (Softmax) curve between `0.0` and `1.0`. This gives prediction probabilities.
*   **Algorithm Steps (`max_iter`):** A gradient descent solver steps down an error curve mathematically hunting for optimal weights. We cap it at 2000 steps to guarantee convergence without stalling.
*   **Scaling Requirement:** Because it calculates weight-adjustments based on magnitudes, we must mathematically normalize (`StandardScaler`) the features. Otherwise, raw "minutes" would overpower "hours" simply because the numerical float values are vastly larger.
*   **Balanced Class Weights:** To combat any minor remaining class generation imbalance, `class_weight="balanced"` mathematically multiplies the error penalty of a minority class during back-propagation.
