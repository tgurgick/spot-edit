import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import Upload from './pages/Upload';
import Confirm from './pages/Confirm';
import { Templates } from './pages/Templates';
import { Edit } from './pages/Edit';

function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  // Don't show navigation on the Edit page for a cleaner interface
  const showNav = !location.pathname.startsWith('/edit/');

  return (
    <div className="min-h-screen bg-gray-50">
      {showNav && (
        <nav className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <Link to="/" className="flex items-center gap-2">
                <svg
                  className="w-8 h-8 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
                <span className="text-xl font-bold text-gray-900">Spot Edit</span>
              </Link>

              <div className="flex items-center gap-4">
                <Link
                  to="/"
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    location.pathname === '/'
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  Home
                </Link>
                <Link
                  to="/templates"
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    location.pathname === '/templates'
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  Templates
                </Link>
                <Link
                  to="/upload"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Upload
                </Link>
              </div>
            </div>
          </div>
        </nav>
      )}
      <main>{children}</main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/confirm" element={<Confirm />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/edit/:id" element={<Edit />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
