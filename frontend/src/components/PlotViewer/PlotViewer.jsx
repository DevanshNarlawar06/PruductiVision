import { useEffect, useState } from 'react'
import { getPlotList, API_BASE } from '../../services/api'
import './PlotViewer.css'

function plotSrc(relativeUrl) {
  if (!relativeUrl) return ''
  if (relativeUrl.startsWith('http')) return relativeUrl
  return `${API_BASE}${relativeUrl}`
}

export default function PlotViewer() {
  const [plots, setPlots]       = useState([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)
  const [lightbox, setLightbox] = useState(null)   // { key, label }

  useEffect(() => {
    getPlotList()
      .then(data => setPlots(Array.isArray(data) ? data : []))
      .catch(e => setError(e.message || 'Failed to load plot list'))
      .finally(() => setLoading(false))
  }, [])

  // Close on Escape
  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') setLightbox(null) }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  if (loading) return (
    <div className="container plots__loading">
      <div className="plots__spinner" />
      <p>Loading plots</p>
    </div>
  )

  if (error) return (
    <div className="container plots__error">{error}</div>
  )

  return (
    <div className="container" id="plots-section">
      <div className="plots__header">
        <h2 className="section-heading">
          <span className="gradient-text">Analysis plots</span>
        </h2>
        <p className="section-sub">
          Figures from the v5.0 training pipeline (11 total). Select a thumbnail to view full size.
        </p>
      </div>

      <div className="plots__grid">
        {(Array.isArray(plots) ? plots : []).map((plot, i) => (
          <button
            key={plot.key}
            id={`plot-card-${plot.key}`}
            className="plots__card glass-card"
            onClick={() => setLightbox(plot)}
            style={{ animationDelay: `${i * 40}ms` }}
          >
            <div className="plots__img-wrap">
              <img
                src={plotSrc(plot.url)}
                alt={plot.label}
                className="plots__img"
                loading="lazy"
              />
              <div className="plots__img-overlay">
                <span className="plots__zoom-label">Open</span>
              </div>
            </div>
            <p className="plots__card-label">{plot.label}</p>
          </button>
        ))}
      </div>

      {/* Lightbox */}
      {lightbox && (
        <div
          className="plots__lightbox"
          onClick={e => { if (e.target === e.currentTarget) setLightbox(null) }}
          role="dialog"
          aria-modal="true"
          aria-label={lightbox.label}
        >
          <div className="plots__lightbox-inner">
            <button
              className="plots__lightbox-close"
              id="plots-lightbox-close"
              onClick={() => setLightbox(null)}
              aria-label="Close"
            >
              ✕
            </button>
            <p className="plots__lightbox-title">{lightbox.label}</p>
            <img
              src={plotSrc(lightbox.url)}
              alt={lightbox.label}
              className="plots__lightbox-img"
            />
          </div>
        </div>
      )}
    </div>
  )
}
