import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Rankings from './pages/Rankings'
import RosterManager from './pages/RosterManager'
import MatchSummary from './pages/MatchSummary'
import { WorldStateProvider } from './hooks/useData'

export default function App() {
  return (
    <WorldStateProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/rankings" element={<Rankings />} />
          <Route path="/roster" element={<RosterManager />} />
          <Route path="/match/:matchKey" element={<MatchSummary />} />
        </Routes>
      </Layout>
    </WorldStateProvider>
  )
}
