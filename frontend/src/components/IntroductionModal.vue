<template>
  <div class="modal-overlay" @click.self="close">
    <div class="intro-container">
      <div class="intro-header">
        <h2>歡迎來到資工之夜小遊戲</h2>
      </div>
      
      <div class="intro-content">
        <p>
        點擊螢幕中央的方塊開始挖掘，賺取金錢並升級工具，提升效率！</p>
        
        <p>🌱 <strong>遊戲驚喜</strong><br>
        挖到垃圾－分類正確就能繼續挖<br>
        挖到獎品－中場與終場可到舞台旁找系學會工作人員兌換</p>
        
        <p><strong>展開你的環保挖寶之旅吧！</strong></p>
      </div>
      
      <div class="intro-footer">
        <button class="start-btn" @click="close">START!</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IntroductionModal',
  emits: ['close'],
  
  setup(props, { emit }) {
    const close = () => {
      // Mark as seen in localStorage so it doesn't show again on refresh
      localStorage.setItem('introSeen', 'true');
      emit('close');
    };
    
    return { close };
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.intro-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
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

.intro-header {
  display: flex;
  text-align: center;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.intro-header h2 {
  margin: 0;
  color: #333;
  font-size: 22px;
}

.intro-content {
  margin-bottom: 20px;
  line-height: 1.6;
  text-align: left;
}

.intro-content p {
  margin-bottom: 16px;
}

.intro-footer {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.start-btn {
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

</style>
