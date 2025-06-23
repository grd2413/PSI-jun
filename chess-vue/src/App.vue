<template>
  <div>
    <header class="app-header">
      <div class="header-left">
        <nav class="nav-links">
          <RouterLink to="/">Home</RouterLink>
          <RouterLink data-cy=login-cypress-test v-if="!token.isAuthenticated()" to="/login">Admin Log-In</RouterLink>
          <RouterLink to="/faq">FAQ</RouterLink>
          <div>
            <button @click="logout" data-cy="logout-cypress-test" class="btn btn-outline-danger">
              Log-Out
            </button>
          </div>
        </nav>
      </div>
    </header>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from "vue-router";
import { useTokenStore } from "@/stores/token";
import { useRouter } from "vue-router";
import { ref, computed } from "vue";

const router = useRouter();
const token = useTokenStore();

const logout = async () => {
    token.clearToken();
    router.push({ name: 'logout' });
};
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: var(--color-bg, #333);
  color: var(--color-white, #fff);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  padding: 1rem 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-links a {
  color: var(--color-white, #fff);
  text-decoration: none;
  font-weight: 500;
  font-size: 1.1rem;
  padding-bottom: 0.25rem;
}

.nav-links a.router-link-exact-active {
  border-bottom: 2px solid var(--color-primary, #42b983);
}

.logout-button {
  margin-left: auto;
  padding: 0.4rem 1rem;
  font-size: 1rem;
}
.main-content {
  padding-top: 90px;
}
</style>
