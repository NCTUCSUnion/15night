<template>
  <div class="modal-overlay" @click.self="close">
    <div class="upgrade-container">
      <div class="upgrade-header">
        <h2>Upgrade Shovel</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div v-if="loading" class="loading">
        <p>Loading shovel data...</p>
      </div>
      
      <div v-else class="upgrade-content">
        <div class="current-stats">
          <p><strong>Current Shovel Level:</strong> {{ shovelLevel }}</p>
          <p><strong>Your Money:</strong> {{ money }}</p>
          <p><strong>Upgrade Cost:</strong> {{ upgradeCost }}</p>
        </div>
        
        <div class="upgrade-action">
          <button 
            @click="upgradeShovel" 
            :disabled="upgrading || money < upgradeCost"
            class="upgrade-btn"
            :class="{ 'disabled': money < upgradeCost }"
          >
            {{ upgrading ? 'Upgrading...' : 'Upgrade Shovel' }}
          </button>
        </div>
        
        <p v-if="money < upgradeCost" class="not-enough-money">
          Not enough money! You need {{ upgradeCost - money }} more.
        </p>
        
        <div v-if="upgradeMessage" class="upgrade-message" :class="{ 'success': upgradeSuccess }">
          {{ upgradeMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { userAPI } from '../services/apiService';

export default {
  name: 'UpgradeModal',
  emits: ['close'],
  
  setup(props, { emit }) {
    const shovelLevel = ref(1);
    const money = ref(0);
    const loading = ref(true);
    const upgrading = ref(false);
    const upgradeMessage = ref('');
    const upgradeSuccess = ref(false);
    
    const upgradeCost = computed(() => {
      return shovelLevel.value * 100;
    });
    
    const close = () => {
      emit('close');
    };
    
    const loadUserData = async () => {
      loading.value = true;
      
      try {
        const response = await userAPI.getStats();
        shovelLevel.value = response.data.shovel_level;
        money.value = response.data.money;
      } catch (error) {
        console.error('Failed to load user stats:', error);
        upgradeMessage.value = 'Failed to load user data';
        upgradeSuccess.value = false;
      } finally {
        loading.value = false;
      }
    };
    
    const upgradeShovel = async () => {
      upgrading.value = true;
      upgradeMessage.value = '';
      
      try {
        const response = await userAPI.upgradeShovel();
        
        // Update local data with response
        shovelLevel.value = response.data.shovel_level;
        money.value = response.data.money;
        
        // Show success message
        upgradeMessage.value = response.data.message || 'Shovel upgraded successfully!';
        upgradeSuccess.value = true;
      } catch (error) {
        console.error('Failed to upgrade shovel:', error);
        upgradeMessage.value = error.response?.data?.detail || 'Failed to upgrade shovel';
        upgradeSuccess.value = false;
      } finally {
        upgrading.value = false;
      }
    };
    
    onMounted(() => {
      loadUserData();
    });
    
    return {
      shovelLevel,
      money,
      upgradeCost,
      loading,
      upgrading,
      upgradeMessage,
      upgradeSuccess,
      close,
      upgradeShovel
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

.upgrade-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 400px;
  padding: 20px;
}

.upgrade-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.upgrade-header h2 {
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

.loading {
  text-align: center;
  padding: 20px;
}

.current-stats {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.upgrade-action {
  text-align: center;
  margin: 20px 0;
}

.upgrade-btn {
  background-color: #4285f4;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  width: 100%;
}

.upgrade-btn:hover:not(.disabled) {
  background-color: #3367d6;
}

.upgrade-btn.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.not-enough-money {
  color: #dc3545;
  font-size: 14px;
  text-align: center;
}

.upgrade-message {
  margin-top: 20px;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  background-color: #f8d7da;
  color: #721c24;
}

.upgrade-message.success {
  background-color: #d4edda;
  color: #155724;
}
</style>
