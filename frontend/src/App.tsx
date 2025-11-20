import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold text-gray-900">Spot Edit</h1>
            <p className="mt-1 text-sm text-gray-600">AI-Powered Document Editor</p>
          </div>
        </header>
        <main>
          <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={
                <div className="px-4 py-6 sm:px-0">
                  <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
                    <div className="text-center">
                      <h2 className="text-2xl font-semibold text-gray-700">Welcome to Spot Edit</h2>
                      <p className="mt-2 text-gray-500">Frontend is ready for development</p>
                    </div>
                  </div>
                </div>
              } />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}

export default App
