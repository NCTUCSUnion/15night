import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { getToken, handleTokenFromUrl, isAuthenticated } from './services/authService'

console.log('Application starting');

// Configure axios
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
axios.defaults.baseURL = apiBaseUrl;
console.log('Using API base URL:', apiBaseUrl || '(default)');

// Add token to API requests
axios.interceptors.request.use(config => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle unauthorized responses
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      console.log('Unauthorized request, redirecting to login');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

// Check if we have a token in the URL at application startup
if (window.location.search.includes('token=')) {
  console.log('Token found in URL at application startup');
  handleTokenFromUrl();
}

console.log('Current authentication state:', isAuthenticated() ? 'Authenticated' : 'Not authenticated');

// Create the Vue app
const app = createApp(App);

// Make axios available globally
app.config.globalProperties.$axios = axios;

// Add router
app.use(router);

// Mount the app
app.mount('#app');

console.log('Vue app mounted successfully');

