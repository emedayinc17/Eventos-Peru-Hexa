<template>
  <div>
    <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-4 sm:mb-6">Dashboard Admin</h1>
    <div class="grid grid-cols-1 gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <div class="card hover:shadow-lg transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Total Pedidos</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">24</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-full">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">+12% vs mes anterior</p>
      </div>
      <div class="card hover:shadow-lg transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Total Usuarios</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">142</p>
          </div>
          <div class="p-3 bg-green-100 rounded-full">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">+8% nuevos usuarios</p>
      </div>
      <div class="card hover:shadow-lg transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs sm:text-sm font-medium text-gray-500">Total Servicios</h3>
            <p class="mt-2 text-2xl sm:text-3xl font-bold text-gray-900">38</p>
          </div>
          <div class="p-3 bg-purple-100 rounded-full">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Catálogo activo</p>
      </div>
      <div class="card hover:shadow-lg transition-shadow">
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
  </div>
</template>
