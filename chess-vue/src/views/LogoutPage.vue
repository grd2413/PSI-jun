<template>
  <div class="logout-container" data-cy="logoutPage">
    <div class="logout-card">
      <h2 class="logout-title">Log Out</h2>
      <p class="logout-text">You are being log out</p>
      <p class="logout-subtext">
        You will be redirected to home in <strong>5 seconds</strong>...
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTokenStore } from '@/stores/token';

const router = useRouter();
const tokenStore = useTokenStore();

onMounted(() => {
  setTimeout(() => {
    router.push({ name: 'home' });
  }, 1500);
});
</script>

<!-- <style scoped>
.logout-message {
  margin: 3rem auto;
  text-align: center;
  font-size: 1.3rem;
}
</style> -->
<style scoped>
.logout-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
  background-color: #f8fafc;
  padding: 2rem;
}

.logout-card {
  background-color: white;
  padding: 2.5rem 3rem;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
  width: 100%;
}

.logout-title {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.logout-text {
  font-size: 1.2rem;
  color: #34495e;
  margin-bottom: 0.5rem;
}

.logout-subtext {
  font-size: 1rem;
  color: #7f8c8d;
}
</style>
