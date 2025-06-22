import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1'; // cambia si tu Django está en otro puerto

// Añade el token si usas autenticación
const token = localStorage.getItem('token'); // asegúrate de guardar el token al hacer login
const headers = token ? { Authorization: `Token ${token}` } : {};

export const createTournament = (tournamentData) => {
  return axios.post(`${API_URL}/tournaments/`, tournamentData, { headers });
};