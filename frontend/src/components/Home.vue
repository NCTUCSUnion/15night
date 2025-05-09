<template>
    <div class="home">
        <transition name="fade" mode="out-in">
            <div v-if="showToast" class="toast">{{ ToastMessage || 'Block selected!' }}</div>
        </transition>
        <div class="mobile-navbar">
            <div class="student-id">Hello, {{ userInfo?.studentId || 'User' }}</div>
            <button class="logout-btn" @click="logout">Logout</button>
        </div>
        <div class="header">
            <h1>15Night Game</h1>
        </div>
        <div class="user-info">
            <p>Money: {{ money }}</p>
            <p>Shovel Level: {{ shovelLevel }}</p>
        </div>
        
        <!-- Mining progress display and button -->
        <div v-if="selectedBlock && blockHealth > 0" class="mining-controls">
            <div class="mining-progress-container">
                <div class="mining-progress-bar" :style="{width: `${(blockHealth / maxBlockHealth) * 100}%`}"></div>
            </div>
            <p>Block Health: {{ blockHealth }}/{{ maxBlockHealth }}</p>
            <button 
                class="mining-button" 
                @click="mineBlock" 
                :disabled="!selectedBlock || !isMining"
            >
                Mine Block
            </button>
        </div>
        <div class="game-category">
            <div class="category-buttons">
                <button @click="toggleBlockSelection">Select Block</button>
                <button @click="toggleBackpack">Backpack</button>
                <button @click="toggleUpgrade">Upgrade</button>
                <button @click="toggleLeaderBoard">Leaderboard</button>
                <button @click="togglePrizePack">Prize Pack</button>
            </div>
        </div>
        <BlockSelection 
            v-if="showBlockSelection"
            :currentSelectedBlock="selectedBlock"
            @select-block="handleBlockSelection"
            @close="toggleBlockSelection"
        />
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
        <LeaderBoard
         v-if="showLeaderBoard"
         @close="toggleLeaderBoard"
         :studentId="userInfo?.studentId"
        />
        <GarbageHintPopup
         v-if="showGarbageHint"
         @close="showGarbageHint = !showGarbageHint"
         :message="garbageHintMessage"
        />
        <PrizePack
         v-if="showPrizePack"
         @close="togglePrizePack"
        />
        <WarningModal
         v-if="showWarning"
         @close="toggleWarning"
         :message="WarningMessage"
        />
    </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getUserInfo, removeToken, isAuthenticated } from '../services/authService';
import BackpackModal from './Backpack.vue';
import UpgradeModal from './Upgrade.vue';
import BlockSelection from './BlockSelection.vue';
import LeaderBoard from './LeaderBoard.vue';
import GarbageHintPopup from './GarbageHintPopup.vue';
import PrizePack from './PrizePack.vue';
import WarningModal from './WarningModal.vue';
export default {
    name: 'Home',
    components: {
        BackpackModal,
        UpgradeModal,
        BlockSelection,
        LeaderBoard,
        GarbageHintPopup,
        PrizePack,
        WarningModal
    },
    created() {
        axios.defaults.withCredentials = true;
    },
    setup() {
        const router = useRouter();
        const userInfo = ref(null);
        const tokenExpiry = ref('');
        const showBlockSelection = ref(false);
        const showBackpack = ref(false);
        const showUpgrade = ref(false);
        const showLeaderBoard = ref(false);
        const showGarbageHint = ref(false);
        const showPrizePack = ref(false);
        const shovelLevel = ref(1);
        const money = ref(0);
        const selectedBlock = ref(null);
        const selectedBlockId = ref(null);
        const isMining = ref(false);
        const blockHealth = ref(0);
        const maxBlockHealth = ref(0);
        const garbageHintMessage = ref('');
        const showToast = ref(false);
        const ToastMessage = ref('');
        const WarningMessage = ref('');
        const showWarning = ref(false);
        const lastClickTime = ref(0);
        const CLICK_COOLDOWN = 500; // 500ms cooldown between clicks

        // Calculate damage based on shovel level
        const damagePerClick = computed(() => {
            return shovelLevel.value; // 5 damage per shovel level
        });
        const Blocks = ref([]);
        const fetchBlocks = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('/api/blocks', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    },
                    withCredentials: true
                });
                return response.data.blocks;
            } catch (error) {
                console.error('Error fetching blocks:', error);
            }
        };
        // Function to fetch user stats from the server
        // This function will be called when the user clicks the "Upgrade" button
        const fetchUserStats = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('/api/user/stats', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    },
                    withCredentials: true
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

        const syncMiningStatus = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.post('/api/blocks/status', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    },
                    withCredentials: true
                });
                isMining.value = response.data.mining;
                if(isMining.value) {
                    selectedBlockId.value = response.data.block_id;
                    selectedBlock.value = Blocks.value.find(b => b.id === selectedBlockId.value) || Blocks.value[0];
                    isMining.value = false;
                    handleStartMining();
                }
            } catch (error) {
                console.error('Error checking mining status:', error);
            }
        };

        // Load default block (id = 1) if nothing is selected
        const loadDefaultBlock = async () => {
            Blocks.value = await fetchBlocks();
            if (Blocks.value && Blocks.value.length > 0) {
                // Find block with ID 1 or use first block
                selectedBlockId.value = selectedBlockId.value ? selectedBlockId.value : 1;
                if(!selectedBlock.value) {
                    const defaultBlock = Blocks.value.find(b => b.id === selectedBlockId.values) || Blocks.value[0];
                    selectedBlock.value = defaultBlock;
                }
                handleStartMining();
            }
            else {
                console.error('No blocks available to load as default.');
            }
            console.log('Default block loaded:', selectedBlock.value);
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
            await fetchUserStats();
            
            Blocks.value = await fetchBlocks();
            await syncMiningStatus();
            // show isMining 
            console.log('isMining:', isMining.value);
            // If no active mining session and no selected block, load default
            if (!isMining.value && !selectedBlock.value) {
                await loadDefaultBlock();
            }
        });
        
        const toggleBackpack = () => {
            showBackpack.value = !showBackpack.value;
        };
        
        const toggleUpgrade = () => {
            showUpgrade.value = !showUpgrade.value;
        };
        
        const toggleLeaderBoard = () => {
            showLeaderBoard.value = !showLeaderBoard.value;
        };

        const toggleBlockSelection = () => {
            showBlockSelection.value = !showBlockSelection.value;
        };

        const togglePrizePack = () => {
            showPrizePack.value = !showPrizePack.value;
        };

        const toggleshowToast = () => {
            showToast.value = true;
            setTimeout(() => {
                showToast.value = false;
            }, 500);
        };

        const toggleWarning = () => {
            showWarning.value = !showWarning.value;
        };

        const logout = () => {
            // Remove the token
            removeToken();
            // Navigate to login page
            router.push('/login');
        };
        
        // Handle block selection from BlockGrid
        const handleBlockSelection = async (block) => {
            // If a block is already selected, stop mining on it
            console.log('Block selected:', block.id);
            console.log('Current Block selected:', selectedBlock.value?.id);
            console.log('isMining:', isMining.value);
            if (isMining.value && selectedBlock.value && selectedBlock.value.id !== block.id) {
                try {
                    const token = localStorage.getItem('token');
                    await axios.post(`/api/blocks/${selectedBlock.value.id}/cancel`, {}, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    });
                    isMining.value = false;
                } catch (error) {
                    console.error('Error stopping mining:', error);
                }
            }
            selectedBlock.value = block;
            selectedBlockId.value = block.id;
            blockHealth.value = block.health;
            maxBlockHealth.value = block.health;
            console.log('Selected block:', block.name);
            handleStartMining();
        };
        
        // Handle mining start
        const handleStartMining = async () => {
            if (isMining.value) return;
            try {
                isMining.value = true;
                console.log(`Mining started on ${selectedBlock.value.name}`);
                
                const token = localStorage.getItem('token');
                const response = await axios.post(`/api/blocks/${selectedBlock.value.id}/start`, 
                    {}, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    }, {
                        withCredentials: true
                    }
                );
                
                // Map the API response to match our expected structure
                const blockData = {
                    id: response.data.block_id, // Map block_id to id
                    name: response.data.name,
                    health: response.data.health,
                    got_garbage: response.data.got_garbage,
                    got_prize: response.data.got_prize,
                    prize_info: response.data.prize_info
                };
                
                selectedBlock.value = blockData;
                blockHealth.value = response.data.health;
                maxBlockHealth.value = response.data.health;
                console.log('Block health:', blockHealth.value);
                console.log('selectedBlock:', selectedBlock.value);
            } catch (error) {
                console.error('Mining error:', error);
                alert('Failed to mine block. Please try again.');
            }
        };
        
        
        // Handle mining click with rate limiting
        const mineBlock = async () => {
            if (!selectedBlock.value || blockHealth.value <= 0) return;
            
            // Check if clicking too fast
            const currentTime = Date.now();
            if (currentTime - lastClickTime.value < CLICK_COOLDOWN) {
                WarningMessage.value = "You are mining too fast! Please slow down.";
                showWarning.value = true;
                return;
            }
            
            // Update last click time
            lastClickTime.value = currentTime;
            
            // Decrease block health based on shovel level
            blockHealth.value = Math.max(0, blockHealth.value - damagePerClick.value);
            
            // If block health reaches 0, complete mining
            if (blockHealth.value === 0) {
                try {
                    isMining.value = false;
                    const token = localStorage.getItem('token');
                    const response = await axios.post(`/api/blocks/${selectedBlock.value.id}/complete`, 
                        {}, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        },
                        withCredentials: true
                    });
                    if(response.data.got_garbage) {
                        showGarbageHint.value = true;
                        garbageHintMessage.value = `You received garbage!`;
                    }
                    // Update user stats after successful mining
                    await fetchUserStats();
                    toggleshowToast();
                    ToastMessage.value = `You earn ${response.data.money_earned} money!`;
                    console.log('Toast message:', ToastMessage.value);
                } catch (error) {
                    console.error('Error completing mining:', error);
                    if (error.response?.status === 400 && error.response?.data?.message?.includes('Mining too fast')) {
                        WarningMessage.value = error.response.data.message || 'Mining too fast! Please slow down.';
                        showWarning.value = true;
                    } else{
                        alert('Failed to complete mining. Please try again.');
                    }
                } finally {
                    isMining.value = false;
                    handleStartMining(); // Restart mining on the next block
                }
            }
        };
        
        return {
            Blocks,
            fetchBlocks,
            toggleBlockSelection,
            toggleBackpack, 
            toggleUpgrade,
            toggleLeaderBoard,
            togglePrizePack,
            toggleshowToast,
            toggleWarning,
            logout,
            fetchUserStats,
            userInfo,
            tokenExpiry,
            showToast,
            showBlockSelection,
            showBackpack,
            showUpgrade,
            showLeaderBoard,
            showPrizePack,
            showWarning,
            shovelLevel,
            money,
            handleBlockSelection,
            handleStartMining,
            selectedBlock,
            isMining,
            blockHealth,
            maxBlockHealth,
            mineBlock,
            damagePerClick,
            showGarbageHint,
            garbageHintMessage,
            ToastMessage,
            WarningMessage,
            lastClickTime,
            CLICK_COOLDOWN,
        };
    },
};
</script>

<style scoped>
.home {
    max-width: 100%;
    width: 100vw;
    height: 100vh;
    margin: 0 auto;
    padding: 15px;
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
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 60%;
}

.header {
    margin-bottom: 20px;
    text-align: center;
}

.header h1 {
    font-size: 24px;
    margin: 0;
}

.user-info {
    display: flex;
    justify-content: space-around;
    background-color: #f5f5f5;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 15px;
}

.user-info p {
    margin: 0;
    font-weight: bold;
}

.logout-btn {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}
.logout-btn:hover {
    background-color: #c82333;
}

/* Game Category buttons */
.game-category {
    margin-top: 15px;
}

.category-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 15px;
}

.category-buttons button {
    padding: 12px 0;
    background-color: #4285f4;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.category-buttons button:hover {
    background-color: #3367d6;
}

/* Mining Controls */
.mining-controls {
    margin: 15px 0;
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
    padding: 15px 0;
    width: 100%;
    background-color: #ff9800;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    margin-top: 10px;
    font-size: 16px;
}

.mining-button:hover {
    background-color: #f57c00;
}

.mining-button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}

/* Add meta viewport tag to ensure proper scaling */
@media (max-width: 480px) {
    .header h1 {
        font-size: 22px;
    }
    
    .mining-button {
        padding: 12px 0;
    }
    
    .home {
        padding: 10px;
        padding-top: 50px;
    }
}

.toast {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background-color: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 16px;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.5s;
}

/* When the toast is shown */
.toast.fade-enter-active, .toast.fade-leave-active {
    transition: opacity 0.5s ease-in-out;
}

.toast.fade-enter-from, .toast.fade-leave-to {
    opacity: 0;
}

.toast.fade-enter-to, .toast.fade-leave-from {
    opacity: 1;
}
</style>