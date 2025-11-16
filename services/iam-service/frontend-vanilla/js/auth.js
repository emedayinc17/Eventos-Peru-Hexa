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
    const data = await IAM.login(email, password);
    if (!data || !data.access_token) {
      throw new Error("Respuesta de login inválida");
    }
    this.token = data.access_token;
    sessionStorage.setItem(KEY_TOKEN, data.access_token);
    setToken(data.access_token);
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
