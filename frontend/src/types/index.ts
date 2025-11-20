/**
 * TypeScript type definitions for Spot Edit
 */

export interface Field {
  id: string
  name: string
  type: 'text' | 'date' | 'number' | 'email' | 'phone'
  positions: [number, number][]
  current_value: string
}

export interface Template {
  id: string
  name: string
  created_at: string
  document_text: string
  fields: Field[]
}

export interface UploadResponse {
  file_id: string
  detected_fields: Field[]
  document_text: string
}

export interface UpdateRequest {
  command: string
}

export interface UpdateResponse {
  updated_document: string
  changes: {
    field_id: string
    old_value: string
    new_value: string
  }[]
}
