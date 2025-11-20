import { useMemo } from 'react';
import type { Template, Field, FieldPosition } from '../types';

// Support both Path 4 (confirm page) and Path 5 (edit page) use cases
interface DocumentPreviewPropsPath4 {
  documentText: string;
  fields: Field[];
  selectedFieldId?: string | null;
  template?: never;
  highlightFields?: never;
}

interface DocumentPreviewPropsPath5 {
  template: Template;
  highlightFields?: boolean;
  documentText?: never;
  fields?: never;
  selectedFieldId?: never;
}

type DocumentPreviewProps = DocumentPreviewPropsPath4 | DocumentPreviewPropsPath5;

interface TextSegment {
  text: string;
  fieldId?: string;
  fieldName?: string;
  isHighlighted?: boolean;
}

export function DocumentPreview(props: DocumentPreviewProps) {
  // Normalize props to work with both interfaces
  const documentText = props.template ? props.template.documentText : props.documentText!;
  const fields = props.template ? props.template.fields : props.fields!;
  const selectedFieldId = props.selectedFieldId;
  const highlightFields = 'highlightFields' in props ? props.highlightFields : true;

  // Generate color for field based on its ID (consistent colors for Path 4)
  const getFieldColor = (fieldId: string, isSelected: boolean) => {
    if (isSelected) {
      return 'bg-blue-300 border-blue-500';
    }

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

  // Build segments for rendering
  const segments = useMemo<TextSegment[]>(() => {
    if (!documentText || !highlightFields) {
      return [{ text: documentText || '' }];
    }

    const result: TextSegment[] = [];
    const positionMap = new Map<number, { field: Field; position: FieldPosition }>();

    // Build position map
    fields.forEach((field) => {
      if (field.confirmed) {
        field.positions.forEach((pos) => {
          for (let i = pos.start; i < pos.end; i++) {
            positionMap.set(i, { field, position: pos });
          }
        });
      }
    });

    let currentSegment: TextSegment = { text: '' };
    let currentFieldId: string | undefined = undefined;

    for (let i = 0; i < documentText.length; i++) {
      const char = documentText[i];
      const fieldInfo = positionMap.get(i);
      const thisFieldId = fieldInfo?.field.id;

      if (thisFieldId !== currentFieldId) {
        if (currentSegment.text) {
          result.push(currentSegment);
        }

        currentFieldId = thisFieldId;
        currentSegment = {
          text: char,
          fieldId: thisFieldId,
          fieldName: fieldInfo?.field.name,
          isHighlighted: !!fieldInfo && fieldInfo.field.id === selectedFieldId,
        };
      } else {
        currentSegment.text += char;
      }
    }

    if (currentSegment.text) {
      result.push(currentSegment);
    }

    return result;
  }, [documentText, fields, selectedFieldId, highlightFields]);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full flex flex-col">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Document Preview</h2>
        <p className="text-sm text-gray-600">
          {highlightFields ? 'Highlighted fields are detected variables' : 'View your document'}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4">
        <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed">
          {segments.map((segment, idx) => {
            if (segment.fieldId) {
              const colorClass = getFieldColor(segment.fieldId, !!segment.isHighlighted);
              return (
                <mark
                  key={idx}
                  className={`px-1 rounded border ${colorClass}`}
                  title={`${segment.fieldName}: ${segment.fieldId}`}
                >
                  {segment.text}
                </mark>
              );
            }
            return <span key={idx}>{segment.text}</span>;
          })}
        </pre>
      </div>

      {/* Field legend */}
      {highlightFields && fields.length > 0 && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Fields:</h3>
          <div className="flex flex-wrap gap-2">
            {fields.filter(f => f.confirmed).map((field) => (
              <div
                key={field.id}
                className="inline-flex items-center px-3 py-1 bg-yellow-100 border border-yellow-300 rounded-full text-xs"
              >
                <span className="font-medium text-gray-900">{field.name}:</span>
                <span className="ml-1 text-gray-700">{field.currentValue}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Export as default for backward compatibility with Path 4
export default DocumentPreview;
