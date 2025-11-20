import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DocumentUpload from '../components/DocumentUpload';

describe('DocumentUpload', () => {
  it('renders upload interface', () => {
    const onSuccess = vi.fn();
    const onError = vi.fn();

    render(
      <DocumentUpload onUploadSuccess={onSuccess} onUploadError={onError} />
    );

    expect(screen.getByText(/Drop your document here/i)).toBeInTheDocument();
    expect(screen.getByText(/or click to browse/i)).toBeInTheDocument();
  });

  it('shows supported formats', () => {
    const onSuccess = vi.fn();
    const onError = vi.fn();

    render(
      <DocumentUpload onUploadSuccess={onSuccess} onUploadError={onError} />
    );

    expect(screen.getByText(/Supported formats: TXT, PDF, DOCX/i)).toBeInTheDocument();
  });

  it('displays uploading state', () => {
    const onSuccess = vi.fn();
    const onError = vi.fn();

    render(
      <DocumentUpload
        onUploadSuccess={onSuccess}
        onUploadError={onError}
        isUploading={true}
      />
    );

    expect(screen.getByText(/Uploading.../i)).toBeInTheDocument();
  });

  it('validates file size', () => {
    const onSuccess = vi.fn();
    const onError = vi.fn();

    render(
      <DocumentUpload onUploadSuccess={onSuccess} onUploadError={onError} />
    );

    // Create a large file (> 10MB)
    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.txt', {
      type: 'text/plain',
    });

    const input = screen.getByLabelText(/file-input/i, { selector: 'input' });
    fireEvent.change(input, { target: { files: [largeFile] } });

    expect(onError).toHaveBeenCalledWith(
      expect.stringContaining('File size must be less than 10MB')
    );
  });

  it('validates file type', () => {
    const onSuccess = vi.fn();
    const onError = vi.fn();

    render(
      <DocumentUpload onUploadSuccess={onSuccess} onUploadError={onError} />
    );

    const invalidFile = new File(['content'], 'test.exe', {
      type: 'application/x-msdownload',
    });

    const input = screen.getByLabelText(/file-input/i, { selector: 'input' });
    fireEvent.change(input, { target: { files: [invalidFile] } });

    expect(onError).toHaveBeenCalledWith(
      expect.stringContaining('File type not supported')
    );
  });

  it('accepts valid file', () => {
    const onSuccess = vi.fn();
    const onError = vi.fn();

    render(
      <DocumentUpload onUploadSuccess={onSuccess} onUploadError={onError} />
    );

    const validFile = new File(['content'], 'test.txt', { type: 'text/plain' });

    const input = screen.getByLabelText(/file-input/i, { selector: 'input' });
    fireEvent.change(input, { target: { files: [validFile] } });

    expect(onSuccess).toHaveBeenCalledWith(validFile);
  });
});
