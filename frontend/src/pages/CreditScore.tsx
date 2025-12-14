import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { ArrowLeft, TrendingUp } from 'lucide-react'

export default function CreditScore() {
  const navigate = useNavigate()
  const { data, isLoading, error } = useQuery({
    queryKey: ['credit-score'],
    queryFn: async () => {
      const response = await api.post('/credit-score')
      return response.data
    }
  })

  if (isLoading) return <div className="p-8">Loading...</div>
  if (error) return <div className="p-8 text-red-600">Error loading credit score</div>

  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
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
              <h1 className="text-xl font-bold text-gray-900">Credit Score</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Financial Strength Score</h2>
                <p className="text-gray-600 mt-1">Your credit readiness assessment</p>
              </div>
              <div className={`text-5xl font-bold ${getScoreColor(data?.score || 0)}`}>
                {data?.score?.toFixed(1) || 'N/A'}
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

          {data?.risk_factors && data.risk_factors.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Risk Factors</h3>
              <div className="space-y-2">
                {data.risk_factors.map((risk: any, idx: number) => (
                  <div key={idx} className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                    <div className="text-sm text-gray-700">{risk.message}</div>
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
