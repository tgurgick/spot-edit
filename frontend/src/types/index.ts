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
  updatedAt?: string;
  documentText: string;
  fields: Field[];
}

// Template metadata for list views
export interface TemplateMetadata {
  id: string;
  name: string;
  createdAt: string;
  updatedAt?: string;
  fieldCount: number;
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

// Extended update response with proposed changes (for Path 5)
export interface UpdateResponse {
  success: boolean;
  updated_template?: Template;
  proposed_changes?: {
    field_id: string;
    field_name: string;
    old_value: string;
    new_value: string;
  }[];
  error?: string;
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

// Chat interface types (for Path 5)
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  proposed_changes?: UpdateResponse['proposed_changes'];
}
