import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import FieldConfirmation from '../components/FieldConfirmation';
import DocumentPreview from '../components/DocumentPreview';
import { saveTemplate } from '../api/client';
import type { Field } from '../types';

interface LocationState {
  documentText: string;
  detectedFields: Field[];
  fileName: string;
}

export default function Confirm() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [documentText, setDocumentText] = useState('');
  const [fields, setFields] = useState<Field[]>([]);
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  const [templateName, setTemplateName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showNameDialog, setShowNameDialog] = useState(false);

  useEffect(() => {
    // Check if we have the required data from navigation state
    if (!state || !state.documentText || !state.detectedFields) {
      // Redirect back to upload if no data
      navigate('/');
      return;
    }

    setDocumentText(state.documentText);
    setFields(state.detectedFields);

    // Set default template name from file name
    if (state.fileName) {
      const nameWithoutExt = state.fileName.replace(/\.[^/.]+$/, '');
      setTemplateName(nameWithoutExt);
    }
  }, [state, navigate]);

  const handleFieldsChange = (updatedFields: Field[]) => {
    setFields(updatedFields);
  };

  const handleFieldSelect = (fieldId: string | null) => {
    setSelectedFieldId(fieldId);
  };

  const handleSaveInitiate = () => {
    setShowNameDialog(true);
  };

  const handleSaveConfirm = async (confirmedFields: Field[]) => {
    if (!templateName.trim()) {
      setError('Please enter a template name');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const response = await saveTemplate({
        name: templateName.trim(),
        documentText,
        fields: confirmedFields,
      });

      // Navigate to templates list with success message
      navigate('/templates', {
        state: {
          successMessage: `Template "${templateName}" saved successfully!`,
          newTemplateId: response.templateId,
        },
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save template';
      setError(errorMessage);
      setIsSaving(false);
    }
  };

  const handleCancelSave = () => {
    setShowNameDialog(false);
  };

  const handleBack = () => {
    navigate('/');
  };

  if (!state) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleBack}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
                title="Back to upload"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Confirm Fields</h1>
                <p className="text-sm text-gray-600 mt-1">
                  Review detected fields and save your template
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4 border border-red-200">
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
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Field Confirmation */}
          <div>
            <FieldConfirmation
              fields={fields}
              onFieldsChange={handleFieldsChange}
              onSave={handleSaveInitiate}
              isSaving={isSaving}
              onFieldSelect={handleFieldSelect}
            />
          </div>

          {/* Right Column - Document Preview */}
          <div>
            <DocumentPreview
              documentText={documentText}
              fields={fields.filter((f) => f.confirmed)}
              selectedFieldId={selectedFieldId}
            />
          </div>
        </div>
      </main>

      {/* Template Name Dialog */}
      {showNameDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Save Template</h3>
            <div className="mb-4">
              <label htmlFor="template-name" className="block text-sm font-medium text-gray-700 mb-2">
                Template Name
              </label>
              <input
                id="template-name"
                type="text"
                value={templateName}
                onChange={(e) => setTemplateName(e.target.value)}
                placeholder="Enter a name for your template"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSaveConfirm(fields.filter((f) => f.confirmed));
                  }
                }}
              />
            </div>
            <div className="flex space-x-3 justify-end">
              <button
                onClick={handleCancelSave}
                disabled={isSaving}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleSaveConfirm(fields.filter((f) => f.confirmed))}
                disabled={!templateName.trim() || isSaving}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSaving ? 'Saving...' : 'Save Template'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
