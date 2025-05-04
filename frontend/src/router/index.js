import { createRouter, createWebHistory } from 'vue-router';
import { isAuthenticated, handleTokenFromUrl } from '../services/authService';
import LoginPage from '../components/Login.vue';
import Home from '../components/Home.vue';

// Define routes
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    // Check for token in query params
    beforeEnter: (to, from, next) => {
      // If we have a token in the URL, we'll handle it in the component
      if (to.query.token) {
        // Process and save the token immediately
        handleTokenFromUrl(to.query.token);
        // Redirect to home if token is valid
        if (isAuthenticated()) {
          next('/');
          return;
        }
      }
      // If already authenticated without needing URL token, go to home
      if (isAuthenticated()) {
        console.log('User already authenticated, redirecting to home');
        next('/');
      } else {
        // Allow access to login page for non-authenticated users
        console.log('Proceeding to login page');
        next();
      }
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: to => {
      return isAuthenticated() ? '/' : '/login';
    }
  }
];

// Create router instance with history mode (no hash)
const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  console.log(`Navigating to: ${to.path}`);
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated()) {
    console.log('Authentication required, redirecting to login');
    next('/login');
  } else {
    next();
  }
});

export default router;