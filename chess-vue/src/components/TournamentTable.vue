<template>
  <div>
    <table>
      <thead>
        <tr><th>Name</th><th>Date</th></tr>
      </thead>
      <tbody>
        <tr v-for="t in tournaments" :key="t.id">
          <td><a :href="`/tournaments/${t.id}`">{{ t.name }}</a></td>
          <td>{{ t.date }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="paginated && totalPages > 1">
      <button @click="prevPage" :disabled="currentPage === 1">Prev</button>
      <button @click="nextPage" :disabled="currentPage === totalPages">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

defineProps(['tournaments', 'paginated'])

const currentPage = ref(1)
const perPage = 10

const totalPages = computed(() => Math.ceil(props.tournaments.length / perPage))
const pagedTournaments = computed(() =>
  props.paginated
    ? props.tournaments.slice((currentPage.value - 1) * perPage, currentPage.value * perPage)
    : props.tournaments
)

const nextPage = () => currentPage.value++
const prevPage = () => currentPage.value--
</script>
