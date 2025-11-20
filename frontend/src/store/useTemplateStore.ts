import { create } from 'zustand';
import type { Template, ChatMessage, GetTemplatesResponse, GetTemplateResponse } from '../types';
import * as api from '../api/client';

interface TemplateStore {
  // Template list state
  templates: Template[];
  isLoadingTemplates: boolean;
  templatesError: string | null;

  // Current template state
  currentTemplate: Template | null;
  isLoadingTemplate: boolean;
  templateError: string | null;

  // Chat state
  chatMessages: ChatMessage[];
  isSendingMessage: boolean;
  chatError: string | null;

  // Actions for template list
  fetchTemplates: () => Promise<void>;
  deleteTemplate: (id: string) => Promise<void>;
  clearTemplates: () => void;

  // Actions for current template
  loadTemplate: (id: string) => Promise<void>;
  clearCurrentTemplate: () => void;
  updateCurrentTemplate: (template: Template) => void;

  // Actions for chat
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  sendCommand: (command: string) => Promise<void>;
  clearChat: () => void;
  applyChanges: (changes: ChatMessage['proposed_changes']) => Promise<void>;
}

export const useTemplateStore = create<TemplateStore>((set, get) => ({
  // Initial state
  templates: [],
  isLoadingTemplates: false,
  templatesError: null,
  currentTemplate: null,
  isLoadingTemplate: false,
  templateError: null,
  chatMessages: [],
  isSendingMessage: false,
  chatError: null,

  // Template list actions
  fetchTemplates: async () => {
    set({ isLoadingTemplates: true, templatesError: null });
    try {
      const response: GetTemplatesResponse = await api.getTemplates();
      set({ templates: response.templates, isLoadingTemplates: false });
    } catch (error) {
      set({
        templatesError: error instanceof Error ? error.message : 'Failed to fetch templates',
        isLoadingTemplates: false,
      });
    }
  },

  deleteTemplate: async (id: string) => {
    try {
      await api.deleteTemplate(id);
      set((state) => ({
        templates: state.templates.filter((t) => t.id !== id),
      }));

      // If the deleted template is the current one, clear it
      if (get().currentTemplate?.id === id) {
        get().clearCurrentTemplate();
      }
    } catch (error) {
      set({
        templatesError: error instanceof Error ? error.message : 'Failed to delete template',
      });
    }
  },

  clearTemplates: () => {
    set({ templates: [], templatesError: null });
  },

  // Current template actions
  loadTemplate: async (id: string) => {
    set({ isLoadingTemplate: true, templateError: null });
    try {
      const response: GetTemplateResponse = await api.getTemplate(id);
      set({ currentTemplate: response.template, isLoadingTemplate: false });
    } catch (error) {
      set({
        templateError: error instanceof Error ? error.message : 'Failed to load template',
        isLoadingTemplate: false,
      });
    }
  },

  clearCurrentTemplate: () => {
    set({ currentTemplate: null, templateError: null, chatMessages: [] });
  },

  updateCurrentTemplate: (template: Template) => {
    set({ currentTemplate: template });
  },

  // Chat actions
  addMessage: (message) => {
    const newMessage: ChatMessage = {
      ...message,
      id: `msg-${Date.now()}-${Math.random()}`,
      timestamp: new Date(),
    };
    set((state) => ({
      chatMessages: [...state.chatMessages, newMessage],
    }));
  },

  sendCommand: async (command: string) => {
    const { currentTemplate, addMessage } = get();

    if (!currentTemplate) {
      set({ chatError: 'No template loaded' });
      return;
    }

    // Add user message
    addMessage({ role: 'user', content: command });

    set({ isSendingMessage: true, chatError: null });
    try {
      const response = await api.updateTemplate(currentTemplate.id, { command });

      // Note: The actual API returns UpdateTemplateResponse, not UpdateResponse
      // We're showing the updates happened
      addMessage({
        role: 'assistant',
        content: `Updated fields: ${response.fieldsChanged.join(', ')}`,
      });

      // Reload the template to get the updated version
      await get().loadTemplate(currentTemplate.id);

      set({ isSendingMessage: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send command';
      set({ chatError: errorMessage, isSendingMessage: false });

      addMessage({
        role: 'assistant',
        content: `Error: ${errorMessage}`,
      });
    }
  },

  applyChanges: async (changes) => {
    const { currentTemplate, addMessage } = get();

    if (!currentTemplate || !changes) {
      return;
    }

    set({ isSendingMessage: true, chatError: null });
    try {
      const response: GetTemplateResponse = await api.applyChanges(currentTemplate.id, changes);
      set({ currentTemplate: response.template, isSendingMessage: false });

      addMessage({
        role: 'assistant',
        content: 'Changes applied successfully!',
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to apply changes';
      set({ chatError: errorMessage, isSendingMessage: false });

      addMessage({
        role: 'assistant',
        content: `Error applying changes: ${errorMessage}`,
      });
    }
  },

  clearChat: () => {
    set({ chatMessages: [], chatError: null });
  },
}));
