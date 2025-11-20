import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DocumentPreview } from '../components/DocumentPreview';
import type { Field } from '../types';

const mockDocumentText = 'This is a test document with Acme Corp on 2024-01-01.';

const mockFields: Field[] = [
  {
    id: '1',
    name: 'Company Name',
    type: 'text',
    positions: [{ start: 30, end: 39, text: 'Acme Corp' }],
    currentValue: 'Acme Corp',
    confirmed: true,
  },
  {
    id: '2',
    name: 'Date',
    type: 'date',
    positions: [{ start: 43, end: 53, text: '2024-01-01' }],
    currentValue: '2024-01-01',
    confirmed: true,
  },
];

describe('DocumentPreview', () => {
  it('renders document text', () => {
    render(
      <DocumentPreview
        documentText={mockDocumentText}
        fields={mockFields}
        selectedFieldId={null}
      />
    );

    expect(screen.getByText(/This is a test document/i)).toBeInTheDocument();
  });

  it('shows empty state when no document', () => {
    render(<DocumentPreview documentText="" fields={[]} selectedFieldId={null} />);

    expect(screen.getByText('No document loaded')).toBeInTheDocument();
  });

  it('displays field legend', () => {
    render(
      <DocumentPreview
        documentText={mockDocumentText}
        fields={mockFields}
        selectedFieldId={null}
      />
    );

    expect(screen.getByText('Company Name')).toBeInTheDocument();
    expect(screen.getByText('Date')).toBeInTheDocument();
  });

  it('shows field counts in legend', () => {
    render(
      <DocumentPreview
        documentText={mockDocumentText}
        fields={mockFields}
        selectedFieldId={null}
      />
    );

    // Each field has 1 occurrence
    const legendItems = screen.getAllByText(/\(1\)/);
    expect(legendItems).toHaveLength(2);
  });

  it('displays document statistics', () => {
    render(
      <DocumentPreview
        documentText={mockDocumentText}
        fields={mockFields}
        selectedFieldId={null}
      />
    );

    expect(screen.getByText(/characters/i)).toBeInTheDocument();
    expect(screen.getByText(/2 fields detected/i)).toBeInTheDocument();
  });

  it('highlights fields in document', () => {
    const { container } = render(
      <DocumentPreview
        documentText={mockDocumentText}
        fields={mockFields}
        selectedFieldId={null}
      />
    );

    // Check that highlighted spans exist
    const highlightedElements = container.querySelectorAll('span[title^="Field:"]');
    expect(highlightedElements.length).toBeGreaterThan(0);
  });

  it('handles multiple field occurrences', () => {
    const multiOccurrenceFields: Field[] = [
      {
        id: '1',
        name: 'Company',
        type: 'text',
        positions: [
          { start: 0, end: 4, text: 'Acme' },
          { start: 10, end: 14, text: 'Acme' },
        ],
        currentValue: 'Acme',
        confirmed: true,
      },
    ];

    render(
      <DocumentPreview
        documentText="Acme and Acme again"
        fields={multiOccurrenceFields}
        selectedFieldId={null}
      />
    );

    expect(screen.getByText(/\(2\)/)).toBeInTheDocument();
  });
});
