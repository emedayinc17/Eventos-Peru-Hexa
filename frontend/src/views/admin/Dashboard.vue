<script setup lang="ts">
import { computed, onMounted } from 'vue'
import useAdminSummary from '@/composables/useAdminSummary'
import { useOrdersStore } from '@/stores/orders'

const { data, loading, error } = useAdminSummary()
const ordersStore = useOrdersStore()

// Load admin orders (small list used to compute counts). This replaces an extra metrics call
onMounted(() => {
  // Fire-and-forget; UI will update when the store populates
  void ordersStore.fetchPedidos(undefined, undefined, true).catch(() => {})
})

// Prefer live orders from the orders store when available; otherwise fallback to summary data
const totalOrders = computed(() => {
  if (ordersStore.pedidos && ordersStore.pedidos.length > 0) return ordersStore.pedidos.length
  const orders = data.value?.orders
  if (orders != null) return orders
  const contratacionOk = data.value?.services?.contratacion?.ok
  if (contratacionOk === 200) return 0
  return '—'
})

const ordersByStatus = computed(() => {
  // If we have pedidos in the store, compute by reducing them; be tolerant with different status field names
  if (ordersStore.pedidos && ordersStore.pedidos.length > 0) {
    const map: Record<string, number> = {}
    for (const p of ordersStore.pedidos) {
      const s = (p as any).status ?? (p as any).estado ?? (p as any).estado_id ?? (p as any).estadoId ?? (p as any).state
      if (s == null) continue
      const key = String(s)
      map[key] = (map[key] || 0) + 1
    }
    return map
  }
  return data.value?.orders_by_status ?? {}
})

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

// Chart helpers: compute labels and series for last 6 months using ordersStore.pedidos (fallback to summary if empty)
function getLastMonths(n = 6) {
  const months: Date[] = []
  const now = new Date()
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    months.push(d)
  }
  return months
}

const months = getLastMonths(6)
const labels = computed(() => {
  return months.map(m => m.toLocaleString('es-PE', { month: 'short' })).map(s => s.charAt(0).toUpperCase() + s.slice(1))
})

function monthRange(monthDate: Date) {
  const start = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1)
  const end = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 1)
  return { start, end }
}

const ordersSeries = computed(() => {
  const arr: number[] = []
  for (const m of months) {
    const { start, end } = monthRange(m)
    let count = 0
    if (ordersStore.pedidos && ordersStore.pedidos.length > 0) {
      count = ordersStore.pedidos.filter((p: any) => {
        const created = (p as any).created_at ?? (p as any).fecha_creacion ?? (p as any).fecha_evento ?? null
        if (!created) return false
        const d = new Date(created)
        return d >= start && d < end
      }).length
    } else if (data.value && Array.isArray(data.value.orders_by_month)) {
      // optional fallback if summary provides a series
      const key = `${start.getFullYear()}-${start.getMonth() + 1}`
      const found = (data.value.orders_by_month || []).find((x: any) => x.month === key)
      count = found ? Number(found.count) : 0
    }
    arr.push(count)
  }
  return arr
})

// removed unused ordersMax to avoid lint warning

const revenueSeries = computed(() => {
  const arr: number[] = []
  for (const m of months) {
    const { start, end } = monthRange(m)
    let sum = 0
    if (ordersStore.pedidos && ordersStore.pedidos.length > 0) {
      for (const p of ordersStore.pedidos) {
        const created = (p as any).created_at ?? (p as any).fecha_creacion ?? (p as any).fecha_evento ?? null
        if (!created) continue
        const d = new Date(created)
        if (d >= start && d < end) {
          sum += Number((p as any).monto_total ?? (p as any).total ?? 0) || 0
        }
      }
    }
    arr.push(sum)
  }
  return arr
})

const revenueMax = computed(() => Math.max(1, ...revenueSeries.value))

const revenuePoints = computed(() => {
  // Build "x,y x,y ..." for polyline (svg viewbox 600x160)
  const pts: string[] = []
  revenueSeries.value.forEach((v, i) => {
    const x = 30 + i * 95
    const y = 140 - (v / revenueMax.value) * 120
    pts.push(`${x},${y.toFixed(2)}`)
  })
  return pts.join(' ')
})

const revenueTotal = computed(() => revenueSeries.value.reduce((s, v) => s + v, 0))

// Period range for "últimos 6 meses" (non-null assertions because months is built with 6 entries)
const periodStart = months[0]!
const periodEnd = months[months.length - 1]!

const periodOrdersTotal = computed(() => {
  if (ordersStore.pedidos && ordersStore.pedidos.length > 0) {
    const start = new Date(periodStart.getFullYear(), periodStart.getMonth(), 1)
    const end = new Date(periodEnd.getFullYear(), periodEnd.getMonth() + 1, 1)
    return ordersStore.pedidos.filter((p: any) => {
      const created = (p as any).created_at ?? (p as any).fecha_creacion ?? (p as any).fecha_evento ?? null
      if (!created) return false
      const d = new Date(created)
      return d >= start && d < end
    }).length
  }
  // Fallback: sum of ordersSeries months
  return ordersSeries.value.reduce((s, v) => s + v, 0)
})

// Top event types in the period
const topEventData = computed(() => {
  const map: Record<string, number> = {}
  const names: Record<string, string> = {}
  const start = new Date(periodStart.getFullYear(), periodStart.getMonth(), 1)
  const end = new Date(periodEnd.getFullYear(), periodEnd.getMonth() + 1, 1)

  if (ordersStore.pedidos && ordersStore.pedidos.length > 0) {
    for (const p of ordersStore.pedidos) {
      const created = (p as any).created_at ?? (p as any).fecha_creacion ?? (p as any).fecha_evento ?? null
      if (!created) continue
      const d = new Date(created)
      if (d < start || d >= end) continue
      const tipoId = String((p as any).tipo_evento_id ?? (p as any).tipo_evento?.id ?? (p as any).tipo_evento_id)
      const tipoName = (p as any).tipo_evento?.nombre ?? (p as any).tipo_evento_nombre ?? `Tipo ${tipoId}`
      map[tipoId] = (map[tipoId] || 0) + 1
      names[tipoId] = tipoName
    }
  }

  // Turn into sorted array
  const arr = Object.keys(map).map(k => ({ id: k, name: names[k] || k, count: Number(map[k] || 0) }))
  arr.sort((a, b) => (Number(b.count) || 0) - (Number(a.count) || 0))
  const top = arr.slice(0, 6)
  return top
})

const topEventLabels = computed(() => topEventData.value.map(x => x.name ?? '—'))
const topEventCounts = computed(() => topEventData.value.map(x => Number(x.count || 0)))
const eventMax = computed(() => {
  const arr = topEventCounts.value.map(v => v || 0)
  return Math.max(1, ...arr)
})
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

    <!-- Charts: top event types (left) and revenue (right) -->
    <div class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div class="p-4 bg-white rounded shadow-sm">
        <h2 class="text-sm font-medium text-gray-700 mb-2">Tipos de evento más solicitados (últimos 6 meses)</h2>
        <div class="text-xs text-gray-500 mb-3">Total pedidos en periodo: <strong>{{ periodOrdersTotal }}</strong></div>
        <div class="w-full h-40">
          <svg viewBox="0 0 600 160" class="w-full h-full">
            <!-- grid lines -->
            <g stroke="#e5e7eb" stroke-width="1">
              <line x1="0" y1="20" x2="600" y2="20" />
              <line x1="0" y1="60" x2="600" y2="60" />
              <line x1="0" y1="100" x2="600" y2="100" />
              <line x1="0" y1="140" x2="600" y2="140" />
            </g>
            <!-- bars for top event types -->
            <g fill="#6366f1">
              <g v-for="(v, i) in topEventCounts" :key="i">
                <rect :x="20 + i * 90" :y="140 - (v / eventMax) * 120" :width="50" :height="(v / eventMax) * 120" rx="6" />
              </g>
            </g>
            <!-- labels -->
            <g fill="#374151" font-size="11" text-anchor="middle">
              <text v-for="(lab, i) in topEventLabels" :key="i" :x="45 + i * 90" y="155">{{ lab }}</text>
            </g>
          </svg>
        </div>
      </div>

      <div class="p-4 bg-white rounded shadow-sm">
        <h2 class="text-sm font-medium text-gray-700 mb-2">Ingresos últimos 6 meses</h2>
        <div class="text-xs text-gray-500 mb-3">Ingresos totales: <strong>S/ {{ revenueTotal.toFixed(2) }}</strong></div>
        <div class="w-full h-40">
          <svg viewBox="0 0 600 160" class="w-full h-full">
            <!-- grid lines -->
            <g stroke="#e5e7eb" stroke-width="1">
              <line x1="0" y1="20" x2="600" y2="20" />
              <line x1="0" y1="60" x2="600" y2="60" />
              <line x1="0" y1="100" x2="600" y2="100" />
              <line x1="0" y1="140" x2="600" y2="140" />
            </g>
            <!-- revenue polyline -->
            <polyline :points="revenuePoints" fill="none" stroke="#10b981" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" />
            <!-- area under curve -->
            <polyline :points="revenuePoints + ' 600,140 0,140'" fill="#d1fae5" opacity="0.6" stroke="none" />
            <!-- labels -->
            <g fill="#6b7280" font-size="12" text-anchor="middle">
              <text v-for="(lab, i) in labels" :key="i" :x="30 + i * 95" y="155">{{ lab }}</text>
            </g>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>


