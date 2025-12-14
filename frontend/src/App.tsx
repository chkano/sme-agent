import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import FinancialHealth from './pages/FinancialHealth'
import CreditScore from './pages/CreditScore'
import RiskAlerts from './pages/RiskAlerts'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import './App.css'

const queryClient = new QueryClient()

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/financial-health"
              element={
                <ProtectedRoute>
                  <FinancialHealth />
                </ProtectedRoute>
              }
            />
            <Route
              path="/credit-score"
              element={
                <ProtectedRoute>
                  <CreditScore />
                </ProtectedRoute>
              }
            />
            <Route
              path="/risk-alerts"
              element={
                <ProtectedRoute>
                  <RiskAlerts />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
