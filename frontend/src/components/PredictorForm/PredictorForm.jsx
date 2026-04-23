import { useState } from 'react'
import { predict } from '../../services/api'
import ResultCard from '../ResultCard/ResultCard'
import './PredictorForm.css'

const PLATFORMS = ['YouTube', 'Instagram', 'Snapchat', 'LinkedIn', 'Discord']

const SLIDERS = [
  {
    key: 'edu_sm_hours',
    label: 'Educational social media (hours/day)',
    desc: 'Tutorials, course content, study-related feeds',
    min: 0, max: 7, step: 0.1, defaultVal: 1.5,
    color: '#0b5cad',
  },
  {
    key: 'ent_sm_hours',
    label: 'Entertainment social media (hours/day)',
    desc: 'Reels, short video, casual scrolling',
    min: 0, max: 7, step: 0.1, defaultVal: 2.5,
    color: '#1565c0',
  },
  {
    key: 'self_study_hours',
    label: 'Self-study (hours/day)',
    desc: 'Assignments, revision, practice outside class',
    min: 0.2, max: 6, step: 0.1, defaultVal: 2.0,
    color: '#1976d2',
  },
  {
    key: 'sleep_hours',
    label: 'Sleep (hours/night)',
    desc: "Typical night's sleep",
    min: 4.5, max: 9.5, step: 0.1, defaultVal: 7.0,
    color: '#1e88e5',
  },
  {
    key: 'leisure_hours',
    label: 'Other leisure (hours/day)',
    desc: 'Sports, hobbies, offline downtime',
    min: 0.1, max: 2.5, step: 0.1, defaultVal: 0.8,
    color: '#42a5f5',
  },
]

const DEFAULT_FORM = Object.fromEntries(
  SLIDERS.map(s => [s.key, s.defaultVal])
)

export default function PredictorForm() {
  const [form, setForm] = useState({ ...DEFAULT_FORM, platform: 'YouTube' })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSlider = (key, val) => {
    setForm(f => ({ ...f, [key]: parseFloat(val) }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await predict(form)
      setResult(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const totalSM = (form.edu_sm_hours + form.ent_sm_hours).toFixed(1)
  const rawSum =
    form.sleep_hours + 6 + 2 + form.edu_sm_hours +
    form.ent_sm_hours + form.self_study_hours + form.leisure_hours
  const rawTotalHours = Math.round(rawSum * 10) / 10
  const totalHours = Math.min(rawTotalHours, 24).toFixed(1)
  const isOverBudget = rawTotalHours > 24
  const untrackedHours = Math.max(0, 24 - rawTotalHours).toFixed(1)

  return (
    <div className="container">
      <div className="predictor__header">
        <h2 className="section-heading">
          Productivity <span className="gradient-text">predictor</span>
        </h2>
        <p className="section-sub">
          Outputs <strong>Low</strong>, <strong>Medium</strong>, or <strong>High</strong> using the
          best-performing model on the test split, plus class probabilities and a linear score estimate.
        </p>
      </div>

      <div className="predictor__layout">
        <form
          id="productivity-predictor-form"
          className="predictor__form glass-card"
          onSubmit={handleSubmit}
        >
          <div className="predictor__budget">
            <div className="predictor__budget-label">
              <span>Approx. accounted hours (incl. college 6h + care 2h)</span>
              <span className={isOverBudget ? 'budget-over' : 'budget-ok'}>
                {isOverBudget ? '24.0' : totalHours}h / 24h
              </span>
            </div>
            <div className="predictor__budget-bar">
              <div
                className="predictor__budget-fill"
                style={{ width: `${Math.min((rawTotalHours / 24) * 100, 100)}%` }}
              />
            </div>
          </div>

          {SLIDERS.map(s => {
            const pct = ((form[s.key] - s.min) / (s.max - s.min)) * 100
            return (
              <div key={s.key} className="predictor__field">
                <div className="predictor__field-header">
                  <div className="predictor__field-meta">
                    <label htmlFor={`slider-${s.key}`} className="predictor__field-label">
                      {s.label}
                    </label>
                    <span className="predictor__field-desc">{s.desc}</span>
                  </div>
                  <span className="predictor__field-value" style={{ color: s.color }}>
                    {form[s.key].toFixed(1)}h
                  </span>
                </div>
                <input
                  id={`slider-${s.key}`}
                  type="range"
                  min={s.min}
                  max={s.max}
                  step={s.step}
                  value={form[s.key]}
                  onChange={e => handleSlider(s.key, e.target.value)}
                  className="predictor__slider"
                  style={{ '--pct': `${pct}%`, '--thumb-color': s.color }}
                />
                <div className="predictor__slider-range">
                  <span>{s.min}h</span><span>{s.max}h</span>
                </div>
              </div>
            )
          })}

          <div className="predictor__field">
            <div className="predictor__field-header">
              <div className="predictor__field-meta">
                <span className="predictor__field-label">Primary platform</span>
                <span className="predictor__field-desc">Dominant app for social media time</span>
              </div>
            </div>
            <div className="predictor__platforms">
              {PLATFORMS.map(p => (
                <button
                  key={p}
                  type="button"
                  id={`platform-btn-${p.toLowerCase()}`}
                  className={`predictor__platform-btn ${form.platform === p ? 'active' : ''}`}
                  onClick={() => setForm(f => ({ ...f, platform: p }))}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="predictor__sm-summary">
            <div className="predictor__sm-item" style={{ '--c': '#0b5cad' }}>
              <span>Educational SM</span>
              <strong>{form.edu_sm_hours.toFixed(1)}h</strong>
            </div>
            <div className="predictor__sm-divider">+</div>
            <div className="predictor__sm-item" style={{ '--c': '#1565c0' }}>
              <span>Entertainment SM</span>
              <strong>{form.ent_sm_hours.toFixed(1)}h</strong>
            </div>
            <div className="predictor__sm-divider">=</div>
            <div className="predictor__sm-item" style={{ '--c': '#14233d' }}>
              <span>Total SM</span>
              <strong>{totalSM}h</strong>
            </div>
          </div>
          
          <div className="predictor__sm-summary" style={{ marginTop: '1rem' }}>
             <div className="predictor__sm-item" style={{ '--c': '#607d8b' }}>
              <span>Untracked Time (Sleep/College/Care/Forms)</span>
              <strong>{untrackedHours}h</strong>
            </div>
          </div>

          <button
            id="predict-submit-btn"
            type="submit"
            className="btn-primary predictor__submit"
            disabled={loading || isOverBudget}
          >
            {loading ? (
              <><span className="predictor__spinner" aria-hidden />Running prediction</>
            ) : isOverBudget ? (
              'Hours exceed 24! Please reduce.'
            ) : (
              'Run prediction'
            )}
          </button>

          {error && (
            <div className="predictor__error" role="alert">
              {error}
            </div>
          )}
        </form>

        <div className="predictor__result-panel">
          {result ? (
            <ResultCard result={result} />
          ) : (
            <div className="predictor__placeholder glass-card">
              <div className="predictor__placeholder-mark" aria-hidden />
              <p>Results appear here after you run the predictor.</p>
              <p className="predictor__placeholder-sub">
                Ensure the FastAPI server is running on port 8000.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
