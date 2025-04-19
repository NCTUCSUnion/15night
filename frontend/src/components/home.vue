<template>
    <div class="home">
        <div class="mobile-navbar">
            <div class="student-id">Hello, {{ userInfo?.studentId || 'User' }}</div>
            <button class="navbar-logout-btn" @click="logout">Logout</button>
        </div>
        <div class="header">
            <h1>15Night Game</h1>
        </div>
        <div class="game-container">
            <div class="buttons">
                <button @click="toggleBackpack">Backpack</button>
                <button @click="toggleUpgrade">Upgrade</button>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getUserInfo, removeToken, isAuthenticated } from '../services/authService';

export default {
    name: 'Home',
    setup() {
        const router = useRouter();
        const userInfo = ref(null);
        const tokenExpiry = ref('');
        
        onMounted(async () => {
            // Redirect if not authenticated
            if (!isAuthenticated()) {
                router.push('/login');
                return;
            }
            
            // Get user info from token
            const user = getUserInfo();
            userInfo.value = user;
            
            if (user && user.exp) {
                const expiryDate = new Date(user.exp * 1000);
                tokenExpiry.value = expiryDate.toLocaleString();
            }
            try {
                // Fetch user data from backend
                const response = await axios.get('/api/user/stats');
                console.log('User stats:', response.data);
                // You can update userInfo with additional data from response if needed
            } catch (error) {
                console.error('Error fetching user data:', error);
                if (error.response?.status === 401) {
                    removeToken();
                    router.push('/login');
                }
            }
        });
        
        const toggleBackpack = () => {
            alert('Backpack feature coming soon!');
        };
        
        const toggleUpgrade = () => {
            alert('Upgrade feature coming soon!');
        };
        
        const logout = () => {
            // Remove the token
            removeToken();
            // Navigate to login page
            router.push('/login');
        };
        
        return { 
            toggleBackpack, 
            toggleUpgrade,
            logout,
            userInfo,
            tokenExpiry
        };
    },
};
</script>

<style scoped>
.home {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    padding-top: 50px;
}
/* Mobile Navbar */
.mobile-navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between; /* Main axis */
    align-items: center; /* Cross-axis */
    background-color: #333;
    color: white;
    padding: 12px 15px;
    z-index: 100;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.student-id {
    font-weight: bold;
    font-size: 16px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.game-container {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    text-align: center;
}

.logout-btn {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}

.logout-btn:hover {
    background-color: #c82333;
}

.buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-top: 30px;
}

.buttons button {
    padding: 10px 20px;
    background-color: #4285f4;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.buttons button:hover {
    background-color: #3367d6;
}

@media (max-width: 768px) {
    .buttons {
        flex-direction: column;
        align-items: center;
    }

    .buttons button {
        width: 100%;
    }
}

.debug {
  background: #d4edda;
  color: #155724;
  padding: 5px;
  margin: 10px 0;
  border-radius: 4px;
}

.user-info {
    text-align: center;
    margin: 0 20px;
}

.token-expiry {
    font-size: 0.8em;
    color: #666;
}
</style>