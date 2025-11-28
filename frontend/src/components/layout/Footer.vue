<template>
  <footer class="bg-gray-800 text-white mt-auto">
    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <h3 class="text-lg font-semibold mb-4">EventosPeru</h3>
          <p class="text-sm text-gray-300">
            Organizamos el evento de tus sueños con servicios personalizados y profesionales.
          </p>
        </div>
        <div>
          <h4 class="text-sm font-semibold uppercase tracking-wide mb-4">Enlaces Rápidos</h4>
          <ul class="space-y-2">
            <li><a href="/" class="text-sm text-gray-300 hover:text-white">Inicio</a></li>
            <li><a href="/paquetes" class="text-sm text-gray-300 hover:text-white">Paquetes</a></li>
            <li><a href="/proveedores" class="text-sm text-gray-300 hover:text-white">Proveedores</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-semibold uppercase tracking-wide mb-4">Contacto</h4>
          <ul class="space-y-2 text-sm text-gray-300">
            <li>Email: contacto@eventosperu.com</li>
            <li>Teléfono: +51 987 654 321</li>
            <li>Lima, Perú</li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-semibold uppercase tracking-wide mb-4">Legal</h4>
          <ul class="space-y-2">
            <li><a href="#" class="text-sm text-gray-300 hover:text-white">Términos y Condiciones</a></li>
            <li><a href="#" class="text-sm text-gray-300 hover:text-white">Política de Privacidad</a></li>
          </ul>
        </div>
      </div>
      <div class="mt-8 border-t border-gray-700 pt-8 text-center">
        <p class="text-sm text-gray-400">
          © {{ new Date().getFullYear() }} EventosPeru. Todos los derechos reservados.
        </p>
      </div>
    </div>
  </footer>
</template>
