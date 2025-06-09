<template>
  <h1>Login</h1>

  <div id="login-form">
    <form @submit.prevent="sendLoginForm">
      <div class="row mb-2 formContainer">
        <div class="col-12">
          <div class="form">
            <input
              ref="user"
              v-model="username"
              type="text"
              class="form-control"
              data-cy="user"
              :class="{ 'is-invalid': procesando && invalidUser }"
              @focus="resetEstado"
              placeholder="User"
              @keypress="resetEstado"
            />
          </div>
        </div>
      </div>

      <div class="row mb-2 formContainer">
        <div class="col-12">
          <div class="form">
            <input
              v-model="password"
              type="password"
              placeholder="Password"
              class="form-control"
              data-cy="password"
              :class="{ 'is-invalid': procesando && invalidPassword }"
              @focus="resetEstado"
            />
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-md-4 mt-4">
          <div class="form-group">
            <button class="btn btn-primary" data-cy="add-button">Login</button>
          </div>
        </div>
      </div>

      <br />
      <div class="container">
        <div class="row">
          <div class="col-md-12">
            <div
              v-if="error && procesando"
              class="alert alert-danger"
              role="alert"
            >
              Debes rellenar todos los campos!
            </div>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useTokenStore } from "@/stores/token";
import { useRouter } from "vue-router";

const router = useRouter();
const token = useTokenStore();

defineOptions({
  user: "LoginForm",
});

const procesando = ref(false);
const correcto = ref(false);
const error = ref(false);

const username = ref("");
const password = ref("");
const invalidUser = computed(() => username.value.length < 1);
const invalidPassword = computed(() => password.value.length < 1);

//const user = ref(null);

//const emit = defineEmits(["login-admin"]);

const sendLoginForm = async () => {
  procesando.value = true;
  correcto.value = false;
  error.value = false;

  if (invalidUser.value || invalidPassword.value) {
    error.value = true;
    return;
  }

  try {
    const admin = {
      username: username.value,
      password: password.value,
    };
    console.log("Sending login form..." + admin.username);
    console.log("Sending login form..." + admin.password);
    const response = await fetch("http://127.0.0.1:8001/api/v1/token/login", {
      method: "POST",
      body: JSON.stringify(admin),
      headers: { "Content-type": "application/json; charset=UTF-8" },
    });

    const result = await response.json();
    token.setToken(result.auth_token);
    console.log("Token: " + token.getToken());

    console.log(result);

    error.value = false;
    correcto.value = true;
    procesando.value = false;
  } catch (error) {
    console.error(error);
  }

  router.push({ name: "home" });
};
</script>

<style scoped>
form {
  width: 250px;
}
</style>
