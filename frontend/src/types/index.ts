// Field types
export type FieldType = 'text' | 'date' | 'number' | 'email' | 'phone' | 'currency' | 'other';

// Position of a field occurrence in the document
export interface FieldPosition {
  start: number;
  end: number;
  text: string;
}

// Field detected or confirmed by the user
export interface Field {
  id: string;
  name: string;
  type: FieldType;
  positions: FieldPosition[];
  currentValue?: string;
  confirmed: boolean;
}

// Template metadata
export interface Template {
  id: string;
  name: string;
  createdAt: string;
  documentText: string;
  fields: Field[];
}

// API Request/Response types

export interface UploadDocumentRequest {
  file: File;
}

export interface UploadDocumentResponse {
  documentText: string;
  detectedFields: Field[];
  temporaryId: string;
}

export interface SaveTemplateRequest {
  name: string;
  documentText: string;
  fields: Field[];
}

export interface SaveTemplateResponse {
  templateId: string;
  message: string;
}

export interface GetTemplatesResponse {
  templates: Template[];
}

export interface GetTemplateResponse {
  template: Template;
}

export interface UpdateTemplateRequest {
  command: string;
}

export interface UpdateTemplateResponse {
  updatedDocument: string;
  fieldsChanged: string[];
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: any;
}

// UI State types

export interface UploadState {
  file: File | null;
  uploading: boolean;
  error: string | null;
}

export interface ConfirmationState {
  documentText: string;
  fields: Field[];
  selectedField: string | null;
  saving: boolean;
  error: string | null;
}
