import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { ArrowLeft, AlertTriangle } from 'lucide-react'

export default function RiskAlerts() {
  const navigate = useNavigate()
  const { data, isLoading, error } = useQuery({
    queryKey: ['risk-alerts'],
    queryFn: async () => {
      const response = await api.get('/risk-alerts')
      return response.data
    }
  })

  if (isLoading) return <div className="p-8">Loading...</div>
  if (error) return <div className="p-8 text-red-600">Error loading risk alerts</div>

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-300 text-red-800'
      case 'high':
        return 'bg-orange-100 border-orange-300 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800'
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/')}
                className="mr-4 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <h1 className="text-xl font-bold text-gray-900">Risk Alerts</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {!data || data.length === 0 ? (
            <div className="bg-white shadow rounded-lg p-8 text-center">
              <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No active risk alerts</p>
            </div>
          ) : (
            <div className="space-y-4">
              {data.map((alert: any) => (
                <div
                  key={alert.id}
                  className={`bg-white shadow rounded-lg p-6 border-l-4 ${
                    alert.severity === 'critical' || alert.severity === 'high'
                      ? 'border-red-500'
                      : 'border-yellow-500'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
                        <span
                          className={`px-2 py-1 text-xs font-semibold rounded uppercase ${getSeverityColor(
                            alert.severity
                          )}`}
                        >
                          {alert.severity}
                        </span>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {alert.alert_type.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                      </h3>
                      <p className="text-gray-700 mb-2">{alert.message}</p>
                      <p className="text-sm text-gray-500">
                        Detected: {new Date(alert.detected_at).toLocaleString()}
                      </p>
                    </div>
                    {alert.is_resolved && (
                      <span className="px-3 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded">
                        Resolved
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
