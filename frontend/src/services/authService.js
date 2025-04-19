/**
 * Authentication service for token management
 */

// Token storage functions - use 'oauth_token' as the key
export const getToken = () => localStorage.getItem('oauth_token');
export const setToken = (token) => localStorage.setItem('oauth_token', token);
export const removeToken = () => localStorage.removeItem('oauth_token');

// Handle token from URL query parameter
export const handleTokenFromUrl = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');
  
  if (token) {
    console.log('Token found in URL, storing it');
    setToken(token);
    
    // Clean URL by removing token parameter
    const cleanUrl = window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl);
    
    return true;
  }
  return false;
};

// Check if token exists and is valid
export const isAuthenticated = () => {
  const token = getToken();
  if (!token) return false;
  
  try {
    // Parse the JWT token
    const payload = JSON.parse(atob(token.split('.')[1]));
    // Check if token is expired
    return payload.exp > Date.now() / 1000;
  } catch (e) {
    console.error('Error parsing token:', e);
    removeToken();
    return false;
  }
};

// Extract user info from token
export const getUserInfo = () => {
  const token = getToken();
  if (!token) return null;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      studentId: payload.sub, // Using 'sub' as studentId as per your backend
      isAdmin: payload.is_admin || false,
      exp: payload.exp,
      iat: payload.iat,
      iss: payload.iss
    };
  } catch (e) {
    console.error('Error extracting user info:', e);
    return null;
  }
};

// Initiate OAuth login
export const initiateOAuthLogin = () => {
  window.location.href = '/api/oauth/login';
};
