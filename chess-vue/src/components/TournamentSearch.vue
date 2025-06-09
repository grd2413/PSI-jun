<template>
  <div>
    <input v-model="searchQuery" @input="search" placeholder="Search tournaments by name..." />
    <ul>
      <li v-for="t in results" :key="t.id">{{ t.name }} - {{ t.date }}</li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from "vue";
const props = defineProps(["token"]);

const searchQuery = ref("");
const results = ref([]);

const search = async () => {
  if (searchQuery.value.trim().length < 2) {
    results.value = [];
    return;
  }

  const url = `http://127.0.0.1:8001/api/v1/searchTournaments/?name=${encodeURIComponent(searchQuery.value)}`;
  const response = await fetch(url, {
    headers: {
      Authorization: `Token ${props.token}`,
    },
  });

  if (response.ok) {
    results.value = await response.json();
  } else {
    console.error("Error en búsqueda");
  }
};
</script>