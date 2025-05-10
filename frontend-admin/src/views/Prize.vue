<template>
  <div class="text-gray-800 p-6">
    <div class="max-w-7xl mx-auto text-center">
      <h2
        class="text-3xl font-bold mb-6 tracking-wide border-b border-gray-300 pb-6"
      >
        Prizes Overview
      </h2>
      <div class="max-w-4xl mx-auto my-6">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by Student ID or Prize Name"
          class="w-full px-4 py-2 border rounded-lg shadow-sm border-gray-300 focus:outline-none"
        />
      </div>
      <div class="max-w-4xl mx-auto my-6 overflow-x-auto rounded-lg shadow-md">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-100">
            <tr>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                ID
              </th>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                Student ID
              </th>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                Prize Name
              </th>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="prize in filteredPrizes"
              :key="prize.id"
              class="hover:bg-gray-50 transition-colors duration-200"
            >
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm font-medium text-gray-900">{{
                  prize.id
                }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm text-gray-900">{{
                  prize.student_id
                }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm text-gray-900">{{
                  prize.prize_name
                }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    prize.claimed
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800',
                  ]"
                >
                  {{ prize.claimed ? "Claimed" : "Unclaimed" }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <button
                  @click="handleTogglePrizeStatus(prize.id, prize.claimed)"
                  :class="[
                    'px-3 py-1 rounded text-sm',
                    prize.claimed
                      ? 'outline outline-yellow-500 text-yellow-600 hover:bg-yellow-100'
                      : 'outline outline-green-500 text-green-600 hover:bg-green-100',
                  ]"
                >
                  {{ prize.claimed ? "Mark Unclaimed" : "Mark Claimed" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from "vue";
import axios from "axios";
import { authStore } from "../store/auth";

export default {
  name: "Prizes",
  setup() {
    const prizes = ref([]);
    const searchQuery = ref("");
    const apiBase = import.meta.env.VITE_API_BASE_URL;

    const fetchPrizes = async () => {
      try {
        const response = await axios.get(`${apiBase}/admin/prizes`, {
          headers: {
            Authorization: `Bearer ${authStore.token}`,
          },
        });
        prizes.value = response.data.sort((a, b) => a.id - b.id);
      } catch (error) {
        console.error("Failed to fetch prizes", error);
      }
    };

    const togglePrizeStatus = async (prizeId, claimed) => {
      try {
        await axios.put(
          `${apiBase}/admin/prizes/${prizeId}/claim-status`,
          { claimed },
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
            },
          }
        );
        await fetchPrizes();
      } catch (error) {
        console.error("Failed to update prize status", error);
        alert("Failed to update prize status");
      }
    };

    const handleTogglePrizeStatus = (prizeId, claimed) => {
      if (claimed) {
        const confirmUnclaim = confirm(
          "Are you sure you want to mark this prize as unclaimed?"
        );
        if (!confirmUnclaim) {
          return;
        }
      }
      togglePrizeStatus(prizeId, !claimed);
    };

    const filteredPrizes = computed(() => {
      const query = searchQuery.value.toLowerCase();
      return prizes.value.filter(
        (prize) =>
          prize.student_id.toLowerCase().includes(query) ||
          prize.prize_name.toLowerCase().includes(query)
      );
    });

    let intervalId = null;
    onMounted(() => {
      fetchPrizes();
      intervalId = setInterval(fetchPrizes, 5000);
    });

    onUnmounted(() => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    });

    return {
      prizes,
      searchQuery,
      filteredPrizes,
      handleTogglePrizeStatus,
    };
  },
};
</script>
