// js/auth.js
import { setToken, IAM } from "./api.js";

export const Auth = {
  get token() { return sessionStorage.getItem("token"); },
  set token(v) { if (v) sessionStorage.setItem("token", v); else sessionStorage.removeItem("token"); },

  async init() {
    const t = this.token;
    setToken(t);
    return t ? await this.me().catch(() => null) : null;
  },

  async login(email, password) {
    const data = await IAM.login(email, password);
    this.token = data.access_token;
    setToken(data.access_token);
    return data.user;
  },

  logout() {
    this.token = null;
    setToken(null);
  },

  async me() {
    return IAM.me();
  }
};
