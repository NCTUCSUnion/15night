<template>
    <div class="home">
        <div class="mobile-navbar">
            <div class="student-id">Hello, {{ userInfo?.studentId || 'User' }}</div>
            <button class="navbar-logout-btn" @click="logout">Logout</button>
        </div>
        <div class="header">
            <h1>15Night Game</h1>
        </div>
        <div class="user-info">
            <p>Money: {{ money }}</p>
            <p>Shovel Level: {{ shovelLevel }}</p>
        </div>
        <BlockGrid 
            @select-block="handleBlockSelection"
            @start-mining="handleStartMining"
        />
        
        <!-- Mining progress display and button -->
        <div v-if="selectedBlock && blockHealth > 0" class="mining-controls">
            <div class="mining-progress-container">
                <div class="mining-progress-bar" :style="{width: `${(blockHealth / maxBlockHealth) * 100}%`}"></div>
            </div>
            <p>Block Health: {{ blockHealth }}/{{ maxBlockHealth }}</p>
            <button 
                class="mining-button" 
                @click="mineBlock" 
                :disabled="!selectedBlock || isMining"
            >
                Mine Block
            </button>
        </div>
        
        <div class="game-category">
            <div class="buttons">
                <button @click="toggleBackpack">Backpack</button>
                <button @click="toggleUpgrade">Upgrade</button>
            </div>
        </div>
        <BackpackModal
        v-if="showBackpack"
        @close="toggleBackpack"
         />
        <UpgradeModal
         v-if="showUpgrade"
         @close="toggleUpgrade" 
         :fetchUserStats="fetchUserStats"
         :shovelLevel="shovelLevel"
         :money="money"
        />
    </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getUserInfo, removeToken, isAuthenticated } from '../services/authService';
import BackpackModal from './backpack.vue';
import UpgradeModal from './upgrade.vue';
import BlockGrid from './BlockGrid.vue';

export default {
    name: 'Home',
    components: {
        BackpackModal,
        UpgradeModal,
        BlockGrid
    },
    setup() {
        const router = useRouter();
        const userInfo = ref(null);
        const tokenExpiry = ref('');
        const showBackpack = ref(false);
        const showUpgrade = ref(false);
        const shovelLevel = ref(1);
        const money = ref(0);
        const selectedBlock = ref(null);
        const isMining = ref(false);
        const blockHealth = ref(0);
        const maxBlockHealth = ref(0);
        
        // Calculate damage based on shovel level
        const damagePerClick = computed(() => {
            return shovelLevel.value; // 5 damage per shovel level
        });

        // Function to fetch user stats from the server
        // This function will be called when the user clicks the "Upgrade" button
        const fetchUserStats = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('/api/user/stats', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                shovelLevel.value = response.data.shovel_level;
                money.value = response.data.money;
            } catch (error) {
                console.error('Error fetching user data:', error);
                if (error.response?.status === 401) {
                    removeToken();
                    router.push('/login');
                }
            }
        };

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
            // Fetch user stats
            await fetchUserStats();
        });
        
        const toggleBackpack = () => {
            showBackpack.value = !showBackpack.value;
        };
        
        const toggleUpgrade = () => {
            showUpgrade.value = !showUpgrade.value;
        };
        
        const logout = () => {
            // Remove the token
            removeToken();
            // Navigate to login page
            router.push('/login');
        };
        
        // Handle block selection from BlockGrid
        const handleBlockSelection = (block) => {
            selectedBlock.value = block;
            console.log('Selected block:', block.name);
        };
        
        // Handle mining start
        const handleStartMining = async (block) => {
            if (isMining.value) return;
            try {
                isMining.value = true;
                console.log(`Mining started on ${block.name}`);
                // Make API call to start mining
                const token = localStorage.getItem('token');
                const response = await axios.post(`/api/blocks/${block.id}/start`, 
                    {}, 
                    {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    }
                );
                blockHealth.value = response.data.health;
                maxBlockHealth.value = response.data.health;
                selectedBlock.value = block;
                console.log('Block health:', blockHealth.value);
                console.log('selectedBlock:', selectedBlock.value);
                // await fetchUserStats();
                
            } catch (error) {
                console.error('Mining error:', error);
                alert('Failed to mine block. Please try again.');
            } finally {
                isMining.value = false;
            }
        };
        
        axios.defaults.withCredentials = true;
        // Handle mining click
        const mineBlock = async () => {
            if (!selectedBlock.value || blockHealth.value <= 0) return;
            
            // Decrease block health based on shovel level
            blockHealth.value = Math.max(0, blockHealth.value - damagePerClick.value);
            
            // If block health reaches 0, complete mining
            if (blockHealth.value === 0) {
                try {
                    isMining.value = true;
                    const token = localStorage.getItem('token');
                    await axios.post(`/api/blocks/${selectedBlock.value.id}/complete`, 
                        {}, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        },
                        withCredentials: true
                    });
                    
                    // Update user stats after successful mining
                    await fetchUserStats();
                    alert(`Successfully mined ${selectedBlock.value.name}!`);
                    
                    // Reset mining state
                    selectedBlock.value = null;
                } catch (error) {
                    console.error('Error completing mining:', error);
                    alert('Failed to complete mining. Please try again.');
                } finally {
                    isMining.value = false;
                }
            }
        };
        
        return { 
            toggleBackpack, 
            toggleUpgrade,
            logout,
            fetchUserStats,
            userInfo,
            tokenExpiry,
            showBackpack,
            showUpgrade,
            shovelLevel,
            money,
            handleBlockSelection,
            handleStartMining,
            selectedBlock,
            isMining,
            blockHealth,
            maxBlockHealth,
            mineBlock,
            damagePerClick
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
    color: #213547; /* Explicitly set text color */
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

/* Mining Controls */
.mining-controls {
    margin: 20px auto;
    padding: 15px;
    background-color: #f5f5f5;
    border-radius: 8px;
    text-align: center;
}

.mining-progress-container {
    width: 100%;
    height: 20px;
    background-color: #e0e0e0;
    border-radius: 10px;
    margin-bottom: 10px;
    overflow: hidden;
}

.mining-progress-bar {
    height: 100%;
    background-color: #4CAF50;
    transition: width 0.3s ease;
}

.mining-button {
    padding: 10px 20px;
    background-color: #ff9800;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    margin-top: 10px;
}

.mining-button:hover {
    background-color: #f57c00;
}

.mining-button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}
</style>