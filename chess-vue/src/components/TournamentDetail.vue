<template>
  <div class="container mt-4">
    <h2 class="mb-4">Torneo: {{ tournamentName }}</h2>

    <div class="accordion" id="tournamentAccordion">

      <!-- Ranking -->
      <div class="accordion-item">
        <h2 class="accordion-header" id="headingRanking">
          <button
            class="accordion-button"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#collapseRanking"
            aria-expanded="true"
            aria-controls="collapseRanking"
          >
            Clasificación de Jugadores
          </button>
        </h2>
        <div
          id="collapseRanking"
          class="accordion-collapse collapse show"
          aria-labelledby="headingRanking"
          data-bs-parent="#tournamentAccordion"
        >
          <div class="accordion-body">
            <table class="table table-striped">
                <thead>
                    <tr>
                    <th>Rank</th>
                    <th>Nombre</th>
                    <th>Puntos</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="player in ranking" :key="player.id">
                    <td>{{ player.rank }}</td>
                    <td>{{ player.name }}</td>
                    <td>{{ player.score }}</td>
                    </tr>
                </tbody>
                </table>
          </div>
        </div>
      </div>

    <!-- Rondas y juegos -->
    <div class="accordion-item">
    <h2 class="accordion-header" id="headingRounds">
        <button
        class="accordion-button collapsed"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#collapseRounds"
        aria-expanded="false"
        aria-controls="collapseRounds"
        >
        Rondas y Partidas
        </button>
    </h2>
    <div
        id="collapseRounds"
        class="accordion-collapse collapse"
        aria-labelledby="headingRounds"
        data-bs-parent="#tournamentAccordion"
    >
        <div class="accordion-body">
        <div
            v-for="(round, index) in rounds"
            :key="index"
            class="mb-4 border p-3 rounded"
        >
            <h5 class="mb-3"> {{ round.round_number }}</h5>
            <ul class="list-group">
            <li
                v-for="game in round.games"
                :key="game.id"
                class="list-group-item d-flex justify-content-between align-items-center"
            >
                {{ game.white }} vs {{ game.black }}
                <span>
                <template v-if="game.result !== '*'">
                    Resultado: {{ game.result }}
                </template>
                <template v-else-if="boardType === 'OTB'">
                    <input
                    v-model="game.new_result"
                    placeholder="w/b/="
                    class="form-control d-inline-block w-auto me-2"
                    />
                    <button
                    @click="submitResult(game)"
                    class="btn btn-sm btn-primary"
                    >
                    Guardar
                    </button>
                </template>
                <template v-else>
                    <em>Esperando resultado</em>
                </template>
                </span>
            </li>
            </ul>
        </div>
        </div>
    </div>
    </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTokenStore } from '@/stores/token'

const route = useRoute()
const token = useTokenStore()
const tournamentId = route.params.tournament_id

const tournamentName = ref('')
const ranking = ref([])
const boardType = ref('')

const rounds = ref([])
const loading = ref(true)

const userName = ref("");
const userEmail = ref("");

const fetchRounds = async () => {
  loading.value = true
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/v1/get_round_results/${tournamentId}/`)
    if (!res.ok) throw new Error('Error al obtener las rondas')
    const data = await res.json()
    rounds.value = data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const fetchTournamentData = async () => {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/v1/tournament/${tournamentId}/`, {
      headers: {
        Authorization: `Token ${token.getToken()}`,
      }
    })
    const tournament = await res.json();
    tournamentName.value = tournament.name || `#${tournamentId}`
    boardType.value = tournament.board_type
    
    const rankingRes = await fetch(`http://127.0.0.1:8000/api/v1/get_ranking/${tournamentId}/`, {
      headers: {
        Authorization: `Token ${token.getToken()}`,
      }
    })
    if (!rankingRes.ok) throw new Error('Error al obtener ranking')
    const rawRanking = await rankingRes.json()
    const playersArray = Object.values(rawRanking)
    const sortedPlayers = playersArray.sort((a, b) => a.rank - b.rank)
    ranking.value = sortedPlayers
    
  } catch (err) {
    console.error('Error al cargar datos del torneo:', err)
  }
}

const getCurrentUser = async () => {
  const res = await fetch("http://127.0.0.1:8000/api/v1/current_user/", {
    method: "GET",
    headers: {
      Authorization: `Token ${token.getToken()}`,
    },
  });

  if (res.ok) {
    const data = await res.json();
    userName.value = data.name;
    userEmail.value = data.email;
    console.log(userName, userEmail)
  } else {
    console.warn("No se pudo obtener el usuario actual");
  }
}

const submitResult = async (game) => {
  try {
    if (boardType.value === "OTB") {
      const payload = {
        game_id: game.id,
        name: userName.value,
        email: userEmail.value,
        otb_result: game.new_result,
      };
      const res = await fetch("http://127.0.0.1:8000/api/v1/update_otb_game/", {
        method: "POST",
        headers: { Authorization: `Token ${token.getToken()}`, "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (data.result) {
        alert("Resultado guardado correctamente");
        game.result = game.new_result;
      } else {
        alert(`Error: ${data.message}`);
      }

    } else if (boardType === "LIC") {
      if (!game.lichess_game_id) {
        alert("Debes introducir el ID de la partida de Lichess");
        return;
      }

      const payload = {
        game_id: game.id,
        lichess_game_id: game.lichess_game_id,
      };

      const res = await fetch("http://127.0.0.1:8000/api/v1/update_lichess_game/", {
        method: "POST",
        headers: { Authorization: `Token ${token.getToken()}`, "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (data.result) {
        alert("Resultado actualizado desde Lichess");
        game.result = "Actualizado";
      } else {
        alert(`Error: ${data.message}`);
      }
    }
  } catch (err) {
    console.error(err);
    alert("Error al guardar el resultado");
  }
};

onMounted(() => {
  fetchTournamentData(),
  fetchRounds(),
  getCurrentUser()
})
</script>

<style scoped>
input {
  max-width: 100px;
}
</style>
