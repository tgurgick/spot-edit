import React, { useState, useCallback } from 'react';

interface DocumentUploadProps {
  onUploadSuccess: (file: File) => void;
  onUploadError: (error: string) => void;
  isUploading?: boolean;
}

const ALLOWED_FILE_TYPES = ['.txt', '.pdf', '.docx'];
const ALLOWED_MIME_TYPES = [
  'text/plain',
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export default function DocumentUpload({
  onUploadSuccess,
  onUploadError,
  isUploading = false,
}: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const validateFile = useCallback((file: File): string | null => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return 'File size must be less than 10MB';
    }

    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_FILE_TYPES.includes(fileExtension)) {
      return `File type not supported. Please upload ${ALLOWED_FILE_TYPES.join(', ')} files`;
    }

    // Check MIME type
    if (!ALLOWED_MIME_TYPES.includes(file.type) && file.type !== '') {
      return 'Invalid file format';
    }

    return null;
  }, []);

  const handleFile = useCallback(
    (file: File) => {
      const error = validateFile(file);
      if (error) {
        onUploadError(error);
        setSelectedFile(null);
        return;
      }

      setSelectedFile(file);
      onUploadSuccess(file);
    },
    [validateFile, onUploadSuccess, onUploadError]
  );

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      if (files.length === 0) {
        return;
      }

      if (files.length > 1) {
        onUploadError('Please upload only one file at a time');
        return;
      }

      handleFile(files[0]);
    },
    [handleFile, onUploadError]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        handleFile(files[0]);
      }
    },
    [handleFile]
  );

  const handleClick = () => {
    if (!isUploading) {
      document.getElementById('file-input')?.click();
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        onClick={handleClick}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400 bg-white'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input
          id="file-input"
          type="file"
          accept={ALLOWED_FILE_TYPES.join(',')}
          onChange={handleFileInput}
          className="hidden"
          disabled={isUploading}
        />

        <div className="flex flex-col items-center space-y-4">
          {/* Upload Icon */}
          <svg
            className={`w-16 h-16 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>

          {/* Upload Text */}
          <div className="space-y-2">
            {isUploading ? (
              <>
                <p className="text-lg font-medium text-gray-700">Uploading...</p>
                <div className="w-48 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full animate-pulse w-full"></div>
                </div>
              </>
            ) : selectedFile ? (
              <>
                <p className="text-lg font-medium text-green-600">File selected!</p>
                <p className="text-sm text-gray-600">{selectedFile.name}</p>
                <p className="text-xs text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </>
            ) : (
              <>
                <p className="text-lg font-medium text-gray-700">
                  {isDragging ? 'Drop your file here' : 'Drop your document here'}
                </p>
                <p className="text-sm text-gray-500">or click to browse</p>
              </>
            )}
          </div>

          {/* Supported formats */}
          {!isUploading && !selectedFile && (
            <div className="text-xs text-gray-500">
              Supported formats: TXT, PDF, DOCX (max 10MB)
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
