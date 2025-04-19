<template>
  <div class="modal-overlay" @click.self="close">
    <div class="backpack-container">
      <div class="backpack-header">
        <h2>Your Backpack</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div v-if="loading" class="loading">
        <p>Loading backpack items...</p>
      </div>
      
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="fetchBackpackItems">Try Again</button>
      </div>
      
      <div v-else class="backpack-content">
        <div v-if="items.length === 0" class="empty-backpack">
          <p>Your backpack is empty!</p>
        </div>
        
        <div v-else class="items-grid">
          <div v-for="item in items" :key="item.block_id" class="backpack-item">
            <div class="item-card" :class="{ 'prize-item': item.type === 'prize' }">
              <h3>{{ item.name }}</h3>
              <p class="quantity">x{{ item.quantity }}</p>
              <p class="item-type">{{ item.type }}</p>
            </div>
          </div>
        </div>
        
        <div class="backpack-stats">
          <p>Total Items: {{ totalItems }}</p>
          <p>Unique Items: {{ uniqueItems }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { getToken, isAuthenticated } from '../services/authService';

export default {
  name: 'Backpack',
  emits: ['close'],
  
  setup(props, { emit }) {
    const router = useRouter();
    const items = ref([]);
    const loading = ref(true);
    const error = ref('');
    const totalItems = ref(0);
    const uniqueItems = ref(0);
    
    const close = () => {
      emit('close');
    };
    
    const fetchBackpackItems = async () => {
      loading.value = true;
      error.value = '';
      
      // Check authentication status before making request
      if (!isAuthenticated()) {
        console.error('User not authenticated, redirecting to login');
        router.push('/login');
        return;
      }
      
      try {
        // Get token directly before request for extra safety
        const token = getToken();
        
        // Make request with token in headers
        const response = await axios.get('/api/user/backpack', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        console.log('Backpack data:', response.data);
        
        // Parse the response data
        if (response.data && response.data.items) {
          items.value = response.data.items;
          totalItems.value = response.data.total_items || 0;
          uniqueItems.value = response.data.unique_items || 0;
        } else {
          items.value = [];
          error.value = 'Invalid response format from server';
        }
      } catch (err) {
        console.error('Error fetching backpack items:', err);
        error.value = err.response?.data?.detail || 'Failed to load backpack items';
        
        // Handle unauthorized error
        if (err.response?.status === 401) {
          router.push('/login');
        }
      } finally {
        loading.value = false;
      }
    };
    
    onMounted(() => {
      fetchBackpackItems();
    });
    
    return {
      items,
      loading,
      error,
      totalItems,
      uniqueItems,
      close,
      fetchBackpackItems
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

.backpack-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  padding: 20px;
}

.backpack-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.backpack-header h2 {
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

.loading, .error, .empty-backpack {
  text-align: center;
  padding: 20px;
}

.error {
  color: #dc3545;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.item-card {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 10px;
  text-align: center;
  background-color: #f9f9f9;
  height: 100%;
}

.prize-item {
  background-color: #fff3cd;
  border-color: #ffeeba;
}

.item-card h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
}

.quantity {
  font-weight: bold;
  color: #28a745;
  margin: 5px 0;
}

.item-type {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
}

.backpack-stats {
  border-top: 1px solid #eee;
  padding-top: 15px;
  margin-top: 15px;
  display: flex;
  justify-content: space-around;
}

@media (max-width: 480px) {
  .items-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
