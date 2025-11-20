/**
 * API client for Spot Edit backend
 */

import axios from 'axios'
import type { Template, UploadResponse, UpdateRequest, UpdateResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Upload and analyze document
export const uploadDocument = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post<UploadResponse>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

// Get all templates
export const getTemplates = async (): Promise<Template[]> => {
  const response = await apiClient.get<Template[]>('/api/templates')
  return response.data
}

// Get specific template
export const getTemplate = async (id: string): Promise<Template> => {
  const response = await apiClient.get<Template>(`/api/templates/${id}`)
  return response.data
}

// Save new template
export const saveTemplate = async (
  document_text: string,
  fields: any[],
  metadata: { name: string }
): Promise<{ template_id: string }> => {
  const response = await apiClient.post('/api/templates', {
    document_text,
    fields,
    ...metadata,
  })
  return response.data
}

// Update template
export const updateTemplate = async (
  id: string,
  updates: Partial<Template>
): Promise<Template> => {
  const response = await apiClient.put<Template>(`/api/templates/${id}`, updates)
  return response.data
}

// Delete template
export const deleteTemplate = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/templates/${id}`)
}

// Apply natural language update to template
export const applyUpdate = async (
  id: string,
  command: string
): Promise<UpdateResponse> => {
  const response = await apiClient.post<UpdateResponse>(
    `/api/templates/${id}/update`,
    { command } as UpdateRequest
  )
  return response.data
}

// Download updated document
export const downloadDocument = async (id: string): Promise<Blob> => {
  const response = await apiClient.get(`/api/templates/${id}/download`, {
    responseType: 'blob',
  })
  return response.data
}
