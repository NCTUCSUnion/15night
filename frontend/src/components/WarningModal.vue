<template>
  <div class="modal-backdrop">
    <div class="modal">
      <div class="modal-content">
        <h3>Warning</h3>
        <p>{{ message }}</p>
        <div class="actions">
          <button @click="$emit('close')" class="close-btn">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WarningModal',
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
  max-width: 80%;
  width: 300px;
  padding: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  color: #dc3545;
  margin-top: 0;
  font-size: 18px;
}

.modal-content p {
  margin: 15px 0;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.close-btn {
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
