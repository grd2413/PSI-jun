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

    <button type="submit">Create tournament</button>
  </form>
</template>

<script setup>
import { reactive } from 'vue'
import { useTokenStore } from '@/stores/token'

const token = useTokenStore()

const tournament_types = ['SWISS', 'ROUNDROBIN']
const boardTypes = ['LIC', 'OTB']
const rankingMethods = ['pseudobuchholz', 'buchholz', 'cumulative', 'wins']

const form = reactive({
  name: '',
  onlyAdminUpdate: false,
  tournament_type: '',
  boardType: '',
  points: {
    win: 1,
    draw: 0.5,
    loss: 0
  },
  rankings: []
})

const submitForm = async () => {
  const payload = {
    name: form.name,
    only_admin_can_update: form.onlyAdminUpdate,
    tournament_type: form.tournament_type,
    board_type: form.boardType,
    points: {
      win: form.points.win,
      draw: form.points.draw,
      loss: form.points.loss,
    },
    ranking_methods: form.rankings,
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
  } catch (error) {
    console.error(error)
    alert(error.message || 'Fallo al crear el torneo')
  }
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
