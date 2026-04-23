# Project Tech Stack 
## Social Media vs Student Productivity (ML Pipeline v5.0)

A complete breakdown of the technologies used to power the Frontend, Backend, and Machine Learning components.

---

### 🎨 Frontend Stack (User Interface)
*   **React:** The core JavaScript library used for building the user interface, component architecture, and state management (e.g., the `PredictorForm`).
*   **Vite:** A blazing fast modern build tool and development server. Used to handle hot-module-reloading much faster than traditional Create React App.
*   **Axios:** A promise-based HTTP client used inside `api.js` to send requests (like form submissions) to the FastAPI backend and fetch metrics/plots.
*   **Vanilla CSS:** Used for custom styling directly in `.css` files rather than relying on heavy component libraries.
*   **Node.js & npm:** The default runtime and package manager used to install dependencies and run the frontend build scripts.

---

### ⚙️ Backend Stack (API & Routing)
*   **FastAPI:** A modern, incredibly fast Python web framework used to expose endpoints (`/api/predict`, `/api/metrics`). It inherently handles asynchronous requests seamlessly.
*   **Uvicorn:** The lightning-fast ASGI (Asynchronous Server Gateway Interface) web server you run in the terminal (`uvicorn main:app --reload`) that actually hosts the FastAPI application.
*   **Pydantic:** A data validation library integrated deeply into FastAPI. It powers `schemas.py`, instantly rejecting bad API requests if the frontend sends invalid types (e.g., sending a string when a float was expected).
*   **Python 3:** The core language powering the entire backend architecture.

---

### 🧠 Machine Learning & Data Science Stack
*   **Scikit-Learn (`sklearn`):** The heavyweight library powering the actual Machine Learning pipeline. It provides the models (`LogisticRegression`, `RandomForestClassifier`, `DecisionTreeClassifier`), pre-processors (`StandardScaler`, `LabelEncoder`), and cross-validation tools.
*   **Pandas:** The data manipulation library used to create, slice, and group the `DataFrame` structure in `generate_dataset.py` and `train.py`.
*   **NumPy:** Used heavily under the hood by Pandas, and explicitly in the data generator to calculate hard boundary statistical limits (`np.clip`, `np.random.normal`, `np.random.lognormal`).
*   **Matplotlib & Seaborn:** The visualization powerhouses. Matplotlib provides the skeleton of the figure layout (`plt.subplots`), while Seaborn paints the beautiful statistical heatmaps and boxplots.
*   **SciPy:** A scientific mathematics library specifically imported (`scipy.stats.pearsonr`) to dynamically calculate $r$-value and $p$-value correlation coefficients.
*   **Joblib:** A serialization library highly optimized for large numpy arrays. It freezes your trained `scikit-learn` pipeline and saves it to the hard drive as a `.joblib` file, allowing instantaneous startup without retraining.
