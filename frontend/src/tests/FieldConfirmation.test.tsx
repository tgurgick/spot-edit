import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import FieldConfirmation from '../components/FieldConfirmation';
import type { Field } from '../types';

const mockFields: Field[] = [
  {
    id: '1',
    name: 'Company Name',
    type: 'text',
    positions: [{ start: 0, end: 10, text: 'Acme Corp' }],
    currentValue: 'Acme Corp',
    confirmed: false,
  },
  {
    id: '2',
    name: 'Date',
    type: 'date',
    positions: [{ start: 20, end: 30, text: '2024-01-01' }],
    currentValue: '2024-01-01',
    confirmed: true,
  },
];

describe('FieldConfirmation', () => {
  it('renders field list', () => {
    const onFieldsChange = vi.fn();
    const onSave = vi.fn();

    render(
      <FieldConfirmation
        fields={mockFields}
        onFieldsChange={onFieldsChange}
        onSave={onSave}
      />
    );

    expect(screen.getByText('Company Name')).toBeInTheDocument();
    expect(screen.getByText('Date')).toBeInTheDocument();
  });

  it('shows field counts', () => {
    const onFieldsChange = vi.fn();
    const onSave = vi.fn();

    render(
      <FieldConfirmation
        fields={mockFields}
        onFieldsChange={onFieldsChange}
        onSave={onSave}
      />
    );

    expect(screen.getByText(/1 of 2 confirmed/i)).toBeInTheDocument();
  });

  it('allows toggling field confirmation', () => {
    const onFieldsChange = vi.fn();
    const onSave = vi.fn();

    render(
      <FieldConfirmation
        fields={mockFields}
        onFieldsChange={onFieldsChange}
        onSave={onSave}
      />
    );

    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[0]);

    expect(onFieldsChange).toHaveBeenCalledWith(
      expect.arrayContaining([
        expect.objectContaining({ id: '1', confirmed: true }),
      ])
    );
  });

  it('disables save button when no fields confirmed', () => {
    const onFieldsChange = vi.fn();
    const onSave = vi.fn();

    const unconfirmedFields = mockFields.map((f) => ({ ...f, confirmed: false }));

    render(
      <FieldConfirmation
        fields={unconfirmedFields}
        onFieldsChange={onFieldsChange}
        onSave={onSave}
      />
    );

    const saveButton = screen.getByText('Save Template');
    expect(saveButton).toBeDisabled();
  });

  it('enables save button when fields are confirmed', () => {
    const onFieldsChange = vi.fn();
    const onSave = vi.fn();

    render(
      <FieldConfirmation
        fields={mockFields}
        onFieldsChange={onFieldsChange}
        onSave={onSave}
      />
    );

    const saveButton = screen.getByText('Save Template');
    expect(saveButton).not.toBeDisabled();
  });

  it('shows empty state when no fields', () => {
    const onFieldsChange = vi.fn();
    const onSave = vi.fn();

    render(
      <FieldConfirmation fields={[]} onFieldsChange={onFieldsChange} onSave={onSave} />
    );

    expect(screen.getByText('No fields detected')).toBeInTheDocument();
  });

  it('allows removing a field', () => {
    const onFieldsChange = vi.fn();
    const onSave = vi.fn();

    render(
      <FieldConfirmation
        fields={mockFields}
        onFieldsChange={onFieldsChange}
        onSave={onSave}
      />
    );

    const removeButtons = screen.getAllByTitle('Remove field');
    fireEvent.click(removeButtons[0]);

    expect(onFieldsChange).toHaveBeenCalledWith(
      expect.arrayContaining([expect.objectContaining({ id: '2' })])
    );
    expect(onFieldsChange).toHaveBeenCalledWith(
      expect.not.arrayContaining([expect.objectContaining({ id: '1' })])
    );
  });
});
