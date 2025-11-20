import axios, { type AxiosError } from 'axios';
import type {
  UploadDocumentResponse,
  SaveTemplateRequest,
  SaveTemplateResponse,
  GetTemplatesResponse,
  GetTemplateResponse,
  UpdateTemplateRequest,
  UpdateTemplateResponse,
  ErrorResponse,
  UpdateResponse,
} from '../types';

// Get base URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Error handler
function handleError(error: AxiosError<ErrorResponse>): never {
  if (error.response) {
    // Server responded with error status
    const errorData = error.response.data;
    throw new Error(errorData?.message || 'An error occurred');
  } else if (error.request) {
    // Request made but no response
    throw new Error('No response from server. Please check your connection.');
  } else {
    // Error setting up request
    throw new Error(error.message || 'Failed to make request');
  }
}

/**
 * Upload a document and get AI-detected fields
 */
export async function uploadDocument(file: File): Promise<UploadDocumentResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<UploadDocumentResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    return handleError(error as AxiosError<ErrorResponse>);
  }
}

/**
 * Save a template with confirmed fields
 */
export async function saveTemplate(
  request: SaveTemplateRequest
): Promise<SaveTemplateResponse> {
  try {
    const response = await apiClient.post<SaveTemplateResponse>('/templates', request);
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError<ErrorResponse>);
  }
}

/**
 * Get all templates
 */
export async function getTemplates(): Promise<GetTemplatesResponse> {
  try {
    const response = await apiClient.get<GetTemplatesResponse>('/templates');
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError<ErrorResponse>);
  }
}

/**
 * Get a specific template by ID
 */
export async function getTemplate(id: string): Promise<GetTemplateResponse> {
  try {
    const response = await apiClient.get<GetTemplateResponse>(`/templates/${id}`);
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError<ErrorResponse>);
  }
}

/**
 * Delete a template
 */
export async function deleteTemplate(id: string): Promise<void> {
  try {
    await apiClient.delete(`/templates/${id}`);
  } catch (error) {
    return handleError(error as AxiosError<ErrorResponse>);
  }
}

/**
 * Update a template with natural language command
 */
export async function updateTemplate(
  id: string,
  request: UpdateTemplateRequest
): Promise<UpdateTemplateResponse> {
  try {
    const response = await apiClient.post<UpdateTemplateResponse>(
      `/templates/${id}/update`,
      request
    );
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError<ErrorResponse>);
  }
}

/**
 * Apply proposed changes to a template
 */
export async function applyChanges(
  id: string,
  changes: UpdateResponse['proposed_changes']
): Promise<GetTemplateResponse> {
  try {
    const response = await apiClient.post<GetTemplateResponse>(
      `/templates/${id}/apply`,
      { changes }
    );
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError<ErrorResponse>);
  }
}

/**
 * Download updated document
 */
export async function downloadTemplate(id: string): Promise<Blob> {
  try {
    const response = await apiClient.get(`/templates/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError<ErrorResponse>);
  }
}

export default {
  uploadDocument,
  saveTemplate,
  getTemplates,
  getTemplate,
  deleteTemplate,
  updateTemplate,
  applyChanges,
  downloadTemplate,
};
