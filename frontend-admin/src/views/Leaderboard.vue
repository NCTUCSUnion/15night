<template>
  <div class="text-gray-800 p-6">
    <div class="max-w-7xl mx-auto text-center">
      <h2
        class="text-3xl font-bold mb-6 tracking-wide border-b border-gray-300 pb-6"
      >
        Leaderboard
      </h2>
      <div class="max-w-4xl mx-auto my-6 overflow-x-auto rounded-lg shadow-md">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-100">
            <tr>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                Rank
              </th>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                Student ID
              </th>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                Shovel Level
              </th>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                Money
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="user in leaderboard"
              :key="user.student_id"
              class="hover:bg-gray-50 transition-colors duration-200"
            >
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm font-medium text-gray-900">{{
                  user.rank
                }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm text-gray-900">{{ user.student_id }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm text-gray-900">{{
                  user.shovel_level
                }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm text-gray-900">{{ user.money }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="error" class="text-red-500 mt-4">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import axios from "axios";

export default {
  name: "Leaderboard",
  setup() {
    const leaderboard = ref([]);
    const error = ref(null);
    const apiBase = import.meta.env.VITE_API_BASE_URL;

    const fetchLeaderboard = async () => {
      try {
        const response = await axios.get(`${apiBase}/leaderboard`);
        leaderboard.value = response.data;
        error.value = null;
      } catch (err) {
        error.value = "Failed to fetch leaderboard. Please try again.";
        console.error(err);
      }
    };

    let intervalId = null;
    onMounted(() => {
      fetchLeaderboard();
      intervalId = setInterval(fetchLeaderboard, 5000);
    });

    onUnmounted(() => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    });

    return {
      leaderboard,
      error,
    };
  },
};
</script>

<style scoped></style>
