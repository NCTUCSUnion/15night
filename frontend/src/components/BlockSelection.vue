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
            <div class="block-content">
              <img 
                class="block-image"
                :src="getBlockImage(block.name)" 
                :alt="block.name"
              />
              <div class="block-stat">
                <img src="../assets/icon/hp_icon.png" alt="Health" class="block-stat-icon"/>
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

      const blockImages = {
        stone: new URL('@/assets/blocks/stone.png', import.meta.url).href,
        coal: new URL('@/assets/blocks/coal.png', import.meta.url).href,
        dirt: new URL('@/assets/blocks/dirt.png', import.meta.url).href,
        diamond: new URL('@/assets/blocks/diamond.png', import.meta.url).href,
        iron: new URL('@/assets/blocks/iron.png', import.meta.url).href,
        gold: new URL('@/assets/blocks/gold.png', import.meta.url).href,
      };

      const getBlockImage = (name) => {
        return blockImages[name.toLowerCase()] ?? new URL('@/assets/blocks/default.png', import.meta.url).href;
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
        emitBlockSelection,
        getBlockImage  
      };
    }
  };
</script>
  
<style scoped>
.block-grid-container {
  font-family: "VT323", Helvetica;  /* 設定字型 */
  font-size: 20px;                    /* 字體大小 */
  font-weight: bold; 
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
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.block-item {
  width: 70px; /* 原本 80px 太大 */
  display: flex;
  flex-direction: column;
  align-items: center;
  background: none;
  border: none;
  padding: 0;
  margin: 0;
}

.block-item:hover {
  transform: translateY(-3px);
}

.block-item.selected {
  outline: 2px solid #4285f4;
  outline-offset: 2px;
}


.block-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 0;
}


.block-image {
  width: 48px;
  height: 48px;
  object-fit: contain;
  margin-bottom: 4px;
}


.block-stat {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 12px;
  line-height: 1;
}


.block-stat-icon {
  width: 14px;
  height: 14px;
}


.stat-label {
  font-weight: 500;
}

.stat-value {
  font-weight: bold;
  color: #333;
  white-space: nowrap;
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
  background-color:rgba(228, 109, 4, 0.76);
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
