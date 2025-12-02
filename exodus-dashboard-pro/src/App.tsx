import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useStore } from './lib/store'
import ErrorBoundary from './components/ErrorBoundary'
import Sidebar from './components/Sidebar'
import MobileNav from './components/MobileNav'
import { WebPhone } from './components/WebPhone'
import DashboardHome from './pages/DashboardHome'
import Campaigns from './pages/Campaigns'
import Leads from './pages/Leads'
import LiveCalls from './pages/LiveCalls'
import CallHistory from './pages/CallHistory'
import DNCList from './pages/DNCList'
import Bots from './pages/Bots'
import Settings from './pages/Settings'
import SoundVisualizerDemo from './pages/SoundVisualizerDemo'

function App() {
  const darkMode = useStore((state) => state.darkMode)

  // Apply dark mode class on mount and when it changes
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  return (
    <ErrorBoundary>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className={darkMode ? 'dark' : ''}>
          <div className="flex h-screen bg-dark-1 overflow-hidden">
            {/* Desktop Sidebar */}
            <Sidebar />
            
            {/* Main Content */}
            <main className="flex-1 overflow-y-auto pb-20 md:pb-0">
              <Routes>
                <Route path="/" element={<DashboardHome />} />
                <Route path="/campaigns" element={<Campaigns />} />
                <Route path="/leads" element={<Leads />} />
                <Route path="/live-calls" element={<LiveCalls />} />
                <Route path="/call-history" element={<CallHistory />} />
                <Route path="/dnc" element={<DNCList />} />
                <Route path="/bots" element={<Bots />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/visualizer" element={<SoundVisualizerDemo />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>

            {/* Browser-Based Web Phone (Bottom Right) */}
            <div className="fixed bottom-4 right-4 z-50 w-80 hidden md:block">
              <WebPhone />
            </div>

            {/* Mobile Bottom Nav */}
            <MobileNav />
          </div>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
