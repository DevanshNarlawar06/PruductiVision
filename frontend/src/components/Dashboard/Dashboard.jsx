import { useEffect, useState } from 'react'
import { getMetrics } from '../../services/api'
import './Dashboard.css'

const STRENGTH = r => {
  const a = Math.abs(r)
  if (a < 0.10) return { label: 'negligible', color: '#64748b' }
  if (a < 0.30) return { label: 'weak',       color: '#5c7aea' }
  if (a < 0.50) return { label: 'moderate',   color: '#0b5cad' }
  return               { label: 'strong',     color: '#0a4a8f' }
}

const FEAT_NICE = {
  edu_sm_hours:    'Edu SM Hours',
  ent_sm_hours:    'Ent SM Hours',
  self_study_hours:'Self-Study Hours',
  sleep_hours:     'Sleep Hours',
  leisure_hours:   'Leisure Hours',
}

const MODEL_COLORS = {
  'Logistic Regression': '#0b5cad',
  'Decision Tree':       '#1565c0',
  'Random Forest':       '#1976d2',
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const [activeTab, setActiveTab] = useState('models')

  useEffect(() => {
    getMetrics()
      .then(data => {
        if (data && typeof data === 'object') setMetrics(data)
        else setError('Invalid metrics response')
      })
      .catch(e => setError(e.message || 'Failed to load metrics'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="container dashboard__loading">
      <div className="dashboard__spinner" />
      <p>Loading model metrics</p>
    </div>
  )

  if (error) return (
    <div className="container dashboard__error">
      Could not load metrics: {error}
      <br /><small>Is the FastAPI backend running on port 8000?</small>
    </div>
  )

  if (!metrics) {
    return (
      <div className="container dashboard__error">
        No metrics data. Start the backend with <code>python main.py</code> in <code>backend/</code>.
      </div>
    )
  }

  const {
    models = {},
    pearson = {},
    assumed_betas = {},
    learned_betas = {},
    lin_r2 = 0,
    lin_intercept = 0,
    label_dist = {},
    best_model = '',
    dataset_shape = [0, 0],
  } = metrics

  const n = (dataset_shape[0] || 1)
  const lowP = ((label_dist.Low ?? 0) / n) * 100
  const medP = ((label_dist.Medium ?? 0) / n) * 100
  const highP = ((label_dist.High ?? 0) / n) * 100
  const donutGradient = `conic-gradient(
    var(--label-low) 0% ${lowP}%,
    var(--label-medium) ${lowP}% ${lowP + medP}%,
    var(--label-high) ${lowP + medP}% 100%
  )`

  return (
    <div className="container" id="dashboard-section">
      <div className="dashboard__header">
        <h2 className="section-heading">
          <span className="gradient-text">Model dashboard</span>
        </h2>
        <p className="section-sub">
          Training metrics, Pearson correlations, and beta coefficient analysis
          from the v5.0 pipeline.
        </p>
      </div>

      {/* Dataset info bar */}
      <div className="dashboard__info-bar glass-card">
        <div className="dashboard__info-item">
          <span>Dataset</span>
          <strong>{dataset_shape[0]} × {dataset_shape[1]}</strong>
        </div>
        <div className="dashboard__info-item">
          <span>Best model</span>
          <strong style={{ color: MODEL_COLORS[best_model] }}>{best_model}</strong>
        </div>
        <div className="dashboard__info-item">
          <span>Linear R²</span>
          <strong>{(lin_r2 * 100).toFixed(1)}%</strong>
        </div>
        <div className="dashboard__info-item">
          <span>β₀ (intercept)</span>
          <strong>{lin_intercept > 0 ? '+' : ''}{lin_intercept.toFixed(3)}</strong>
        </div>
        {Object.entries(label_dist).map(([lbl, cnt]) => (
          <div className="dashboard__info-item" key={lbl}>
            <span>{lbl}</span>
            <strong>{cnt} ({(cnt/dataset_shape[0]*100).toFixed(0)}%)</strong>
          </div>
        ))}
      </div>

      {/* Label distribution — CSS donut */}
      <div className="dashboard__donut-row glass-card">
        <div className="dashboard__donut-visual-wrap">
          <div
            className="dashboard__donut-ring"
            style={{ background: donutGradient }}
            role="img"
            aria-label={`Label distribution: Low ${lowP.toFixed(0)}%, Medium ${medP.toFixed(0)}%, High ${highP.toFixed(0)}%`}
          />
          <div className="dashboard__donut-hole" />
        </div>
        <div className="dashboard__donut-legend">
          <h3 className="dashboard__donut-title">Class balance</h3>
          <p className="dashboard__donut-sub">Productivity labels in the synthetic dataset (n = {n})</p>
          <ul>
            <li><span className="dot dot--low" /> Low <strong>{label_dist.Low}</strong> ({lowP.toFixed(0)}%)</li>
            <li><span className="dot dot--med" /> Medium <strong>{label_dist.Medium}</strong> ({medP.toFixed(0)}%)</li>
            <li><span className="dot dot--high" /> High <strong>{label_dist.High}</strong> ({highP.toFixed(0)}%)</li>
          </ul>
        </div>
      </div>

      {/* Tabs */}
      <div className="dashboard__tabs">
        {['models', 'pearson', 'betas'].map(tab => (
          <button
            key={tab}
            id={`dashboard-tab-${tab}`}
            className={`dashboard__tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'models' && 'Models'}
            {tab === 'pearson' && 'Correlations'}
            {tab === 'betas' && 'Beta coefficients'}
          </button>
        ))}
      </div>

      {/* Models tab */}
      {activeTab === 'models' && (
        <div className="dashboard__tab-content">
          <div className="dashboard__model-grid">
            {Object.entries(models).map(([name, res]) => (
              <div
                key={name}
                className={`dashboard__model-card glass-card ${name === best_model ? 'best' : ''}`}
                style={{ '--mc': MODEL_COLORS[name] }}
              >
                {name === best_model && (
                  <span className="dashboard__best-badge">Best</span>
                )}
                <h3 className="dashboard__model-name">{name}</h3>

                <div className="dashboard__acc-row">
                  <div className="dashboard__acc-item">
                    <span>Test Accuracy</span>
                    <div className="dashboard__acc-circle">
                      <svg viewBox="0 0 36 36">
                        <path
                          className="dashboard__acc-track"
                          d="M18 2.0845 a15.9155 15.9155 0 0 1 0 31.831 a15.9155 15.9155 0 0 1 0 -31.831"
                          fill="none"
                          strokeWidth="3"
                        />
                        <path
                          d="M18 2.0845 a15.9155 15.9155 0 0 1 0 31.831 a15.9155 15.9155 0 0 1 0 -31.831"
                          fill="none"
                          stroke={MODEL_COLORS[name]}
                          strokeWidth="3"
                          strokeDasharray={`${(res.test_accuracy * 100).toFixed(1)}, 100`}
                          strokeLinecap="round"
                        />
                        <text x="18" y="20.35" textAnchor="middle" fontSize="7" fill="#14233d" fontWeight="bold">
                          {(res.test_accuracy * 100).toFixed(0)}%
                        </text>
                      </svg>
                    </div>
                  </div>
                  <div className="dashboard__acc-item">
                    <span>5-Fold CV</span>
                    <div className="dashboard__acc-circle">
                      <svg viewBox="0 0 36 36">
                        <path
                          className="dashboard__acc-track"
                          d="M18 2.0845 a15.9155 15.9155 0 0 1 0 31.831 a15.9155 15.9155 0 0 1 0 -31.831"
                          fill="none"
                          strokeWidth="3"
                        />
                        <path
                          d="M18 2.0845 a15.9155 15.9155 0 0 1 0 31.831 a15.9155 15.9155 0 0 1 0 -31.831"
                          fill="none"
                          stroke={MODEL_COLORS[name]}
                          strokeWidth="3"
                          strokeDasharray={`${(res.cv_accuracy * 100).toFixed(1)}, 100`}
                          strokeLinecap="round"
                          opacity="0.6"
                        />
                        <text x="18" y="20.35" textAnchor="middle" fontSize="7" fill="#14233d" fontWeight="bold">
                          {(res.cv_accuracy * 100).toFixed(0)}%
                        </text>
                      </svg>
                    </div>
                  </div>
                </div>

                {/* Per-class F1 */}
                <div className="dashboard__f1">
                  {['Low', 'Medium', 'High'].map(lbl => {
                    const f1 = res.classification_report[lbl]?.['f1-score'] ?? 0
                    return (
                      <div key={lbl} className="dashboard__f1-row">
                        <span className="dashboard__f1-label">{lbl}</span>
                        <div className="dashboard__f1-track">
                          <div
                            className="dashboard__f1-fill"
                            style={{
                              width: `${f1 * 100}%`,
                              background: MODEL_COLORS[name],
                            }}
                          />
                        </div>
                        <span className="dashboard__f1-val">{(f1 * 100).toFixed(0)}%</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pearson tab */}
      {activeTab === 'pearson' && (
        <div className="dashboard__tab-content">
          <div className="dashboard__pearson glass-card">
            <p className="dashboard__pearson-note">
              Correlation with <strong>productivity_score</strong> — Cohen (1988) thresholds
            </p>
            <table className="dashboard__table">
              <thead>
                <tr>
                  <th>Feature</th>
                  <th>r</th>
                  <th>p-value</th>
                  <th>Strength</th>
                  <th>Direction</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(pearson).map(([feat, { r, p }]) => {
                  const s = STRENGTH(r)
                  return (
                    <tr key={feat}>
                      <td>{FEAT_NICE[feat] || feat}</td>
                      <td style={{ fontWeight: 700, color: r > 0 ? '#0b5cad' : '#455a64' }}>
                        {r > 0 ? '+' : ''}{r.toFixed(3)}
                      </td>
                      <td style={{ fontSize: '0.8rem', color: p < 0.05 ? '#0b5cad' : '#64748b' }}>
                        {p.toExponential(2)} {p < 0.001 ? '***' : p < 0.01 ? '**' : p < 0.05 ? '*' : 'ns'}
                      </td>
                      <td style={{ color: s.color, fontWeight: 600 }}>{s.label}</td>
                      <td>{r > 0 ? '↑ positive' : '↓ negative'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Betas tab */}
      {activeTab === 'betas' && (
        <div className="dashboard__tab-content">
          <div className="dashboard__betas glass-card">
            <p className="dashboard__pearson-note">
              Phase 1 (literature) vs Phase 2 (ML learned) — direction agreement validates the dataset
            </p>
            <div className="dashboard__beta-rows">
              {Object.entries(assumed_betas).map(([key, assumed]) => {
                const learned = learned_betas[key] ?? 0
                const match = (assumed > 0) === (learned > 0)
                const maxAbs = Math.max(Math.abs(assumed), Math.abs(learned), 0.1)
                return (
                  <div key={key} className="dashboard__beta-item">
                    <div className="dashboard__beta-name">{key}</div>
                    <div className="dashboard__beta-bars">
                      <div className="dashboard__beta-bar-row">
                        <span>Assumed</span>
                        <div className="dashboard__beta-track">
                          <div
                            className="dashboard__beta-fill"
                            style={{
                              width: `${(Math.abs(assumed) / maxAbs) * 100}%`,
                              background: assumed >= 0 ? '#0b5cad' : '#64748b',
                              marginLeft: assumed >= 0 ? '50%' : `${50 - (Math.abs(assumed)/maxAbs)*50}%`,
                            }}
                          />
                        </div>
                        <span style={{ color: assumed >= 0 ? '#0b5cad' : '#64748b', fontWeight: 700 }}>
                          {assumed >= 0 ? '+' : ''}{assumed.toFixed(2)}
                        </span>
                      </div>
                      <div className="dashboard__beta-bar-row">
                        <span>Learned</span>
                        <div className="dashboard__beta-track">
                          <div
                            className="dashboard__beta-fill"
                            style={{
                              width: `${(Math.abs(learned) / maxAbs) * 100}%`,
                              background: learned >= 0 ? '#1565c0' : '#94a3b8',
                              opacity: 0.65,
                              marginLeft: learned >= 0 ? '50%' : `${50 - (Math.abs(learned)/maxAbs)*50}%`,
                            }}
                          />
                        </div>
                        <span style={{ color: learned >= 0 ? '#1565c0' : '#64748b', fontWeight: 700, opacity: 0.8 }}>
                          {learned >= 0 ? '+' : ''}{learned.toFixed(2)}
                        </span>
                      </div>
                    </div>
                    <span className={`dashboard__beta-match ${match ? 'ok' : 'warn'}`}>
                      {match ? '✓' : '✗'}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
