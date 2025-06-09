// stores/auth.js
import { defineStore } from "pinia";
import { ref } from "vue";

export const useTokenStore = defineStore("auth", () => {
  const token = ref(null);

  function setToken(newToken) {
    token.value = newToken;
    localStorage.setItem("auth_token", newToken);
  }

  function getToken() {
    if (!token.value) {
      token.value = localStorage.getItem("auth_token");
    }
    return token?.value;
  }

  function clearToken() {
    token.value = null;
    localStorage.removeItem("auth_token");
  }

  return { token, setToken, getToken, clearToken };
});
