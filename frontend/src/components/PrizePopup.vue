<template>
  <div class="modal-backdrop">
    <div class="modal">
      <div class="modal-content">
        <div class="header-row">
          <h3>You get a prize!</h3>
          <button class="close-button" @click="$emit('close')">&times;</button>
        </div>
        <div class="prize-message">
          <p>{{ message }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PrizePopup',
  props: {
    message: {
      type: String,
      required: true
    }
  },
  emits: ['close']
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  max-width: 90%;
  width: 400px;
  padding: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
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

.header-row h3 {
  margin: 0;
  color: #4285f4;
  font-size: 22px;
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
  color: #666;
}

.close-button:hover {
  background-color: #f0f0f0;
}

.prize-message {
  text-align: center;
  font-size: 18px;
  color: #333;
  margin: 15px 0;
}

@media (max-width: 480px) {
  .modal {
    width: 95%;
    padding: 15px;
  }
  
  .prize-message {
    font-size: 16px;
  }
  
  .header-row h3 {
    font-size: 20px;
  }
}
</style>
