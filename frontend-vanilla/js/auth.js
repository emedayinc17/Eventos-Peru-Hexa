// js/auth.js
import { setToken, IAM } from "./api.js";

const KEY_TOKEN = "iam_token";

export const Auth = {
  token: null,
  _user: null,

  get isAuthenticated() {
    return !!this.token;
  },

  get user() {
    return this._user;
  },

  async init() {
    const stored = sessionStorage.getItem(KEY_TOKEN);
    if (!stored) {
      this.token = null;
      this._user = null;
      setToken(null);
      return null;
    }
    this.token = stored;
    setToken(stored);
    try {
      const me = await IAM.me();
      this._user = me;
      return me;
    } catch (err) {
      console.error("Auth.init: error al obtener /me, limpiando sesión", err);
      this.logout();
      return null;
    }
  },

  async login(email, password) {
    let data;
    try {
      data = await IAM.login(email, password);
    } catch (err) {
      console.error('Auth.login: fallo en IAM.login', err);
      throw err;
    }

    console.log('Auth.login: respuesta raw:', data);

    const token = data?.access_token ?? data?.accessToken ?? data?.token ?? data?.access_token_value;
    if (!data || !token) {
      const dump = typeof data === 'object' ? JSON.stringify(data) : String(data);
      throw new Error(`Respuesta de login inválida: ${dump}`);
    }
    this.token = token;
    sessionStorage.setItem(KEY_TOKEN, data.access_token);
    setToken(this.token);
    // Traemos el perfil real del usuario
    const me = await this.me();
    return me;
  },

  async me() {
    if (!this.token) return null;
    const me = await IAM.me();
    this._user = me;
    return me;
  },

  logout() {
    this.token = null;
    this._user = null;
    sessionStorage.removeItem(KEY_TOKEN);
    setToken(null);
  }
};
