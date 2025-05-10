<template>
  <div class="app-container">
    <router-view />
  </div>
</template>

<script>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { isAuthenticated, removeToken } from './services/authService.js';

export default {
  name: 'App',
  setup() {
    const router = useRouter();
    
    const checkAuth = computed(() => {
      return isAuthenticated();
    });
    
    const logout = () => {
      removeToken();
      router.push('/login');
    };
    
    return {
      isAuthenticated: checkAuth,
      logout
    };
  }
}
</script>

<style>
body {
  margin: 0;
  font-family: 'VT323', monospace;
  background-color: #f5f5f5;
}

* {
  box-sizing: border-box;
}

.app-container {
  position: relative;
  min-height: 100vh;
}

.nav-links {
  padding: 10px;
  background-color: #333;
  color: white;
  text-align: center;
}

.nav-links a {
  color: white;
  text-decoration: none;
  margin: 0 10px;
}

.nav-links a.router-link-active {
  font-weight: bold;
  color: #42b983;
}

.logout-nav-btn {
  background: none;
  color: white;
  border: none;
  padding: 0 10px;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
}

.logout-nav-btn:hover {
  text-decoration: underline;
}
</style>
