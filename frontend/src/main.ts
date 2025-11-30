import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import App from './App.vue'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Global listener for authorization/permission issues dispatched by api client
window.addEventListener('auth:insufficient', (ev: Event) => {
	try {
		const detail = (ev as CustomEvent).detail || {};
		const msg = detail && detail.detail ? detail.detail : 'No autorizado para este recurso';
		console.warn('auth:insufficient', detail);

		// Show a small temporary banner to the user (non-blocking)
		const id = 'auth-insufficient-banner';
		let el = document.getElementById(id);
		if (!el) {
			el = document.createElement('div');
			el.id = id;
			el.style.position = 'fixed';
			el.style.top = '10px';
			el.style.right = '10px';
			el.style.zIndex = '9999';
			el.style.background = '#f8d7da';
			el.style.color = '#721c24';
			el.style.padding = '10px 14px';
			el.style.border = '1px solid #f5c6cb';
			el.style.borderRadius = '6px';
			el.style.boxShadow = '0 2px 6px rgba(0,0,0,0.15)';
			document.body.appendChild(el);
		}
		el.textContent = `No autorizado: ${msg}`;
		// Hide after 5s
		setTimeout(() => {
			try { el && el.remove(); } catch(e) {}
		}, 5000);
	} catch (e) {
		// ignore
	}
});

app.mount('#app')
