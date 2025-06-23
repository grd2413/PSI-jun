<template>
  <div class="home-page">

    <div v-if="isAuthenticated" class="create-tournament-container">
       <RouterLink to="/createtournament" class="btn btn-success" data-cy="create-tournament-button">
        Crear Torneo
      </RouterLink>
    </div>
    <br/>
    <br/>
    <br/>

    <h1>Torneos disponibles</h1>

    <input
      type="text"
      v-model="searchTerm"
      placeholder="Buscar torneo..."
      @input="filterTournaments"
      class="form-control mb-3"
      data-cy="search-input"
    />

    <ul class="list-group">
      <li
        v-for="tournament in pagedTournaments"
        :key="tournament.id"
        class="list-group-item"
        data-cy="tournament-item"
      >
      <RouterLink :to="`/tournamentdetail/${tournament.id}`">{{ tournament.name }}</RouterLink>
      </li>
    </ul>

    <nav v-if="totalPages > 1" aria-label="Paginación torneos" class="mt-3">
      <ul class="pagination justify-content-center">
        <li
          class="page-item"
          :class="{ disabled: currentPage === 1 }"
          @click="changePage(currentPage - 1)"
        >
          <a class="page-link" href="#">Anterior</a>
        </li>

        <li
          v-for="page in totalPages"
          :key="page"
          class="page-item"
          :class="{ active: currentPage === page }"
          @click="changePage(page)"
        >
          <a class="page-link" href="#">{{ page }}</a>
        </li>

        <li
          class="page-item"
          :class="{ disabled: currentPage === totalPages }"
          @click="changePage(currentPage + 1)"
        >
          <a class="page-link" href="#">Siguiente</a>
        </li>
      </ul>
    </nav>
  </div>
  <footer class="app-footer">
      <div class="footer-content">
        <p>© 2025 Diego Grande Camarero. Todos los derechos reservados.</p>
      </div>
  </footer>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useTokenStore } from "@/stores/token";
import { useRouter } from "vue-router";

const router = useRouter();
const token = useTokenStore();

const tournaments = ref([]);
const filteredTournaments = ref([]);
const searchTerm = ref('');
const currentPage = ref(1);
const itemsPerPage = 10;

const isAuthenticated = token.isAuthenticated(); 

const fetchTournaments = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/v1/tournaments/');
    const data = await res.json();

    if (Array.isArray(data.results)) {
      tournaments.value = data.results;
      filteredTournaments.value = data.results;
    } else {
      console.error('Error: data.results no es un array:', data);
      tournaments.value = [];
      filteredTournaments.value = [];
    }
  } catch (error) {
    console.error('Error fetching tournaments:', error);
    tournaments.value = [];
    filteredTournaments.value = [];
  }
};

const filterTournaments = () => {
  const term = searchTerm.value.toLowerCase();
  filteredTournaments.value = tournaments.value.filter(t =>
    t.name.toLowerCase().includes(term)
  );
  currentPage.value = 1;
};

const totalPages = computed(() =>
  Math.ceil(filteredTournaments.value.length / itemsPerPage)
);

const pagedTournaments = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredTournaments.value.slice(start, start + itemsPerPage);
});

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
};

onMounted(() => {
  fetchTournaments();
});
</script>

<style scoped>
.home-page {
  max-width: 600px;
  margin: 2rem auto;
}
.list-group-item {
  cursor: pointer;
}
.pagination li {
  cursor: pointer;
}
</style>
