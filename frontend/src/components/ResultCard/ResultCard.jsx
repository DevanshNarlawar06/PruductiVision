import { useEffect, useRef } from 'react'
import './ResultCard.css'

const LABEL_CONFIG = {
  Low: {
    letter: 'L',
    color: '#3d5a80',
    bg: 'rgba(61, 90, 128, 0.08)',
    border: 'rgba(61, 90, 128, 0.35)',
  },
  Medium: {
    letter: 'M',
    color: '#0b5cad',
    bg: 'rgba(11, 92, 173, 0.08)',
    border: 'rgba(11, 92, 173, 0.35)',
  },
  High: {
    letter: 'H',
    color: '#1565c0',
    bg: 'rgba(21, 101, 192, 0.1)',
    border: 'rgba(21, 101, 192, 0.35)',
  },
}

const MODEL_LABELS = {
  'Logistic Regression': 'LR',
  'Decision Tree': 'DT',
  'Random Forest': 'RF',
}

function ProbBar({ label, value, color }) {
  const barRef = useRef(null)
  useEffect(() => {
    if (barRef.current) {
      setTimeout(() => {
        barRef.current.style.width = `${value * 100}%`
      }, 100)
    }
  }, [value])

  return (
    <div className="result__prob-row">
      <span className="result__prob-label">{label}</span>
      <div className="result__prob-track">
        <div
          ref={barRef}
          className="result__prob-fill"
          style={{ background: color }}
        />
      </div>
      <span className="result__prob-pct">{(value * 100).toFixed(1)}%</span>
    </div>
  )
}

export default function ResultCard({ result }) {
  const cfg = LABEL_CONFIG[result.label] || LABEL_CONFIG.Medium

  return (
    <div className="result glass-card result--animate">
      <div className="result__verdict" style={{ borderColor: cfg.border, background: cfg.bg }}>
        <span
          className="result__label-badge"
          style={{
            color: cfg.color,
            borderColor: cfg.border,
            background: 'var(--bg-elevated)',
          }}
          aria-hidden
        >
          {cfg.letter}
        </span>
        <div className="result__verdict-text">
          <span className="result__verdict-sub">Predicted productivity</span>
          <span className="result__verdict-label" style={{ color: cfg.color }}>
            {result.label}
          </span>
        </div>
        <div className="result__score-badge">
          <span className="result__score-val">{result.score_estimate}</span>
          <span className="result__score-unit">/ 10</span>
        </div>
      </div>

      <div className="result__meta">
        Best model: <strong>{result.model_used}</strong>
      </div>

      <div className="result__section">
        <h4 className="result__section-title">Class probabilities</h4>
        {Object.entries(result.probabilities).map(([lbl, val]) => (
          <ProbBar
            key={lbl}
            label={lbl}
            value={val}
            color={LABEL_CONFIG[lbl]?.color || '#0b5cad'}
          />
        ))}
      </div>

      <div className="result__section">
        <h4 className="result__section-title">All model predictions</h4>
        <div className="result__model-grid">
          {Object.entries(result.all_model_predictions).map(([name, pred]) => {
            const c = LABEL_CONFIG[pred.label] || LABEL_CONFIG.Medium
            return (
              <div
                key={name}
                className="result__model-card"
                style={{ borderColor: c.border, background: c.bg }}
              >
                <span className="result__model-short">{MODEL_LABELS[name] || name}</span>
                <span className="result__model-label" style={{ color: c.color }}>
                  {pred.label}
                </span>
                <span className="result__model-conf">
                  {(pred.confidence * 100).toFixed(0)}%
                </span>
                <span className="result__model-name">{name}</span>
              </div>
            )
          })}
        </div>
      </div>

      <div className="result__insight">
        <p>
          {result.label === 'High' &&
            'Strong pattern: more educational social media and self-study, with adequate sleep, aligns with higher productivity in this model.'}
          {result.label === 'Medium' &&
            'Mixed signal. Shifting time from entertainment feeds toward study blocks or sleep often moves cases toward the High bucket in this dataset.'}
          {result.label === 'Low' &&
            'High entertainment social media relative to sleep and study is associated with lower predicted productivity; tightening daily scroll time may help.'}
        </p>
      </div>
    </div>
  )
}
