import { Component } from 'react'

export default class ErrorBoundary extends Component {
  state = { hasError: false, message: '' }

  static getDerivedStateFromError(err) {
    return { hasError: true, message: err?.message || 'Unknown error' }
  }

  componentDidCatch(err, info) {
    console.error('UI error:', err, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: '100vh',
            padding: '2rem',
            background: '#f6f8fc',
            color: '#14233d',
            fontFamily: 'IBM Plex Sans, system-ui, sans-serif',
            maxWidth: 640,
            margin: '0 auto',
          }}
        >
          <h1 style={{ fontSize: '1.25rem', marginBottom: '1rem', fontWeight: 600 }}>
            Something went wrong
          </h1>
          <p style={{ color: '#455a64', marginBottom: '1rem', lineHeight: 1.5 }}>
            {this.state.message}
          </p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: 6,
              border: '1px solid #0b5cad',
              cursor: 'pointer',
              background: '#0b5cad',
              color: '#fff',
              fontWeight: 600,
              fontFamily: 'inherit',
            }}
          >
            Reload page
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
