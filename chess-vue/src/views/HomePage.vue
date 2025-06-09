<template>
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
    <TournamentForm
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
    const response = await fetch("http://127.0.0.1:8001/api/v1/tournament/", {
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
</script>


