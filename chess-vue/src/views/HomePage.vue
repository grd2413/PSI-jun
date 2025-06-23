<template>
  <div class="home-page">

    <div v-if="isAuthenticated" class="create-tournament-container">
      <button @click="goToCreateTournament" class="btn btn-success">
        Crear Torneo
      </button>
    </div>

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
        {{ tournament.name }}
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
    const res = await fetch('http://localhost:8000/api/v1/searchTournaments/');
    const data = await res.json();

    if (Array.isArray(data)) {
      tournaments.value = data;
      filteredTournaments.value = data;
    } else {
      console.error('Error: la respuesta no es un array:', data);
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



<!-- <template>
  <div id="home-page" class="container">
    <div class="row">
      <h1>Tournaments</h1>
      <TournamentTable :tournaments="tournaments" :paginated="true" />
    </div>
    <div>
      <h2>Search</h2>
      <TournamentSearch :token="token.getToken()" />
    </div>
  </div>

  <div class="row" v-if="userRole === 'admin'">
    <h2>Create tournament</h2>
    <CreateTournament
      :pairingSystems="pairingSystems"
      :boardTypes="boardTypes"
      :rankingMethods="rankingMethods"
      :token="token.getToken()"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useTokenStore } from "@/stores/token";

const token = useTokenStore();

const tournaments = ref([]);
const pairingSystems = ref([]);
const boardTypes = ref([]);
const rankingMethods = ref([]);

// Aquí puedes definir userRole si lo manejas con el token o backend
const userRole = ref("admin"); // o "player"

onMounted(() => {
  fetchTournaments();
  fetchModelData();
});

const fetchTournaments = async () => {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/v1/tournaments/", {
      headers: {
        Authorization: `Token ${token.getToken()}`,
      },
    });

    if (!response.ok) {
      console.error("Error al cargar torneos:", response.status);
      return;
    }

    const result = await response.json();
    tournaments.value = result;
  } catch (error) {
    console.error("Error en fetchTournaments:", error);
  }
};

const fetchModelData = async () => {
  const [psRes, btRes, rmRes] = await Promise.all([
    fetch("http://127.0.0.1:8001/api/v1/models/pairing-systems/", {
      headers: { Authorization: `Token ${token.getToken()}` },
    }),
    fetch("http://127.0.0.1:8001/api/v1/models/board-types/", {
      headers: { Authorization: `Token ${token.getToken()}` },
    }),
    fetch("http://127.0.0.1:8001/api/v1/models/ranking-methods/", {
      headers: { Authorization: `Token ${token.getToken()}` },
    }),
  ]);

  pairingSystems.value = await psRes.json();
  boardTypes.value = await btRes.json();
  rankingMethods.value = await rmRes.json();
};
</script> -->
