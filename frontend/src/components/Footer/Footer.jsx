import './Footer.css'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer__line" />
      <div className="container footer__inner">
        <div className="footer__brand">
          <span className="footer__brand-mark" aria-hidden />
          <span className="footer__brand-name">
            Producti<span className="gradient-text">Vision</span>
          </span>
        </div>

        <div className="footer__info">
          <p>Social media use and student productivity — ML pipeline <strong>v5.0</strong></p>
          <p className="footer__meta">
            PICT &nbsp;·&nbsp; SY_09 &nbsp;·&nbsp; DSM CIE-I
          </p>
        </div>

        <div className="footer__stack">
          {['React', 'FastAPI', 'scikit-learn', 'Python'].map(t => (
            <span key={t} className="footer__tag">{t}</span>
          ))}
        </div>
      </div>
      <div className="footer__copy">
        © {new Date().getFullYear()} PICT SY_09 · DSM CIE-I
      </div>
    </footer>
  )
}
