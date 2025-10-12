import { API_URL } from '../config';

export const api = {
  // Fetch available templates
  async fetchTemplates() {
    const response = await fetch(`${API_URL}/templates`);
    if (!response.ok) {
      throw new Error('Erro ao carregar templates');
    }
    return response.json();
  },

  // Generate catalog
  async generateCatalog(payload) {
    const response = await fetch(`${API_URL}/catalog/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao gerar catálogo');
    }
    
    return response.json();
  },

  // Get job status
  async getJobStatus(jobId) {
    const response = await fetch(`${API_URL}/jobs/${jobId}`);
    if (!response.ok) {
      throw new Error('Erro ao verificar estado do catálogo');
    }
    return response.json();
  }
};