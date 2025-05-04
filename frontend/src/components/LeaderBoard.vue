<template>
    <div class="leaderboard-modal-overlay" @click.self="$emit('close')">
        <div class="leaderboard-modal">
            <div class="header-row">
                <h1 class="leaderboard-title">Leaderboard</h1>
                <button class="close-button" @click="$emit('close')">×</button>
            </div>
            
            <div v-if="loading" class="loading">
                Loading leaderboard data...
            </div>
            
            <div v-else-if="error" class="error">
                {{ error }}
            </div>
            
            <table v-else class="leaderboard-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Student ID</th>
                        <th>Shovel Level</th>
                        <th>Money</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="player in topPlayers" :key="player.student_id" :class="{ 'current-user': isCurrentUser(player.student_id) }">
                        <td>{{ player.rank }}</td>
                        <td>{{ player.student_id }}</td>
                        <td>{{ player.shovel_level }}</td>
                        <td>{{ formatMoney(player.money) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

export default {
    name: 'LeaderBoard',
    
    emits: ['close'],
    
    setup(props, { emit }) {
        const leaderboardData = ref([]);
        const loading = ref(true);
        const error = ref(null);
        const currentUserId = ref(null); // This would come from your auth system

        const close = () => {
            emit('close');
        };
        const topPlayers = computed(() => {
            // Return only top 10 players
            return leaderboardData.value.slice(0, 10);
        });

        async function fetchLeaderboardData() {
            try {
                    loading.value = true;
                    const response = await axios.get('/api/leaderboard');
                    leaderboardData.value = response.data;
                    loading.value = false;
            } catch (err) {
                    error.value = 'Failed to load leaderboard data';
                    loading.value = false;
                    console.error('Error fetching leaderboard:', err);
            }
        }

        function formatMoney(amount) {
            return amount.toLocaleString();
        }

        function isCurrentUser(studentId) {
            return studentId === currentUserId.value;
        }

        onMounted(() => {
            fetchLeaderboardData();
            // You could set the current user ID here from your auth system
            // currentUserId.value = yourAuthSystem.getCurrentUser().id;
        });

        return {
            loading,
            error,
            topPlayers,
            formatMoney,
            isCurrentUser,
            close
        };
    }
}
</script>

<style scoped>
.leaderboard-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.leaderboard-modal {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    width: 90%;
    max-width: 800px;
    padding: 20px;
    animation: modal-appear 0.3s ease-out;
}

@keyframes modal-appear {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.leaderboard-title {
    margin: 0;
}

.close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
}

.close-button:hover {
    background-color: #f0f0f0;
}

.leaderboard-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}

.leaderboard-table th,
.leaderboard-table td {
    padding: 12px;
    text-align: center;
    border-bottom: 1px solid #ddd;
}

.leaderboard-table th {
    background-color: #f2f2f2;
    font-weight: bold;
}

.leaderboard-table tr:nth-child(even) {
    background-color: #f8f8f8;
}

.leaderboard-table tr:hover {
    background-color: #eaf0f7;
}

.current-user {
    background-color: #fffbdd !important;
    font-weight: bold;
}

.loading, .error {
    text-align: center;
    margin: 40px 0;
    font-style: italic;
}

.error {
    color: #d32f2f;
}
</style>