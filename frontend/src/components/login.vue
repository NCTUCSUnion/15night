<template>
  <div class="login-wrapper">
    <div class="login-container">
      <h1>Login to 15Night</h1>
      
      <button @click="loginWithOAuth" class="login-button" :disabled="isLoading">
        {{ isLoading ? 'Redirecting...' : 'Login with NYCU OAuth' }}
      </button>
      
      <div v-if="loginSuccess" class="success">Login successful! Redirecting...</div>
      <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
      
      <!-- Development only - direct token login -->
      <div v-if="showDevLogin" class="dev-login">
        <button @click="loginWithMock" class="mock-button">
          Mock Login (Dev Only)
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { setToken, handleTokenFromUrl } from '../services/authService';

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter();
    const isLoading = ref(false);
    const errorMessage = ref('');
    const loginSuccess = ref(false);
    const showDevLogin = ref(false);
    
    // OAuth login - redirects to the backend OAuth endpoint
    const loginWithOAuth = () => {
      isLoading.value = true;
      window.location.href = import.meta.env.VITE_API_BASE_URL + '/api/oauth/login';
      const redirectUri = encodeURIComponent(window.location.href);
      console.log(`Redirecting to OAuth login: ${import.meta.env.VITE_API_BASE_URL}/api/oauth/login?redirect_uri=${redirectUri}`);
    };
    
    // Mock login for development
    const loginWithMock = async () => {
      isLoading.value = true;
      try {
        // Use URLSearchParams to properly encode form data
        const params = new URLSearchParams();
        params.append('username', 'admin');
        params.append('password', 'password');        
        // Make API request for token
        const response = await axios.post('/api/token', params, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
        if (response.data && response.data.access_token) {
          setToken(response.data.access_token);
          loginSuccess.value = true;
          setTimeout(() => {
            router.push('/');
          }, 1000);
        } else {
          errorMessage.value = 'Invalid response from server';
        }
      } catch (error) {
        console.error('Login error:', error);
        errorMessage.value = error.response?.data?.detail || 'Login failed';
      } finally {
        isLoading.value = false;
      }
    };
    
    // Check for development environment to show mock login
    const checkDevEnvironment = async () => {
      if (import.meta.env.DEV) {
        showDevLogin.value = true;
      }
    };
    
    onMounted(() => {
      console.log('Login component mounted, checking for token in URL');
      // Check if we have a token in the URL (OAuth callback)
      if (handleTokenFromUrl()) {
        loginSuccess.value = true;
        
        setTimeout(() => {
          router.push('/');
        }, 1000);
      }
      checkDevEnvironment();
    });
    
    return {
      isLoading,
      errorMessage,
      loginSuccess,
      showDevLogin,
      loginWithOAuth,
      loginWithMock
    };
  }
};
</script>

<style>
.login-wrapper {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
}

.login-container {
  width: 90%;
  max-width: 400px;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
}

h1 {
  color: #333;
  margin-top: 0;
  margin-bottom: 30px;
  font-size: 28px;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

.login-button {
  display: block;
  width: 100%;
  margin: 20px 0;
  padding: 12px;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.login-button:hover {
  background-color: #3367d6;
}

.login-button:disabled {
  background-color: #a2b8e3;
  cursor: wait;
}

.error {
  color: #dc3545;
  margin-top: 20px;
  font-weight: bold;
}

.debug {
  background: #f8d7da;
  color: #721c24;
  padding: 5px;
  margin: 10px 0;
  border-radius: 4px;
}

.success {
  color: #28a745;
  margin-top: 20px;
  font-weight: bold;
}

.mock-button {
  display: block;
  width: 100%;
  margin: 10px 0;
  padding: 10px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.mock-button:hover {
  background-color: #218838;
}

.dev-login {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px dashed #ccc;
}
</style>
