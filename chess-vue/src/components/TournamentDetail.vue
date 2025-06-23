<!-- <template>
  <div class="container mt-4">
    <h2 class="mb-4">Torneo: {{ tournamentName }}</h2>

    <h4>Clasificación</h4>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>Posición</th>
          <th>Jugador</th>
          <th>Puntos</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(player, index) in ranking" :key="player.username">
          <td>{{ index + 1 }}</td>
          <td>{{ player.username }}</td>
          <td>{{ player.points }}</td>
        </tr>
      </tbody>
    </table>

    <h4 class="mt-4">Rondas y Partidas</h4>
    <div v-for="(round, index) in rounds" :key="index" class="mb-3">
      <h5>Ronda {{ round.round_number }}</h5>
      <ul class="list-group">
        <li
          v-for="game in round.games"
          :key="game.id"
          class="list-group-item d-flex justify-content-between align-items-center"
        >
          {{ game.white_player }} vs {{ game.black_player }}
          <span>
            <template v-if="game.result">
              Resultado: {{ game.result }}
            </template>
            <template v-else-if="boardType === 'OTB'">
              <input
                v-model="game.new_result"
                placeholder="Ej: 1-0"
                class="form-control d-inline-block w-auto me-2"
              />
              <button @click="submitResult(game)" class="btn btn-primary btn-sm">Guardar</button>
            </template>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTokenStore } from '@/stores/token'

const route = useRoute()
const tokenStore = useTokenStore()
const tournamentId = route.params.tournament_id

const tournamentName = ref('')
const ranking = ref([])
const rounds = ref([])
const boardType = ref('')  // Para saber si se permite actualizar resultado (solo OTB)

const fetchTournamentData = async () => {
  try {
    // Cargar clasificación
    const rankingRes = await fetch(`http://127.0.0.1:8000/api/v1/get_ranking/${tournamentId}/`, {
      headers: {
        Authorization: `Token ${tokenStore.getToken()}`,
      }
    })

    const rankingData = await rankingRes.json()
    ranking.value = rankingData.ranking
    tournamentName.value = rankingData.tournament_name || `#${tournamentId}`
    boardType.value = rankingData.board_type || ''  // si se incluye en la respuesta

    // Cargar rondas y partidas
    const roundsRes = await fetch(`http://127.0.0.1:8000/api/v1/get_round_results/${tournamentId}/`, {
      headers: {
        Authorization: `Token ${tokenStore.getToken()}`,
      }
    })

    const roundsData = await roundsRes.json()
    rounds.value = roundsData.map(round => ({
      ...round,
      games: round.games.map(game => ({
        ...game,
        new_result: ''
      }))
    }))
  } catch (err) {
    console.error('Error al cargar datos del torneo:', err)
    alert('No se pudieron cargar los datos del torneo')
  }
}

const submitResult = async (game) => {
  const payload = {
    game_id: game.id,
    result: game.new_result
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/update_otb_game/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${tokenStore.getToken()}`,
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorData = await response.json()
      console.error(errorData)
      throw new Error('Error al actualizar resultado')
    }

    game.result = game.new_result
    game.new_result = ''
    alert('Resultado guardado correctamente')
  } catch (error) {
    console.error(error)
    alert(error.message || 'Fallo al guardar el resultado')
  }
}

onMounted(() => {
  fetchTournamentData()
})
</script>

<style scoped>
input {
  max-width: 100px;
}
</style> -->

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
                <template v-if="game.result">
                    Resultado: {{ game.result }}
                </template>
                <template v-else-if="boardType === 'OTB'">
                    <input
                    v-model="game.new_result"
                    placeholder="Ej: 1-0"
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
                    <em>Esperando resultado de Lichess</em>
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
const tokenStore = useTokenStore()
const tournamentId = route.params.tournament_id

const tournamentName = ref('')
const ranking = ref([])
const boardType = ref('')

const rounds = ref([])
const loading = ref(true)

const fetchRounds = async () => {
  loading.value = true
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/v1/get_round_results/${tournamentId}/`)
    if (!res.ok) throw new Error('Error al obtener las rondas')
    const data = await res.json()
    rounds.value = data
    console.log(rounds.value)
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
        Authorization: `Token ${tokenStore.getToken()}`,
      }
    })
    const tournament = await res.json();
    tournamentName.value = tournament.name || `#${tournamentId}`
    boardType.value = tournament.board_type
    
    const rankingRes = await fetch(`http://127.0.0.1:8000/api/v1/get_ranking/${tournamentId}/`, {
      headers: {
        Authorization: `Token ${tokenStore.getToken()}`,
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

const submitResult = async (game) => {
  const payload = {
    game_id: game.id,
    result: game.new_result
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/update_otb_game/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${tokenStore.getToken()}`,
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorData = await response.json()
      console.error(errorData)
      throw new Error('Error al actualizar resultado')
    }

    game.result = game.new_result
    game.new_result = ''
    alert('Resultado guardado correctamente')
  } catch (error) {
    console.error(error)
    alert(error.message || 'Fallo al guardar el resultado')
  }
}

onMounted(() => {
  fetchTournamentData(),
  fetchRounds()
})
</script>

<style scoped>
input {
  max-width: 100px;
}
</style>
