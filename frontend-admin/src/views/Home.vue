<template>
  <div class="text-gray-800 p-6">
    <div class="max-w-7xl mx-auto text-center">
      <h2
        class="text-3xl font-bold mb-6 tracking-wide border-b border-gray-300 pb-6"
      >
        15 Night Admin Dashboard
      </h2>

      <div v-if="isLoggedIn" class="my-6">
        <div class="mb-8">
          <h2 class="text-2xl font-bold pb-4 text-gray-700">Block Controls</h2>
          <button
            @click="confirmToggleAllBlocks(true)"
            class="border border-emerald-600 text-emerald-600 font-bold px-4 py-2 mr-4 rounded transition-colors duration-200 hover:bg-gray-100 transform hover:scale-105"
          >
            Enable All Blocks
          </button>
          <button
            @click="confirmToggleAllBlocks(false)"
            class="border border-red-600 text-red-600 font-bold px-4 py-2 mr-4 rounded transition-colors duration-200 hover:bg-gray-100 transform hover:scale-105"
          >
            Disable All Blocks
          </button>
          <button
            @click="seedBlocks"
            class="border border-blue-600 text-blue-600 font-bold px-4 py-2 rounded transition-colors duration-200 hover:bg-gray-100 transform hover:scale-105"
          >
            Seed Blocks
          </button>
        </div>

        <div class="mb-8">
          <h2 class="text-2xl font-bold pb-4 text-gray-700">Block Overview</h2>
          <div
            class="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            <div
              v-for="block in blocks"
              :key="block.id"
              class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
            >
              <h3 class="text-xl font-semibold mb-2">{{ block.name }}</h3>
              <div class="space-y-2">
                <div class="flex justify-between items-center text-sm">
                  <span class="text-gray-600">Status:</span>
                  <span
                    :class="block.enabled ? 'text-green-600' : 'text-red-600'"
                  >
                    {{ block.enabled ? "Enabled" : "Disabled" }}
                  </span>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span class="text-gray-600">Health:</span>
                  <span>{{ block.health }}</span>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span class="text-gray-600">Prize Name:</span>
                  <span>{{ block.prize_name }}</span>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span class="text-gray-600">Prize Chance:</span>
                  <span>{{ block.prize_chance / 100 }}%</span>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span class="text-gray-600">Prize Quantity:</span>
                  <span>{{ block.quantity }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="my-6">
        <p class="mb-4">
          You are not logged in. Please go to the
          <router-link to="/login" class="underline">Login</router-link>
          page.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import { authStore } from "../store/auth";

export default {
  name: "Home",
  setup() {
    const isLoggedIn = computed(() => !!authStore.token);
    const blocks = ref([]);
    const apiBase = import.meta.env.VITE_API_BASE_URL;

    const fetchBlocks = async () => {
      try {
        const response = await axios.get(`${apiBase}/admin/blocks`, {
          headers: {
            Authorization: `Bearer ${authStore.token}`,
          },
        });
        blocks.value = response.data;
      } catch (error) {
        console.error("Failed to fetch blocks", error);
      }
    };

    const toggleAllBlocks = async (enabled) => {
      try {
        await axios.put(
          `${apiBase}/admin/blocks/type/toggle`,
          { enabled },
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
            },
          }
        );
        fetchBlocks();
      } catch (error) {
        console.error("Failed to toggle blocks", error);
        alert("Failed to update blocks status");
      }
    };

    const confirmToggleAllBlocks = (enabled) => {
      const action = enabled ? "enable" : "disable";
      const confirmation = confirm(
        `Are you sure you want to ${action} all blocks?`
      );
      if (confirmation) {
        toggleAllBlocks(enabled);
      }
    };

    const seedBlocks = async () => {
      try {
        const confirmation = confirm(
          "Are you sure you want to seed the blocks?"
        );
        if (!confirmation) return;

        await axios.post(
          `${apiBase}/admin/seed`,
          {},
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
            },
          }
        );
        fetchBlocks();
        alert("Blocks have been successfully seeded.");
      } catch (error) {
        console.error("Failed to seed blocks", error);
        alert("Failed to seed blocks");
      }
    };

    onMounted(() => {
      if (isLoggedIn.value) {
        fetchBlocks();
      }
    });

    return {
      isLoggedIn,
      blocks,
      confirmToggleAllBlocks,
      seedBlocks,
    };
  },
};
</script>

<style scoped></style>
