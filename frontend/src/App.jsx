import Navbar from './components/Navbar/Navbar'
import Hero from './components/Hero/Hero'
import PredictorForm from './components/PredictorForm/PredictorForm'
import Dashboard from './components/Dashboard/Dashboard'
import PlotViewer from './components/PlotViewer/PlotViewer'
import Footer from './components/Footer/Footer'
import './App.css'

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <main>
        <Hero />
        <section id="predictor" className="app-section">
          <PredictorForm />
        </section>
        <section id="dashboard" className="app-section">
          <Dashboard />
        </section>
        <section id="plots" className="app-section">
          <PlotViewer />
        </section>
      </main>
      <Footer />
    </div>
  )
}
