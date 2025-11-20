import { useMemo } from 'react';
import type { Template, Field } from '../types';

interface DocumentPreviewProps {
  template: Template;
  highlightFields?: boolean;
}

export function DocumentPreview({ template, highlightFields = true }: DocumentPreviewProps) {
  // Create a map of positions to fields for efficient lookup
  const positionMap = useMemo(() => {
    const map = new Map<number, Field>();
    template.fields.forEach((field) => {
      field.positions.forEach(([start, end]) => {
        for (let i = start; i < end; i++) {
          map.set(i, field);
        }
      });
    });
    return map;
  }, [template.fields]);

  // Generate highlighted document text
  const renderDocument = () => {
    if (!highlightFields) {
      return <pre className="whitespace-pre-wrap font-mono text-sm">{template.document_text}</pre>;
    }

    const segments: React.ReactElement[] = [];
    let currentField: Field | null = null;
    let currentSegment = '';
    let currentStart = 0;

    for (let i = 0; i < template.document_text.length; i++) {
      const char = template.document_text[i];
      const field = positionMap.get(i);

      if (field !== currentField) {
        // Push the current segment
        if (currentSegment) {
          segments.push(
            currentField ? (
              <mark
                key={`${currentStart}-${i}`}
                className="bg-yellow-200 px-1 rounded"
                title={`${currentField.name}: ${currentField.current_value}`}
              >
                {currentSegment}
              </mark>
            ) : (
              <span key={`${currentStart}-${i}`}>{currentSegment}</span>
            )
          );
        }

        // Start new segment
        currentField = field || null;
        currentSegment = char;
        currentStart = i;
      } else {
        currentSegment += char;
      }
    }

    // Push the last segment
    if (currentSegment) {
      segments.push(
        currentField ? (
          <mark
            key={`${currentStart}-${template.document_text.length}`}
            className="bg-yellow-200 px-1 rounded"
            title={`${currentField.name}: ${currentField.current_value}`}
          >
            {currentSegment}
          </mark>
        ) : (
          <span key={`${currentStart}-${template.document_text.length}`}>{currentSegment}</span>
        )
      );
    }

    return <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed">{segments}</pre>;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full flex flex-col">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Document Preview</h2>
        <p className="text-sm text-gray-600">
          {highlightFields ? 'Highlighted fields are detected variables' : 'View your document'}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4">
        {renderDocument()}
      </div>

      {/* Field legend */}
      {highlightFields && template.fields.length > 0 && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Fields:</h3>
          <div className="flex flex-wrap gap-2">
            {template.fields.map((field) => (
              <div
                key={field.id}
                className="inline-flex items-center px-3 py-1 bg-yellow-100 border border-yellow-300 rounded-full text-xs"
              >
                <span className="font-medium text-gray-900">{field.name}:</span>
                <span className="ml-1 text-gray-700">{field.current_value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
