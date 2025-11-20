/**
 * Represents a field within a document template
 */
export interface Field {
  id: string;
  name: string;
  type: 'text' | 'date' | 'number' | string;
  positions: [number, number][]; // Array of [start, end] positions in the document
  current_value: string;
}

/**
 * Represents a complete document template
 */
export interface Template {
  id: string;
  name: string;
  created_at: string;
  updated_at?: string;
  document_text: string;
  fields: Field[];
}

/**
 * Request to update a template via natural language command
 */
export interface UpdateRequest {
  command: string;
  template_id: string;
}

/**
 * Response from update request with proposed changes
 */
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

/**
 * Message in the chat interface
 */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  proposed_changes?: UpdateResponse['proposed_changes'];
}

/**
 * Metadata for template cards in the library
 */
export interface TemplateMetadata {
  id: string;
  name: string;
  created_at: string;
  updated_at?: string;
  field_count: number;
  last_modified_by?: string;
}
