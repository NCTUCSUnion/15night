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
            :class="{ 'selected': currentSelectedBlockId === block.id}"
            @click="selectBlock(block)"
          >
            <div class="block-header">{{ block.name }}</div>
            <div class="block-content">
              <div class="block-stat">
                <span class="stat-label">Health:</span> 
                <span class="stat-value">{{ block.health }}</span>
              </div>
            </div>
          </div>
        </div>
        <button 
          class="mine-button" 
          @click="emitBlockSelection"
          >Choose this block!</button>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, onMounted, watch } from 'vue';
  import axios from 'axios';
  
  export default {
    name: 'BlockSelection',
    props: {
      selectedBlock: {
        type: Object,
        default: () => null
      }
    },
    setup(props, { emit }) {
      const blocks = ref([]);
      const loading = ref(true);
      const error = ref(null);
      
      // Local state that mirrors the props
      const currentSelectedBlock = ref(props.selectedBlock);
      const currentSelectedBlockId = ref(props.selectedBlock ? props.selectedBlock.id : null);
      
      watch(() => props.selectedBlock, (newBlock) => {
        currentSelectedBlock.value = newBlock;
        currentSelectedBlockId.value = newBlock ? newBlock.id : null;
      });
      
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

      const emitBlockSelection = () => {
        emit('select-block', currentSelectedBlock.value);
      };
      
      const selectBlock = (block) => {
        currentSelectedBlockId.value = block.id;
        currentSelectedBlock.value = block;
      };

      const availableBlocks = computed(() => {
        return blocks.value;
      });
      
      // Load blocks when component mounts
      onMounted(() => {
        fetchBlocks();
      });
      
      return {
        blocks,
        loading,
        error,
        currentSelectedBlockId,
        currentSelectedBlock,
        selectBlock,
        availableBlocks,
        emitBlockSelection
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
  
  .block-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-color: #3367d6;
  }
  
  .block-item.selected {
    border-color: #4285f4;
    background-color: #e8f0fe;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
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
