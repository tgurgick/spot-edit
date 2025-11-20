import { useState } from 'react';
import type { Field, FieldType } from '../types';

interface FieldConfirmationProps {
  fields: Field[];
  onFieldsChange: (fields: Field[]) => void;
  onSave: (fields: Field[]) => void;
  isSaving?: boolean;
  onFieldSelect?: (fieldId: string | null) => void;
}

const FIELD_TYPES: { value: FieldType; label: string }[] = [
  { value: 'text', label: 'Text' },
  { value: 'date', label: 'Date' },
  { value: 'number', label: 'Number' },
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'Phone' },
  { value: 'currency', label: 'Currency' },
  { value: 'other', label: 'Other' },
];

export default function FieldConfirmation({
  fields,
  onFieldsChange,
  onSave,
  isSaving = false,
  onFieldSelect,
}: FieldConfirmationProps) {
  const [editingFieldId, setEditingFieldId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState('');
  const [editingType, setEditingType] = useState<FieldType>('text');

  const confirmedFields = fields.filter((f) => f.confirmed);
  const allConfirmed = fields.length > 0 && confirmedFields.length === fields.length;

  const handleConfirmToggle = (fieldId: string) => {
    const updatedFields = fields.map((field) =>
      field.id === fieldId ? { ...field, confirmed: !field.confirmed } : field
    );
    onFieldsChange(updatedFields);
  };

  const handleRemoveField = (fieldId: string) => {
    const updatedFields = fields.filter((field) => field.id !== fieldId);
    onFieldsChange(updatedFields);
  };

  const handleStartEdit = (field: Field) => {
    setEditingFieldId(field.id);
    setEditingName(field.name);
    setEditingType(field.type);
  };

  const handleSaveEdit = (fieldId: string) => {
    const updatedFields = fields.map((field) =>
      field.id === fieldId
        ? { ...field, name: editingName, type: editingType }
        : field
    );
    onFieldsChange(updatedFields);
    setEditingFieldId(null);
  };

  const handleCancelEdit = () => {
    setEditingFieldId(null);
    setEditingName('');
    setEditingType('text');
  };

  const handleFieldClick = (fieldId: string) => {
    if (onFieldSelect) {
      onFieldSelect(fieldId);
    }
  };

  const handleSaveTemplate = () => {
    const fieldsToSave = fields.filter((f) => f.confirmed);
    onSave(fieldsToSave);
  };

  if (fields.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="text-gray-400 mb-2">
          <svg
            className="w-16 h-16 mx-auto"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <p className="text-gray-600 text-lg">No fields detected</p>
        <p className="text-gray-500 text-sm mt-2">
          The AI couldn't find any editable fields in the document.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-xl font-semibold text-gray-900">Confirm Fields</h2>
        <p className="text-sm text-gray-600 mt-1">
          Review and confirm the fields detected by AI. You can edit names, types, or remove
          fields.
        </p>
        <div className="mt-3 flex items-center space-x-2 text-sm">
          <span className="text-gray-600">
            {confirmedFields.length} of {fields.length} confirmed
          </span>
          {allConfirmed && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
              ✓ Ready to save
            </span>
          )}
        </div>
      </div>

      {/* Fields List */}
      <div className="divide-y divide-gray-200">
        {fields.map((field) => (
          <div
            key={field.id}
            className={`px-6 py-4 hover:bg-gray-50 transition-colors cursor-pointer ${
              field.confirmed ? 'bg-green-50' : 'bg-white'
            }`}
            onClick={() => handleFieldClick(field.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                {/* Checkbox */}
                <div className="flex items-center h-6">
                  <input
                    type="checkbox"
                    checked={field.confirmed}
                    onChange={(e) => {
                      e.stopPropagation();
                      handleConfirmToggle(field.id);
                    }}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </div>

                {/* Field Info */}
                <div className="flex-1 min-w-0">
                  {editingFieldId === field.id ? (
                    <div className="space-y-3" onClick={(e) => e.stopPropagation()}>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Field Name
                        </label>
                        <input
                          type="text"
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                          autoFocus
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Field Type
                        </label>
                        <select
                          value={editingType}
                          onChange={(e) => setEditingType(e.target.value as FieldType)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        >
                          {FIELD_TYPES.map((type) => (
                            <option key={type.value} value={type.value}>
                              {type.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleSaveEdit(field.id)}
                          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                        >
                          Save
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center space-x-2">
                        <h3 className="text-base font-medium text-gray-900">{field.name}</h3>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                          {field.type}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {field.positions.length} occurrence{field.positions.length !== 1 ? 's' : ''}{' '}
                        found
                      </p>
                      {field.currentValue && (
                        <p className="text-sm text-gray-500 mt-1">
                          Current value: <span className="font-mono">{field.currentValue}</span>
                        </p>
                      )}
                    </>
                  )}
                </div>
              </div>

              {/* Actions */}
              {editingFieldId !== field.id && (
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleStartEdit(field);
                    }}
                    className="p-1 text-gray-400 hover:text-blue-600"
                    title="Edit field"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                      />
                    </svg>
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveField(field.id);
                    }}
                    className="p-1 text-gray-400 hover:text-red-600"
                    title="Remove field"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Footer with Save Button */}
      <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
        <div className="flex justify-between items-center">
          <p className="text-sm text-gray-600">
            {confirmedFields.length === 0
              ? 'Select at least one field to save template'
              : `${confirmedFields.length} field${confirmedFields.length !== 1 ? 's' : ''} will be saved`}
          </p>
          <button
            onClick={handleSaveTemplate}
            disabled={confirmedFields.length === 0 || isSaving}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              confirmedFields.length === 0 || isSaving
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isSaving ? 'Saving...' : 'Save Template'}
          </button>
        </div>
      </div>
    </div>
  );
}
