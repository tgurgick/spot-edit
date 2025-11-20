import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DocumentUpload from '../components/DocumentUpload';
import { uploadDocument } from '../api/client';

export default function Upload() {
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUploadSuccess = async (file: File) => {
    setError(null);
    setIsUploading(true);

    try {
      const response = await uploadDocument(file);

      // Navigate to confirmation page with the uploaded document data
      navigate('/confirm', {
        state: {
          documentText: response.documentText,
          detectedFields: response.detectedFields,
          fileName: file.name,
        },
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload document';
      setError(errorMessage);
      setIsUploading(false);
    }
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Spot Edit</h1>
              <p className="text-sm text-gray-600 mt-1">
                AI-powered document editing assistant
              </p>
            </div>
            <button
              onClick={() => navigate('/templates')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              View Templates
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-3xl mx-auto">
          {/* Page Header */}
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-gray-900">Upload Document</h2>
            <p className="text-gray-600 mt-2">
              Upload your document to get started. Our AI will automatically detect editable
              fields.
            </p>
          </div>

          {/* Upload Component */}
          <div className="mb-8">
            <DocumentUpload
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
              isUploading={isUploading}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="rounded-md bg-red-50 p-4 border border-red-200">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-red-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Upload Error</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Info Section */}
          <div className="mt-12 bg-blue-50 rounded-lg p-6 border border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">How it works</h3>
            <ol className="space-y-3 text-sm text-blue-800">
              <li className="flex items-start">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center font-semibold mr-3">
                  1
                </span>
                <span>
                  <strong>Upload Document:</strong> Drop your document (TXT, PDF, or DOCX)
                  above
                </span>
              </li>
              <li className="flex items-start">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center font-semibold mr-3">
                  2
                </span>
                <span>
                  <strong>AI Detection:</strong> Our AI will analyze and identify editable
                  fields
                </span>
              </li>
              <li className="flex items-start">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center font-semibold mr-3">
                  3
                </span>
                <span>
                  <strong>Confirm Fields:</strong> Review and confirm which fields you want to
                  make editable
                </span>
              </li>
              <li className="flex items-start">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center font-semibold mr-3">
                  4
                </span>
                <span>
                  <strong>Save Template:</strong> Your document is saved for future reuse with
                  natural language editing
                </span>
              </li>
            </ol>
          </div>
        </div>
      </main>
    </div>
  );
}
