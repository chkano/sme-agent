import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { ArrowLeft, TrendingUp, AlertTriangle } from 'lucide-react'

export default function FinancialHealth() {
  const navigate = useNavigate()
  const { data, isLoading, error } = useQuery({
    queryKey: ['financial-health'],
    queryFn: async () => {
      const response = await api.post('/financial-health')
      return response.data
    }
  })

  if (isLoading) return <div className="p-8">Loading...</div>
  if (error) return <div className="p-8 text-red-600">Error loading financial health data</div>

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-red-600'
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
              <h1 className="text-xl font-bold text-gray-900">Financial Health</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Financial Health Index</h2>
                <p className="text-gray-600 mt-1">Current assessment of your financial health</p>
              </div>
              <div className={`text-5xl font-bold ${getScoreColor(data?.fhi_score || 0)}`}>
                {data?.fhi_score?.toFixed(1) || 'N/A'}
              </div>
            </div>
          </div>

          {data?.explanation && (
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Explanation</h3>
              <p className="text-gray-700">{data.explanation}</p>
            </div>
          )}

          {data?.recommendations && data.recommendations.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                Recommendations
              </h3>
              <ul className="list-disc list-inside space-y-2">
                {data.recommendations.map((rec: string, idx: number) => (
                  <li key={idx} className="text-gray-700">{rec}</li>
                ))}
              </ul>
            </div>
          )}

          {data?.risk_flags && data.risk_flags.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2 text-red-600" />
                Risk Flags
              </h3>
              <div className="space-y-3">
                {data.risk_flags.map((risk: any, idx: number) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border ${
                      risk.severity === 'high'
                        ? 'bg-red-50 border-red-200'
                        : risk.severity === 'medium'
                        ? 'bg-yellow-50 border-yellow-200'
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{risk.type}</div>
                    <div className="text-sm text-gray-600 mt-1">{risk.message}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {data?.metrics && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Key Metrics</h3>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(data.metrics).map(([key, value]) => (
                  <div key={key} className="border-b pb-2">
                    <div className="text-sm text-gray-600 capitalize">{key.replace(/_/g, ' ')}</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {typeof value === 'number' ? value.toLocaleString() : String(value)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
