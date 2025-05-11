<template>
    <div class="home">
        <transition name="fade" mode="out-in">
            <div v-if="showToast" class="toast">{{ ToastMessage || 'Block selected!' }}</div>
        </transition>
        <div class="mobile-navbar">
            <div class="student-id">Hello, {{ userInfo?.studentId || 'User' }}</div>
            <button class="logout-btn" @click="logout">Logout</button>
        </div>
        <div class="game-category">
            <div class="category-buttons">
                <button @click="togglePrizePack">
                <img src="../assets/button/recycle_btn.png"/>
                </button>
                <button @click="toggleBackpack">
                <img src="../assets/button/backpack_btn.png"/>
                </button>
                <button @click="toggleUpgrade">
                <img src="../assets/button/upgrade_btn.png"/>
                </button>
                <button @click="toggleLeaderBoard">
                <img src="../assets/button/leaderboard_btn.png"/>
                </button>
                <button @click="toggleBlockSelection">
                <img src="../assets/button/cube_btn.png"/>
                </button>
            </div>
        </div>
        
        <!-- Mining progress display and button -->
        <div v-if="selectedBlock && blockHealth > 0" class="mining-controls">
            <button 
                class="mining-button" 
                @click="mineBlock" 
                :disabled="!selectedBlock || !isMining"
            >
                <img src="../assets/blocks/dirt.png">
            </button>
            <div class="mining-progress-container">
                <div class="mining-progress-bar" :style="{width: `${(blockHealth / maxBlockHealth) * 100}%`}"></div>
            </div>
                <p>
                <img src="../assets/icon/hp_icon.png" alt="Health" class="info-icon" />
                : {{ blockHealth }} / {{ maxBlockHealth }}
                </p>
        </div>
        <div class="user-info">
            <p>
            <img src="../assets/icon/coin_icon.png" alt="Money" class="info-icon" />
            X {{ money }}
            </p>
            <p>
                <img src="../assets/icon/pickaxe_icon.png" alt="Shovel" class="info-icon" />
                LV : {{ shovelLevel }}
            </p>
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
        <PrizePopup
         v-if="showPrizeHint"
         @close="togglePrizeHint"
         :message="priceHintMessage"
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
import PrizePopup from './PrizePopup.vue';
export default {
    name: 'Home',
    components: {
        BackpackModal,
        UpgradeModal,
        BlockSelection,
        LeaderBoard,
        GarbageHintPopup,
        PrizePack,
        WarningModal,
        PrizePopup
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
        const CLICK_COOLDOWN = 50;
        const priceHintMessage = ref('');
        const showPrizeHint = ref(false);

        // Calculate damage based on shovel level
        const damagePerClick = computed(() => {
            return shovelLevel.value;
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

                if (response.data.mining) {
                    isMining.value = true;
                    selectedBlockId.value = response.data.block_id;

                    // Populate selectedBlock with data from the status response
                    // This ensures the UI has the correct information for the ongoing session
                    selectedBlock.value = {
                        id: response.data.block_id,
                        name: response.data.name,
                        health: response.data.health, // This is likely the block's max health
                        got_garbage: response.data.got_garbage,
                        got_prize: response.data.got_prize,
                        prize_info: response.data.prize_info
                        // If other static block properties are needed on selectedBlock.value,
                        // you might want to merge with data from Blocks.value:
                        // const fullBlockDetails = Blocks.value.find(b => b.id === response.data.block_id);
                        // if (fullBlockDetails) {
                        //   selectedBlock.value = { ...fullBlockDetails, ...selectedBlock.value };
                        // }
                    };
                    
                    // Set current and max health. Based on current logic elsewhere,
                    // health from /status (and /start) seems to be the block's original/max health.
                    blockHealth.value = response.data.health;
                    maxBlockHealth.value = response.data.health;

                    console.log('Mining session restored from /api/blocks/status:', selectedBlock.value);
                    // DO NOT set isMining.value = false;
                    // DO NOT call handleStartMining();
                } else {
                    isMining.value = false;
                    // Optionally, you might want to clear selectedBlock if no session is active,
                    // though loadDefaultBlock would handle setting a new one if needed.
                    // selectedBlock.value = null;
                    // blockHealth.value = 0;
                    // maxBlockHealth.value = 0;
                }
            } catch (error) {
                console.error('Error checking mining status:', error);
                isMining.value = false; // Assume not mining on error
            }
        };

        // Minor correction in loadDefaultBlock for a typo
        const loadDefaultBlock = async () => {
            // Blocks.value should already be fetched by onMounted before this is typically called.
            // If it can be called in other contexts, ensure Blocks.value is populated.
            // Blocks.value = await fetchBlocks(); // This might be redundant if onMounted always runs first.
            if (Blocks.value && Blocks.value.length > 0) {
                // Ensure a block is selected to start mining on
                if (!selectedBlock.value) { // Only set a default if no block is selected (e.g. by syncMiningStatus)
                    const defaultBlockIdToLoad = 1; // Or some other logic for default
                    const defaultBlock = Blocks.value.find(b => b.id === defaultBlockIdToLoad) || Blocks.value[0];
                    selectedBlock.value = defaultBlock;
                }
                selectedBlockId.value = selectedBlock.value.id; // Ensure selectedBlockId is also in sync

                // blockHealth and maxBlockHealth will be set by handleStartMining
                handleStartMining(); // This is correct here, to initiate mining on the default block
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

        const togglePrizeHint = () => {
            showPrizeHint.value = !showPrizeHint.value;
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
                if (response.data.got_prize) {
                    priceHintMessage.value = response.data.prize_info.prize_name;
                }
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
                    // Update user stats after successful mining
                    await fetchUserStats();
                    toggleshowToast();
                    ToastMessage.value = `You earn ${response.data.money_earned} money!`;
                    console.log('Toast message:', ToastMessage.value);
                    if(response.data.got_garbage) {
                        showGarbageHint.value = true;
                        garbageHintMessage.value = `You received garbage!`;
                    }
                    if(response.data.got_prize) {
                        showPrizeHint.value = true;
                    }
                } catch (error) {
                    console.error('Error completing mining:', error);
                    if (error.response?.status === 400 && error.response?.data?.detail?.includes('Mining too fast')) {
                        WarningMessage.value = 'Mining too fast! Please slow down.';
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
            priceHintMessage,
            ToastMessage,
            WarningMessage,
            lastClickTime,
            CLICK_COOLDOWN,
            showPrizeHint,
            togglePrizeHint
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
    font-family: "VT323", Helvetica;  /* 設定字型 */
    font-size: 30px;                    /* 字體大小 */
    font-weight: bold;                  /* 字體粗細 */
    display: flex;
    justify-content: space-around;
    background-color: #f5f5f5;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 15px;
}

.user-info p {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
}

.info-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
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
    display: flex;
    align-items: center;
    justify-content: center;  
    flex-wrap: wrap;
    gap: 8px;
    padding: 0;
    background: none;
    border: none;
}

.category-buttons button {
    background: none;
    border: none;
    padding: 0;
}

.category-buttons img {
    width: 50px;
    height: 50px;
}


/* Mining Controls */
.mining-controls {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;         /* ⬅️ 這就是橫向置中的關鍵 */
  margin: 15px 0;
  padding: 15px;
  background-color: transparent;
  border-radius: 8px;
  text-align: center;
}
.mining-controls p {
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'VT323', monospace;
  font-size: 30px;
  margin-top: 8px;
}

.mining-button {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}

.mine-icon {
  width: 64px;
  height: 64px;
  object-fit: contain;
}

.mining-progress-container {
  width: 100%;
  height: 20px;
  background-color: transparent; /* 可加淡綠或透明 */
  border: 1px solid #4CAF50;
  border-radius: 10px;
  margin-top: 10px;
  overflow: hidden;
}

.mining-progress-bar {
  height: 100%;
  background-color: #4CAF50;
  transition: width 0.3s ease;
}

.mining-button:disabled .mine-icon {
  opacity: 0.4;
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
