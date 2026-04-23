import './Hero.css'

const STATS = [
  { value: '600', label: 'Synthetic records' },
  { value: '3', label: 'Classifiers' },
  { value: '11', label: 'Figures' },
  { value: 'v5.0', label: 'Pipeline' },
]

export default function Hero() {
  return (
    <section id="home" className="hero">
      <div className="container hero__inner">
        <div className="hero__tag">
          <span className="hero__tag-dot" />
          PICT · SY_09 · DSM CIE-I · v5.0
        </div>

        <h1 className="hero__title">
          Social media use and<br />
          <span className="gradient-text">student productivity</span>
        </h1>

        <p className="hero__subtitle">
          Compares logistic regression, decision tree, and random forest on a
          synthetic, research-style dataset (600 rows). Enter daily habits below
          to get a predicted productivity class and score estimate.
        </p>

        <div className="hero__ctas">
          <a href="#predictor" className="btn-primary" id="hero-cta-predict">
            Open predictor
          </a>
          <a href="#dashboard" className="hero__link" id="hero-cta-dashboard">
            Training metrics
          </a>
        </div>

        <div className="hero__stats">
          {STATS.map(s => (
            <div key={s.label} className="hero__stat glass-card">
              <span className="hero__stat-value">{s.value}</span>
              <span className="hero__stat-label">{s.label}</span>
            </div>
          ))}
        </div>

        <div className="hero__pills">
          {[
            'Stratified train/test split',
            'Balanced class weights',
            'Pearson vs score',
            'OLS beta check',
            '5-fold CV',
            'Platform encoding',
          ].map(p => (
            <span key={p} className="hero__pill">{p}</span>
          ))}
        </div>
      </div>

      <div className="hero__scroll-hint">
        <span>More below</span>
        <div className="hero__scroll-arrow" />
      </div>
    </section>
  )
}
