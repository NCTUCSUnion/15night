<template>
    <div v-if="isVisible" class="popup-container">
        <h2>你挖到了一個垃圾！哪個選項是正確的垃圾分類呢？</h2>
        <p>{{ hintMessage }}</p>
        <div class="garbage-image">
            <img :src="garbageImage" alt="Garbage image" />
        </div>
        <!-- <div v-else class="loading">Loading image...</div> -->
        <div class="garbage-grid">
            <div class="garbage-row">
                <div class="garbage-card" @click="checkAnswer(1)">
                    <img src="/garbage/icon/1.jpg" alt="Trash" />
                    <p>一般垃圾 (Trash)</p>
                </div>
                <div class="garbage-card" @click="checkAnswer(2)">
                    <img src="/garbage/icon/2.jpg" alt="Plastic" />
                    <p>塑膠類 (Plastic)</p>
                </div>
                <div class="garbage-card" @click="checkAnswer(3)">
                    <img src="/garbage/icon/3.jpg" alt="Paper" />
                    <p>紙類 (Paper)</p>
                </div>
            </div>
            <div class="garbage-row">
                <div class="garbage-card" @click="checkAnswer(4)">
                    <img src="/garbage/icon/4.jpg" alt="Metal" />
                    <p>金屬類 (Metal)</p>
                </div>
                <div class="garbage-card" @click="checkAnswer(5)">
                    <img src="/garbage/icon/5.jpg" alt="Glass" />
                    <p>玻璃類 (Glass)</p>
                </div>
                <div class="garbage-card" @click="checkAnswer(6)">
                    <img src="/garbage/icon/6.jpg" alt="Food Waste" />
                    <p>廚餘 (Food Waste)</p>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { ref, onMounted } from 'vue';

export default {
    name: 'GarbageHintPopup',
    emits: ['close'],
    props: {
        message: {
            type: String,
            default: '請選擇正確的垃圾分類'
        }
    },
    setup(props, { emit }) {
        const isVisible = ref(true);
        const hintMessage = ref(props.message);
        const garbageType = ref(0);
        const garbageImage = ref('');
        
        // Map of garbage types to their folder names
        const garbageTypeFolders = {
            1: 'trash',
            2: 'plastic',
            3: 'paper',
            4: 'metal', 
            5: 'glass',
            6: 'food_waste'
        };

        onMounted(() => {
            // Generate random number between 1-6 for garbage type
            garbageType.value = Math.floor(Math.random() * 6) + 1;
            
            // Generate random number between 1-4 for image
            const randomImageNumber = Math.floor(Math.random() * 4) + 1;
            
            // Get folder name for the selected type
            const folderName = garbageTypeFolders[garbageType.value];
            
            // Set image path using public folder
            garbageImage.value = `/garbage/${folderName}/${randomImageNumber}.jpg`;
            
            console.log(`Garbage Type: ${garbageType.value}, Image Path: ${garbageImage.value}`);
        });

        function closePopup() {
            isVisible.value = false;
            emit('close');
        }            

        function checkAnswer(selectedType) {
            if (selectedType === garbageType.value) {
                // If the answer is correct, close the popup
                closePopup();
            } else {
                // Optional: provide feedback for incorrect answers
                hintMessage.value = `That's not correct. Try again!`;
            }
        }
        
        return {
            isVisible,
            hintMessage,
            garbageImage,
            closePopup,
            checkAnswer,
        };
    },
}
</script>
<style scoped>
.garbage-image {
    margin-top: 1rem;
    text-align: center;
}

.garbage-image img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
}

.garbage-type-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;
    margin-bottom: 1rem;
}

.garbage-type-button {
    padding: 6px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: #f5f5f5;
    cursor: pointer;
}

.garbage-type-button:hover {
    background-color: #e0e0e0;
}

.garbage-grid {
    margin: 1.5rem 0;
}

.garbage-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.garbage-card {
    width: 22%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    background-color: white;
}

.garbage-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.garbage-card img {
    width: 100%;
    height: auto;
    border-radius: 4px;
}

.garbage-card p {
    margin-top: 6px;
    text-align: center;
    font-size: 12px;
}
</style>
