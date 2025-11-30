<script setup lang="ts">
import { computed } from 'vue'
import useAdminSummary from '@/composables/useAdminSummary'

const { data, loading, error } = useAdminSummary()

const totalOrders = computed(() => {
  const orders = data.value?.orders
  if (orders != null) return orders
  const contratacionOk = data.value?.services?.contratacion?.ok
  if (contratacionOk === 200) return 0
  return '—'
})
// orders_by_status: object like { '0': 4, '1': 13, ... }
const ordersByStatus = computed(() => data.value?.orders_by_status ?? {})
const ordersStatusCount = (code: string | number) => {
  const s = ordersByStatus.value
  if (!s) return 0
  const key = String(code)
  const v = s[key]
  if (v == null) return 0
  return Number(v)
}
const ordersDraft = computed(() => ordersStatusCount(0))
const ordersQuoted = computed(() => ordersStatusCount(1))
const ordersApproved = computed(() => ordersStatusCount(2))
const ordersAssigned = computed(() => ordersStatusCount(3))
const totalUsers = computed(() => data.value?.users ?? '—')
const totalProviders = computed(() => data.value?.providers ?? '—')
const generatedAt = computed(() => data.value?.generatedAt ?? null)
const connectedFrom = computed(() => data.value?.connectedFrom ?? null)
</script>

<template>
  <div>
    <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-4 sm:mb-6">Dashboard Admin</h1>
    <p class="text-sm text-gray-500 mb-4">conectado desde <strong>{{ connectedFrom ?? 'desconocido' }}</strong></p>
    <div class="grid grid-cols-1 gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-4">

      <div class="card hover:shadow-lg transition-shadow h-full flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Total Pedidos</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">
              <template v-if="loading"> 
                <svg class="animate-spin w-5 h-5 inline-block text-gray-400" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                </svg>
                <span class="ml-2">Cargando...</span>
              </template>
              <template v-else>
                {{ totalOrders }}
              </template>
            </p>
          </div>
          <div class="p-3 bg-blue-100 rounded-full">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">
          <template v-if="error">Error cargando datos: {{ error }}</template>
          <template v-else>{{ generatedAt ? 'Última actualización: ' + generatedAt : 'Cargando...' }}</template>
        </p>
      </div>

      <!-- Status breakdown cards (flattened into main grid so all cards form 2 rows of 4) -->
      <div class="card hover:shadow-lg transition-shadow h-full flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Draft</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">{{ ordersDraft }}</p>
          </div>
          <div class="p-3 bg-gray-100 rounded-full">
            <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h10M7 11h6m2 9H5a2 2 0 01-2-2V7a2 2 0 012-2h7l2 2h3a2 2 0 012 2v9a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Pedidos en estado borrador</p>
      </div>

      <div class="card hover:shadow-lg transition-shadow h-full flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Cotizado</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">{{ ordersQuoted }}</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-full">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 1.567-3 3.5S10.343 15 12 15s3-1.567 3-3.5S13.657 8 12 8z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.4 15A7.5 7.5 0 0012 4.5V3" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Pedidos cotizados</p>
      </div>

      <div class="card hover:shadow-lg transition-shadow h-full flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Aprobado</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">{{ ordersApproved }}</p>
          </div>
          <div class="p-3 bg-green-100 rounded-full">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Pedidos aprobados</p>
      </div>

      <div class="card hover:shadow-lg transition-shadow h-full flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Asignado</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">{{ ordersAssigned }}</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-full">
            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-6a2 2 0 012-2h2a2 2 0 012 2v6M7 17h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2h-1.586A1 1 0 0116.828 4L15 2H9L7.172 4A1 1 0 016.586 5H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Pedidos asignados</p>
      </div>

      <div class="card hover:shadow-lg transition-shadow h-full flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Total Usuarios</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">
              <template v-if="loading">
                <svg class="animate-spin w-5 h-5 inline-block text-gray-400" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                </svg>
                <span class="ml-2">Cargando...</span>
              </template>
              <template v-else>
                {{ totalUsers }}
              </template>
            </p>
          </div>
          <div class="p-3 bg-green-100 rounded-full">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Datos dinámicos desde el backend</p>
      </div>

      <div class="card hover:shadow-lg transition-shadow h-full flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Total Proveedores</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">
              <template v-if="loading">
                <svg class="animate-spin w-5 h-5 inline-block text-gray-400" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                </svg>
                <span class="ml-2">Cargando...</span>
              </template>
              <template v-else>
                {{ totalProviders }}
              </template>
            </p>
          </div>
          <div class="p-3 bg-purple-100 rounded-full">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Catálogo conectado</p>
      </div>

      <div class="card hover:shadow-lg transition-shadow h-full flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Total Paquetes</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">15</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-full">
            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Ofertas disponibles</p>
      </div>
    </div>

    <!-- Debug panel: mostrar raw JSON para ayudar a diagnosticar -->
    <div class="mt-6 p-4 bg-white rounded shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <h2 class="text-sm font-medium text-gray-700">Debug: admin summary (raw)</h2>
        <button class="text-xs text-blue-600" @click.prevent="copyRaw">Copiar JSON</button>
      </div>
      <pre class="text-xs text-gray-700 overflow-auto max-h-48">{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({
  methods: {
    copyRaw() {
      try {
        const payload = JSON.stringify((this as any).data, null, 2)
        navigator.clipboard.writeText(payload)
        // eslint-disable-next-line no-alert
        alert('JSON copiado al portapapeles')
      } catch (e) {
        // eslint-disable-next-line no-alert
        alert('No se pudo copiar')
      }
    }
  }
})
</script>
