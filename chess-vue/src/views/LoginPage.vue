<template>
  <div id="login-form">
    <form @submit.prevent="sendLoginForm">
      <h1>Login</h1>
      <div class="row mb-2 formContainer">
        <div class="col-12">
          <div class="form">
            <input
              ref="user"
              v-model="username"
              type="text"
              class="form-control"
              data-cy="username"
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
            <button class="btn btn-primary" data-cy="login-button">Login</button>
          </div>
        </div>
      </div>

      <br />
      <div class="container">
        <div class="row">
          <div class="col-md-12">
            <div
              v-if="error"
              class="alert alert-danger"
              role="alert"
              data-cy="error-message"
            >
              {{ errorMessage }}
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
const errorMessage = ref("");

const username = ref("");
const password = ref("");
const invalidUser = computed(() => username.value.length < 1);
const invalidPassword = computed(() => password.value.length < 1);

// const sendLoginForm = async () => {
//   procesando.value = true;
//   correcto.value = false;
//   error.value = false;

//   if (invalidUser.value || invalidPassword.value) {
//     error.value = true;
//     return;
//   }
//   try {
//     const admin = {
//       username: username.value,
//       password: password.value,
//     };

//     const response = await fetch("http://127.0.0.1:8000/api/v1/token/login/", {
//       method: "POST",
//       body: JSON.stringify(admin),
//       headers: { "Content-type": "application/json; charset=UTF-8" },
//     });

//     if (!response.ok) {
//       throw new Error("Credenciales incorrectas");
//     }

//     const result = await response.json();
//     print(result)
//     token.setToken(result.auth_token);
//     procesando.value = false;
//     correcto.value = true;
//     router.push({ name: "home" });

//   } catch (err) {
//     console.error(err);
//     error.value = true;
//     procesando.value = false;
//   }
  
// };
const sendLoginForm = async () => {
    procesando.value = true;
    correcto.value = false;
    error.value = false;
    errorMessage.value = "";

    if (invalidUser.value || invalidPassword.value) {
      error.value = true;
      errorMessage.value = "Debes rellenar todos los campos";
      return;
    }

    try {
      const admin = {
        username: username.value,
        password: password.value,
      };

      const response = await fetch("http://localhost:8000/api/v1/token/login", {
        method: "POST",
        body: JSON.stringify(admin),
        headers: {
          "Content-type": "application/json; charset=UTF-8",
        },
      });

      if (!response.ok) {
        throw new Error("Error: Invalid username or password");
      }

      const result = await response.json();
      token.setToken(result.auth_token);
      router.push({ name: "home" });
    } catch (err) {
      console.error(err);
      error.value = true;
      errorMessage.value = err.message || "Error desconocido.";
    } finally {
      procesando.value = false;
    }
};
</script>

<!-- <style scoped>
form {
  width: 250px;
}
</style> -->

<style scoped>
.h1 {
  align-items: center;
}

#login-form {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 25vh;
}


/* Formulario con ancho fijo y fondo suave */
form {
  width: 500px;
  padding: 4rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  align-items: center;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

/* Espaciado entre campos */
.formContainer {
  margin-bottom: 1.2rem;
}

/* Input con borde, padding y tamaño cómodo */
input.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

/* Estilo para inputs inválidos */
input.is-invalid {
  border-color: #dc3545;
  background-color: #f8d7da;
}

/* Botón principal */
button.btn-primary {
  width: 100%;
  padding: 0.6rem;
  font-size: 1.1rem;
  border-radius: 4px;
}

/* Mensaje de error */
.alert-danger {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  text-align: center;
}
</style>
