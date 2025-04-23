<template>
  <div class="block-grid-container">
    <h2>Select Block to Mine</h2>
    
    <div v-if="loading" class="loading">
      <p>Loading blocks data...</p>
    </div>
    
    <div v-else>
      <div class="block-grid">
        <div 
          v-for="block in availableBlocks" 
          :key="block.id"
          class="block-item"
          :class="{ 'selected': selectedBlockId === block.id, 'disabled': !block.enabled }"
          @click="selectBlock(block)"
        >
          <div class="block-header">{{ block.name }}</div>
          <div class="block-content">
            <div class="block-stat">
              <span class="stat-label">Health:</span> 
              <span class="stat-value">{{ block.health }}</span>
            </div>
          </div>
          <div class="block-status">
            {{ block.enabled ? 'Available' : 'Locked' }}
          </div>
        </div>
      </div>
      
      <div v-if="selectedBlock" class="selected-block-info">
        <h3>Selected: {{ selectedBlock.name }}</h3>
        <div class="block-details">
          <p>Health: {{ selectedBlock.health }}</p>
        </div>
        <button 
          class="mine-button" 
          :disabled="!selectedBlock.enabled"
          @click="startMining"
        >
          Start Mining
        </button>
      </div>
      
      <div v-if="!selectedBlock" class="instruction">
        <p>Select a block from above to begin mining</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'BlockGrid',
  emits: ['select-block', 'start-mining'],
  
  setup(props, { emit }) {
    const blocks = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const selectedBlockId = ref(null);
    
    // Fetch blocks from API
    const fetchBlocks = async () => {
      try {
        loading.value = true;
        const response = await axios.get('/api/blocks', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        blocks.value = response.data.blocks;
      } catch (err) {
        error.value = 'Failed to load blocks data. Please try again.';
        console.error('Error fetching blocks:', err);
      } finally {
        loading.value = false;
      }
    };
    
    // Filter blocks that should be displayed (you can adjust this logic)
    const availableBlocks = computed(() => {
      // Show all blocks, even if not enabled
      return blocks.value;
    });
    
    // Get the currently selected block
    const selectedBlock = computed(() => {
      return blocks.value.find(block => block.id === selectedBlockId.value);
    });
    
    // Handle block selection
    const selectBlock = (block) => {
      if (block.enabled) {
        selectedBlockId.value = block.id;
        emit('select-block', block);
      } else {
        // Optionally show a message about locked blocks
        console.log(`${block.name} is locked`);
      }
    };
    
    // Start mining the selected block
    const startMining = () => {
      if (selectedBlock.value && selectedBlock.value.enabled) {
        emit('start-mining', selectedBlock.value);
      }
    };
    
    // Add a method to refresh blocks data
    const refreshBlocks = () => {
      fetchBlocks();
    };
    
    // Load blocks when component mounts
    onMounted(() => {
      fetchBlocks();
    });
    
    return {
      blocks,
      loading,
      error,
      availableBlocks,
      selectedBlockId,
      selectedBlock,
      selectBlock,
      startMining,
      refreshBlocks
    };
  }
};
</script>

<style scoped>
.block-grid-container {
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 20px;
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

.loading {
  text-align: center;
  padding: 20px;
}

.block-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.block-item {
  background-color: white;
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.block-item:hover:not(.disabled) {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-color: #3367d6;
}

.block-item.selected {
  border-color: #4285f4;
  background-color: #e8f0fe;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.block-item.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #f5f5f5;
}

.block-header {
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
  text-align: center;
}

.block-content {
  flex-grow: 1;
  margin-bottom: 10px;
}

.block-stat {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.stat-label {
  font-weight: 500;
}

.stat-value {
  font-weight: bold;
}


.block-status {
  font-size: 12px;
  padding: 4px;
  text-align: center;
  border-radius: 4px;
  background-color: #eee;
}

.selected-block-info {
  margin-top: 20px;
  text-align: center;
}

.mine-button {
  background-color: #4285f4;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}

.mine-button:hover:not(:disabled) {
  background-color: #3367d6;
}

.mine-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.block-details {
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
  text-align: left;
}

.instruction {
  margin-top: 20px;
  color: #666;
  font-style: italic;
  text-align: center;
}
</style>
