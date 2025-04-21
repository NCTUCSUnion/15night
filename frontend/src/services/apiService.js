import axios from 'axios';

// Base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Makes API requests with optional authentication
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Request options
 * @param {boolean} options.auth - Whether authentication is required (default: true)
 * @returns {Promise} - API response
 */
export const apiRequest = async (endpoint, options = {}) => {
  const { auth = true, ...axiosOptions } = options;
  
  // Create request config
  const config = {
    ...axiosOptions,
    headers: {
      'Content-Type': 'application/json',
      ...axiosOptions.headers
    }
  };
  
  // Add auth token if required and available
  if (auth) {
    const token = localStorage.getItem('oauth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  
  // Make the request
  try {
    const response = await axios(endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`, config);
    return response.data;
  } catch (error) {
    if (error.response && error.response.status === 401 && auth) {
      // Handle unauthorized error (expired token, etc)
      // You could redirect to login or trigger token refresh here
    }
    throw error;
  }
};

// API method shortcuts
export const api = {
  get: (endpoint, options = {}) => apiRequest(endpoint, { 
    method: 'GET', 
    ...options 
  }),
  
  post: (endpoint, data, options = {}) => apiRequest(endpoint, { 
    method: 'POST', 
    data, 
    ...options 
  }),
  
  put: (endpoint, data, options = {}) => apiRequest(endpoint, { 
    method: 'PUT', 
    data, 
    ...options 
  }),
  
  delete: (endpoint, options = {}) => apiRequest(endpoint, { 
    method: 'DELETE', 
    ...options 
  })
};

export default api;