import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import FighterProfile from './pages/FighterProfile'
import Rankings from './pages/Rankings'
import Schedule from './pages/Schedule'
import FightNarrative from './pages/FightNarrative'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/fighter/:id" element={<FighterProfile />} />
        <Route path="/rankings" element={<Rankings />} />
        <Route path="/schedule" element={<Schedule />} />
        <Route path="/match/:id" element={<FightNarrative />} />
      </Routes>
    </Layout>
  )
}
