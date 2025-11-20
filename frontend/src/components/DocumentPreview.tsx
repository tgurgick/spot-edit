import { useMemo } from 'react';
import type { Field, FieldPosition } from '../types';

interface DocumentPreviewProps {
  documentText: string;
  fields: Field[];
  selectedFieldId?: string | null;
}

interface TextSegment {
  text: string;
  fieldId?: string;
  fieldName?: string;
  isHighlighted?: boolean;
}

export default function DocumentPreview({
  documentText,
  fields,
  selectedFieldId,
}: DocumentPreviewProps) {
  // Generate color for field based on its ID (consistent colors)
  const getFieldColor = (fieldId: string, isSelected: boolean) => {
    if (isSelected) {
      return 'bg-blue-300 border-blue-500';
    }

    // Generate consistent color based on field ID
    const hash = fieldId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const colors = [
      'bg-yellow-200 border-yellow-400',
      'bg-green-200 border-green-400',
      'bg-purple-200 border-purple-400',
      'bg-pink-200 border-pink-400',
      'bg-indigo-200 border-indigo-400',
      'bg-orange-200 border-orange-400',
    ];
    return colors[hash % colors.length];
  };

  // Parse document text and create segments with field highlighting
  const textSegments = useMemo((): TextSegment[] => {
    if (!documentText || fields.length === 0) {
      return [{ text: documentText }];
    }

    // Get all field positions, sorted by start position
    const allPositions: Array<FieldPosition & { fieldId: string; fieldName: string }> = [];

    fields.forEach((field) => {
      field.positions.forEach((pos) => {
        allPositions.push({
          ...pos,
          fieldId: field.id,
          fieldName: field.name,
        });
      });
    });

    // Sort by start position
    allPositions.sort((a, b) => a.start - b.start);

    // Build segments
    const segments: TextSegment[] = [];
    let lastIndex = 0;

    allPositions.forEach((pos) => {
      // Add text before this field (if any)
      if (pos.start > lastIndex) {
        segments.push({
          text: documentText.slice(lastIndex, pos.start),
        });
      }

      // Add field segment
      segments.push({
        text: documentText.slice(pos.start, pos.end),
        fieldId: pos.fieldId,
        fieldName: pos.fieldName,
        isHighlighted: selectedFieldId === pos.fieldId,
      });

      lastIndex = pos.end;
    });

    // Add remaining text (if any)
    if (lastIndex < documentText.length) {
      segments.push({
        text: documentText.slice(lastIndex),
      });
    }

    return segments;
  }, [documentText, fields, selectedFieldId]);

  if (!documentText) {
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
        <p className="text-gray-600">No document loaded</p>
      </div>
    );
  }

  // Get field legend
  const fieldLegend = fields.map((field) => ({
    id: field.id,
    name: field.name,
    color: getFieldColor(field.id, selectedFieldId === field.id),
    count: field.positions.length,
  }));

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-xl font-semibold text-gray-900">Document Preview</h2>
        <p className="text-sm text-gray-600 mt-1">
          Fields are highlighted in the document below
        </p>
      </div>

      {/* Field Legend */}
      {fields.length > 0 && (
        <div className="border-b border-gray-200 px-6 py-3 bg-gray-50">
          <div className="flex flex-wrap gap-2">
            {fieldLegend.map((field) => (
              <div
                key={field.id}
                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${field.color}`}
              >
                <span className="font-semibold">{field.name}</span>
                <span className="ml-1.5 text-gray-600">({field.count})</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Document Content */}
      <div className="px-6 py-6">
        <div className="prose max-w-none">
          <div className="font-mono text-sm leading-relaxed whitespace-pre-wrap break-words">
            {textSegments.map((segment, index) => {
              if (segment.fieldId) {
                const color = getFieldColor(segment.fieldId, segment.isHighlighted || false);
                return (
                  <span
                    key={index}
                    className={`${color} border px-1 py-0.5 rounded transition-all duration-200 ${
                      segment.isHighlighted ? 'ring-2 ring-blue-500 ring-opacity-50' : ''
                    }`}
                    title={`Field: ${segment.fieldName}`}
                  >
                    {segment.text}
                  </span>
                );
              }
              return <span key={index}>{segment.text}</span>;
            })}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 px-6 py-3 bg-gray-50">
        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>{documentText.length} characters</span>
          <span>
            {fields.length} field{fields.length !== 1 ? 's' : ''} detected
          </span>
        </div>
      </div>
    </div>
  );
}
