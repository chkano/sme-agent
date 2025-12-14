import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { TrendingUp, AlertTriangle, FileText, BarChart3 } from 'lucide-react'

export default function Dashboard() {
  const navigate = useNavigate()
  const { logout } = useAuth()

  const cards = [
    {
      title: 'Financial Health',
      description: 'View your Financial Health Index and metrics',
      icon: TrendingUp,
      route: '/financial-health',
      color: 'bg-blue-500'
    },
    {
      title: 'Credit Score',
      description: 'Check your credit readiness score',
      icon: BarChart3,
      route: '/credit-score',
      color: 'bg-green-500'
    },
    {
      title: 'Risk Alerts',
      description: 'View active risk alerts and warnings',
      icon: AlertTriangle,
      route: '/risk-alerts',
      color: 'bg-red-500'
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Credit Intelligence Platform</h1>
            </div>
            <div className="flex items-center">
              <button
                onClick={logout}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h2>
          
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {cards.map((card) => {
              const Icon = card.icon
              return (
                <div
                  key={card.route}
                  onClick={() => navigate(card.route)}
                  className="bg-white overflow-hidden shadow rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
                >
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className={`flex-shrink-0 ${card.color} rounded-md p-3`}>
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">
                            {card.title}
                          </dt>
                          <dd className="text-sm text-gray-900 mt-1">
                            {card.description}
                          </dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </main>
    </div>
  )
}
