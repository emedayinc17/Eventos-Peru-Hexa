// js/auth.js
import { setToken, IAM } from "./api.js";

/**
 * Módulo de autenticación.
 * - Gestiona el token en sessionStorage.
 * - Expone init/login/logout/me para el resto de la app.
 */
export const Auth = {
  get token() {
    return sessionStorage.getItem("token");
  },
  set token(v) {
    if (v) sessionStorage.setItem("token", v);
    else sessionStorage.removeItem("token");
  },

  /**
   * Inicializa el estado de autenticación al arrancar la app.
   * Si hay token almacenado intenta recuperar el perfil con /me.
   */
  async init() {
    const t = this.token;
    setToken(t);
    if (!t) return null;
    try {
      return await this.me();
    } catch {
      // Token inválido/expirado -> limpiamos estado local
      this.logout();
      return null;
    }
  },

  /**
   * Login de usuario:
   * 1. Llama a /auth/login y guarda el access_token.
   * 2. Llama a /me para obtener el perfil completo.
   * 3. Devuelve el usuario (perfil) para que la UI lo use.
   */
  async login(email, password) {
    const data = await IAM.login(email, password);
    if (!data || !data.access_token) {
      throw new Error("Respuesta de login inválida");
    }
    this.token = data.access_token;
    setToken(data.access_token);
    // Inmediatamente traemos el perfil para conocer rol, estado, etc.
    const user = await this.me();
    return user;
  },

  logout() {
    this.token = null;
    setToken(null);
  },

  async me() {
    return IAM.me();
  }
};
