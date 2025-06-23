<template>
  <form @submit.prevent="submitForm" class="form-container">
    <input v-model="form.name" placeholder="Tournament name" required />

    <label>
      <input type="checkbox" v-model="form.onlyAdminUpdate" />
      Only administrator can update games
    </label>

    <select v-model="form.tournament_type">
      <option disabled value="">Select pairing system</option>
      <option v-for="ps in tournament_types" :key="ps" :value="ps">{{ ps }}</option>
    </select>

    <select v-model="form.boardType">
      <option disabled value="">Select board type</option>
      <option v-for="bt in boardTypes" :key="bt" :value="bt">{{ bt }}</option>
    </select>

    <div>
      <label>wins <input type="number" step="0.1" v-model.number="form.points.win" /></label>
      <label>draws <input type="number" step="0.1" v-model.number="form.points.draw" /></label>
      <label>losses <input type="number" step="0.1" v-model.number="form.points.loss" /></label>
    </div>

    <div>
      <label v-for="rm in rankingMethods" :key="rm">
        <input type="checkbox" :value="rm" v-model="form.rankings" />
        {{ rm }}
      </label>
    </div>

    <div class="players-section">
      <h3>Jugadores</h3>
      <input
        v-model="playerInput"
        placeholder="Introduce username del jugador"
      />
      <button type="button" @click="addPlayer">Añadir</button>

      <ul>
        <li v-for="(player, index) in form.players" :key="index">
          {{ player }}
          <button type="button" @click="removePlayer(index)">Eliminar</button>
        </li>
      </ul>
    </div>

    <button type="submit">Create tournament</button>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useTokenStore } from '@/stores/token'

const token = useTokenStore()

const playerInput = ref('')

const tournament_types = ['SWISS', 'ROUNDROBIN']
const boardTypes = ['LIC', 'OTB']
const rankingMethods = ['pseudobuchholz', 'buchholz', 'cumulative', 'wins']

const form = ref({
  name: '',
  onlyAdminUpdate: false,
  tournament_type: '',
  boardType: '',
  points: {
    win: 1,
    draw: 0.5,
    loss: 0
  },
  rankings: [],
  players: [],
})

const submitForm = async () => {
  let players_text = '';
  if (form.value.board_type == 'LIC'){
    players_text = 'lichess_username';
  }
  players_text += form.value.players.join('\n');
  
  const payload = {
    name: form.value.name,
    only_admin_can_update: form.value.onlyAdminUpdate,
    tournament_type: form.value.tournament_type,
    board_type: form.value.boardType,
    points: {
      win: form.value.points.win,
      draw: form.value.points.draw,
      loss: form.value.points.loss,
    },
    ranking_methods: form.value.rankings,
    players: players_text
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/tournaments/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${token.getToken()}`,
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const errorData = await response.json()
      console.error(errorData)
      throw new Error('Error al crear el torneo')
    }

    alert('Torneo creado exitosamente')
    router.push({ name: "home" });
  } catch (error) {
    console.error(error)
    alert(error.message || 'Fallo al crear el torneo')
  }
}

const addPlayer = () => {
  const username = playerInput.value.trim()
  if (username && !form.value.players.includes(username)) {
    form.value.players.push(username)
    playerInput.value = ''
  }
}

const removePlayer = (index) => {
  form.value.players.splice(index, 1)
}

</script>

<style scoped>
.form-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 500px;
  margin: auto;
}
</style>
