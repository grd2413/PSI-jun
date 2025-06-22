<template>
    <form @submit.prevent="submitForm">
      <input v-model="form.name" placeholder="Tournament name" required />
      <label><input type="checkbox" v-model="form.onlyAdminUpdate" /> Only administrator can update games</label>
      
      <select v-model="form.pairingSystem">
        <option v-for="ps in pairingSystems" :value="ps">{{ ps }}</option>
      </select>
      
      <select v-model="form.boardType">
        <option v-for="bt in boardTypes" :value="bt">{{ bt }}</option>
      </select>
      
      <div>
        <label>wins<input type="number" step="0.1" v-model.number="form.points.win" /></label>
        <label>draws<input type="number" step="0.1" v-model.number="form.points.draw" /></label>
        <label>loses<input type="number" step="0.1" v-model.number="form.points.loss" /></label>
      </div>
  
      <div>
        <label v-for="rm in rankingMethods" :key="rm">
          <input type="checkbox" :value="rm" v-model="form.rankings" /> {{ rm }}
        </label>
      </div>
  
      <button type="submit">Create tournamet</button>
    </form>
  </template>
  
<script setup>
import { useTokenStore } from '@/stores/token'

const token = useTokenStore()
const props = defineProps(["token"]);

const submitForm = async () => {
  const payload = {
    name: form.value.name,
    only_admin_can_update: form.value.onlyAdminUpdate,
    pairing_system: form.value.pairingSystem,
    board_type: form.value.boardType,
    points: {
      win: form.value.points.win,
      draw: form.value.points.draw,
      loss: form.value.points.loss,
    },
    ranking_methods: form.value.rankings,
  }

  try {
    console.log("Token:", token.getToken());
    const response = await fetch('http://127.0.0.1:8001/api/v1/tournaments/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Token ${token.getToken()}`,
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error('Error al crear el torneo')
    }

    alert('Torneo creado exitosamente')
  } catch (error) {
    console.error(error)
    alert('Fallo al crear el torneo')
  }
}
</script>
  