// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Service for DocuMind Backend
class DocuMindAPI {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  // Helper method for making requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Get system statistics
  async getStats() {
    return this.request('/stats');
  }

  // Upload documents
  async uploadDocuments(files) {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    return this.request('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  }

  // Query documents
  async queryDocuments(query, options = {}) {
    const {
      top_k = 5,
      rerank = true,
      file_filter = null,
    } = options;

    const params = new URLSearchParams({
      query,
      top_k: top_k.toString(),
      rerank: rerank.toString(),
    });

    if (file_filter) {
      params.append('file_filter', file_filter);
    }

    return this.request(`/query?${params.toString()}`, {
      method: 'POST',
    });
  }

  // Delete document
  async deleteDocument(filename) {
    return this.request(`/documents/${encodeURIComponent(filename)}`, {
      method: 'DELETE',
    });
  }

  // List uploaded files (get stats and extract file names)
  async getUploadedFiles() {
    const stats = await this.getStats();
    // Extract file names from stats if available
    return stats.files || [];
  }
}

// Export singleton instance
export const api = new DocuMindAPI();

// Export class for testing
export default DocuMindAPI;
