<template>
  <div class="modal-overlay" @click.self="close">
    <div class="prizes-container">
      <div class="prizes-header">
        <h2>Your Prizes</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div v-if="loading" class="loading">
        <p>Loading prizes...</p>
      </div>
      
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="fetchPrizes">Try Again</button>
      </div>
      
      <div v-else class="prizes-content">
        <div v-if="prizes.length === 0" class="empty-prizes">
          <p>You haven't won any prizes yet!</p>
          <p class="hint">Keep mining to win special prizes.</p>
        </div>
        
        <div v-else class="prizes-grid">
          <div v-for="prize in prizes" :key="prize.id" class="prize-item">
            <div class="prize-card">
              <h3>{{ prize.prize_name || 'Mystery Prize' }}</h3>
              <p class="prize-details">Block: {{ prize.name }}</p>
              <p class="date">Won on: {{ formatDate(prize.created_at) }}</p>
              
              <div class="prize-status" :class="{ 'claimed-status': prize.claimed }">
                {{ prize.claimed ? 'CLAIMED' : 'UNCLAIMED' }}
              </div>
              
              <p v-if="prize.claimed" class="claimed-date">
                Claimed on: {{ formatDate(prize.claimed_at) }}
              </p>
            </div>
          </div>
        </div>
        
        <div class="prizes-stats">
          <p>Total Prizes: {{ prizes.length }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getToken, isAuthenticated } from '../services/authService';

export default {
  name: 'PrizePack',
  emits: ['close'],
  
  setup(props, { emit }) {
    const router = useRouter();
    const prizes = ref([]);
    const loading = ref(true);
    const error = ref('');
    
    const close = () => {
      emit('close');
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown';
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };
    
    const fetchPrizes = async () => {
      loading.value = true;
      error.value = '';
      
      if (!isAuthenticated()) {
        console.error('User not authenticated, redirecting to login');
        router.push('/login');
        return;
      }
      
      try {
        const token = getToken();
        const response = await axios.get('/api/user/prizes', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.data && response.data.prizes) {
          prizes.value = response.data.prizes;
        } else {
          prizes.value = [];
          error.value = 'Invalid response format from server';
        }
      } catch (err) {
        console.error('Error fetching prizes:', err);
        error.value = err.response?.data?.detail || 'Failed to load prizes';
        
        if (err.response?.status === 401) {
          router.push('/login');
        }
      } finally {
        loading.value = false;
      }
    };
    
    onMounted(() => {
      fetchPrizes();
    });
    
    return {
      prizes,
      loading,
      error,
      close,
      fetchPrizes,
      formatDate
    };
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.prizes-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  padding: 20px;
}

.prizes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.prizes-header h2 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.loading, .error, .empty-prizes {
  text-align: center;
  padding: 20px;
}

.error {
  color: #dc3545;
}

.hint {
  color: #6c757d;
  font-style: italic;
  font-size: 0.9rem;
}

.prizes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.prize-card {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 15px;
  background-color: #f9f9f9;
  height: 100%;
  position: relative;
  transition: transform 0.2s;
}

.prize-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.prize-card.claimed {
  background-color: #f8f9fa;
  border-color: #e9ecef;
}

.prize-card h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.prize-details {
  margin: 5px 0;
  color: #555;
}

.date {
  font-size: 0.8rem;
  color: #6c757d;
  margin: 5px 0;
}

.prize-status {
  display: inline-block;
  padding: 3px 8px;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
  background-color: #ffc107;
  border-radius: 3px;
  margin: 5px 0;
}

.claimed-status {
  background-color: #28a745;
}

.claimed-date {
  font-size: 0.8rem;
  color: #28a745;
  margin-top: 10px;
}

.prizes-stats {
  border-top: 1px solid #eee;
  padding-top: 15px;
  margin-top: 15px;
  display: flex;
  justify-content: center;
  font-size: 0.9rem;
}

@media (max-width: 480px) {
  .prizes-grid {
    grid-template-columns: 1fr;
  }
  
  .prizes-stats {
    flex-direction: column;
    text-align: center;
  }
  
  .prizes-stats p {
    margin: 5px 0;
  }
}
</style>
