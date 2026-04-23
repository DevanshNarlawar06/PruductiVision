import { useState, useEffect } from 'react'
import './Navbar.css'

const NAV_LINKS = [
  { label: 'Home',      href: '#home' },
  { label: 'Predictor', href: '#predictor' },
  { label: 'Dashboard', href: '#dashboard' },
  { label: 'Plots',     href: '#plots' },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', handler)
    return () => window.removeEventListener('scroll', handler)
  }, [])

  return (
    <header className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`}>
      <div className="navbar__inner container">
        {/* Brand */}
        <a href="#home" className="navbar__brand">
          <span className="navbar__brand-mark" aria-hidden />
          <span className="navbar__brand-name">
            Producti<span className="gradient-text">Vision</span>
          </span>
        </a>

        {/* Desktop nav */}
        <nav className="navbar__links" aria-label="Main navigation">
          {NAV_LINKS.map(link => (
            <a key={link.href} href={link.href} className="navbar__link">
              {link.label}
            </a>
          ))}
        </nav>

        {/* Badge */}
        <div className="navbar__badge">
          PICT · SY_09 · DSM CIE-I
        </div>

        {/* Mobile toggle */}
        <button
          id="navbar-menu-toggle"
          className="navbar__hamburger"
          aria-label="Toggle menu"
          onClick={() => setMenuOpen(o => !o)}
        >
          <span /><span /><span />
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <nav className="navbar__mobile" aria-label="Mobile navigation">
          {NAV_LINKS.map(link => (
            <a
              key={link.href}
              href={link.href}
              className="navbar__mobile-link"
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </a>
          ))}
        </nav>
      )}

    </header>
  )
}
