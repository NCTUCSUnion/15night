import axios from 'axios';
import { getToken } from './authService';
import router from '../router';

/**
 * API service to handle authenticated backend requests
 */

// Create a custom instance of axios with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor to add auth token
api.interceptors.request.use(config => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle auth errors
api.interceptors.response.use(
  response => response,
  error => {
    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      console.log('API: Unauthorized request detected');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

// API methods
export const userAPI = {
  /**
   * Get user statistics
   * @returns {Promise} Promise with user data
   */
  getStats: async () => {
    return api.get('/api/user/stats');
  },
  
  /**
   * Get user backpack contents
   * @returns {Promise} Promise with backpack items data
   */
  getBackpack: async () => {
    return api.get('/api/user/backpack');
  },
  
  /**
   * Upgrade user's shovel
   * @returns {Promise} Promise with upgrade result
   */
  upgradeShovel: async () => {
    return api.post('/api/user/upgrade-shovel');
  }
};

export const blockAPI = {
  /**
   * Get available blocks
   * @returns {Promise} Promise with blocks data
   */
  getAvailable: async () => {
    return api.get('/api/blocks/available');
  },
  
  /**
   * Start mining a block
   * @param {number} blockId - The ID of the block to mine
   * @returns {Promise} Promise with mining start data
   */
  startMining: async (blockId) => {
    return api.post(`/api/blocks/${blockId}/start`);
  },
  
  /**
   * Complete mining operation
   * @param {number} blockId - The ID of the block being mined
   * @returns {Promise} Promise with mining result data
   */
  completeMining: async (blockId) => {
    return api.post(`/api/blocks/${blockId}/complete`);
  }
};

export const leaderboardAPI = {
  /**
   * Get leaderboard data
   * @param {number} limit - Maximum number of entries to return
   * @returns {Promise} Promise with leaderboard data
   */
  getLeaderboard: async (limit = 10) => {
    return api.get(`/api/leaderboard?limit=${limit}`);
  }
};

export default {
  user: userAPI,
  block: blockAPI,
  leaderboard: leaderboardAPI
};
