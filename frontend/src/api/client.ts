import axios, { type AxiosInstance } from 'axios';
import type { Template, TemplateMetadata, UpdateRequest, UpdateResponse } from '../types';

/**
 * API Client for Spot Edit backend
 */
class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = import.meta.env.VITE_API_URL || 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Get all templates (metadata only)
   */
  async getTemplates(): Promise<TemplateMetadata[]> {
    const response = await this.client.get<TemplateMetadata[]>('/api/templates');
    return response.data;
  }

  /**
   * Get a specific template by ID (full template with fields and content)
   */
  async getTemplate(id: string): Promise<Template> {
    const response = await this.client.get<Template>(`/api/templates/${id}`);
    return response.data;
  }

  /**
   * Delete a template by ID
   */
  async deleteTemplate(id: string): Promise<{ success: boolean }> {
    const response = await this.client.delete<{ success: boolean }>(`/api/templates/${id}`);
    return response.data;
  }

  /**
   * Update a template using natural language command
   */
  async updateTemplate(id: string, command: string): Promise<UpdateResponse> {
    const request: UpdateRequest = {
      template_id: id,
      command,
    };
    const response = await this.client.post<UpdateResponse>(
      `/api/templates/${id}/update`,
      request
    );
    return response.data;
  }

  /**
   * Apply proposed changes to a template
   */
  async applyChanges(id: string, changes: UpdateResponse['proposed_changes']): Promise<Template> {
    const response = await this.client.post<Template>(
      `/api/templates/${id}/apply`,
      { changes }
    );
    return response.data;
  }

  /**
   * Download a template as a file
   */
  async downloadTemplate(id: string): Promise<Blob> {
    const response = await this.client.get(`/api/templates/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Upload a new document for field detection
   * Note: This is part of Path 4 but included here for completeness
   */
  async uploadDocument(file: File): Promise<{ fields: any[]; document_text: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Save a new template
   * Note: This is part of Path 4 but included here for completeness
   */
  async saveTemplate(template: Omit<Template, 'id' | 'created_at'>): Promise<Template> {
    const response = await this.client.post<Template>('/api/templates', template);
    return response.data;
  }
}

// Export a singleton instance
export const apiClient = new ApiClient();

// Export the class for testing purposes
export { ApiClient };
