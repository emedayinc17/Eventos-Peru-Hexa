import { defineStore } from 'pinia';
import { ref } from 'vue';
import { catalogApi } from '@/api';
import type { TipoEvento, Servicio, Paquete, CreateTipoEventoRequest, CreateServicioRequest, CreatePaqueteRequest } from '@/types';

export const useCatalogStore = defineStore('catalog', () => {
  // State
  const tiposEvento = ref<TipoEvento[]>([]);
  const servicios = ref<Servicio[]>([]);
  const serviciosTotal = ref<number>(0);
  const serviciosServerSide = ref<boolean>(false);
  const paquetes = ref<Paquete[]>([]);
  const paquetesTotal = ref<number>(0);
  const paquetesServerSide = ref<boolean>(false);
  const paquetesCache = ref<Record<string, any>>({});
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Cache timestamps
  const lastFetchTipos = ref<number>(0);
  const lastFetchServicios = ref<number>(0);
  const lastFetchPaquetes = ref<number>(0);
  const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

  // Opciones cache + loading per-servicio (lazy-load)
  const opcionesCache = ref<Record<string, any[]>>({});
  const opcionesLoading = ref<Record<string, boolean>>({});

  // LocalStorage helpers
  function loadFromStorage() {
    try {
      const storedTipos = localStorage.getItem('catalog.tiposEvento');
      if (storedTipos) tiposEvento.value = JSON.parse(storedTipos);

      const storedServicios = localStorage.getItem('catalog.servicios');
      if (storedServicios) servicios.value = JSON.parse(storedServicios);

      const storedPaquetes = localStorage.getItem('catalog.paquetes');
      if (storedPaquetes) paquetes.value = JSON.parse(storedPaquetes);

      const storedTimestamps = localStorage.getItem('catalog.timestamps');
      if (storedTimestamps) {
        const ts = JSON.parse(storedTimestamps);
        lastFetchTipos.value = ts.tipos || 0;
        lastFetchServicios.value = ts.servicios || 0;
        lastFetchPaquetes.value = ts.paquetes || 0;
      }
    } catch (e) {
      console.error('Error loading from localStorage', e);
    }
  }

  function saveToStorage() {
    try {
      localStorage.setItem('catalog.tiposEvento', JSON.stringify(tiposEvento.value));
      localStorage.setItem('catalog.servicios', JSON.stringify(servicios.value));
      localStorage.setItem('catalog.paquetes', JSON.stringify(paquetes.value));
      localStorage.setItem('catalog.timestamps', JSON.stringify({
        tipos: lastFetchTipos.value,
        servicios: lastFetchServicios.value,
        paquetes: lastFetchPaquetes.value
      }));
    } catch (e) {
      console.error('Error saving to localStorage', e);
    }
  }

  // Initialize from storage
  loadFromStorage();

  // Actions - Tipos de Evento
  async function fetchTiposEvento(forceRefresh = false): Promise<void> {
    const now = Date.now();
    if (!forceRefresh && tiposEvento.value.length > 0 && now - lastFetchTipos.value < CACHE_TTL) {
      return; // Usar cache
    }

    loading.value = true;
    error.value = null;

    try {
      const response = await catalogApi.getTiposEvento();
      // `catalogApi.getTiposEvento()` may return either an array or an ApiResponse object.
      const raw: any = response;
      if (Array.isArray(raw)) {
        tiposEvento.value = raw;
      } else if (raw && (raw.data || raw.items)) {
        tiposEvento.value = raw.data || raw.items || [];
      } else {
        tiposEvento.value = [];
      }
      lastFetchTipos.value = now;
      saveToStorage();
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar tipos de evento';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createTipoEvento(data: CreateTipoEventoRequest): Promise<TipoEvento> {
    loading.value = true;
    error.value = null;

    try {
      const newTipo = await catalogApi.createTipoEvento(data);
      tiposEvento.value.push(newTipo);
      saveToStorage();
      return newTipo;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al crear tipo de evento';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateTipoEvento(id: number | string, data: CreateTipoEventoRequest): Promise<TipoEvento> {
    loading.value = true;
    error.value = null;

    try {
      const updated = await catalogApi.updateTipoEvento(id, data);
      const index = tiposEvento.value.findIndex(t => String(t.id) === String(id));
      if (index !== -1) {
        // Replace the entire object to trigger reactivity
        tiposEvento.value[index] = { ...updated };
        saveToStorage();
      }
      return updated;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar tipo de evento';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteTipoEvento(id: number | string): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      await catalogApi.deleteTipoEvento(id);
      tiposEvento.value = tiposEvento.value.filter(t => String(t.id) !== String(id));
      saveToStorage();
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al eliminar tipo de evento';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Actions - Servicios
  /**
   * fetchServicios soporta paginación híbrida:
   * - Si hay menos de 10 servicios en total, usa client-side (carga todos).
   * - Si hay 10 o más, usa server-side (limit/offset).
   * page y pageSize son opcionales (default: 1, 10).
   */
  async function fetchServicios(opts?: { tipoEventoId?: number; page?: number; pageSize?: number; forceRefresh?: boolean }): Promise<void> {
    const now = Date.now();
    const page = opts?.page ?? 1;
    const pageSize = opts?.pageSize ?? 10;
    const tipoEventoId = opts?.tipoEventoId;
    const forceRefresh = opts?.forceRefresh ?? false;

    // Si no hay cache o se fuerza refresh, consultar total primero
    if (!forceRefresh && servicios.value.length > 0 && now - lastFetchServicios.value < CACHE_TTL && !tipoEventoId) {
      return; // Usar cache solo si no hay filtro
    }

    loading.value = true;
    error.value = null;

    try {
      // Primer fetch: obtener total (limit=1 para eficiencia)
      const totalResp = await catalogApi.getServicios({ tipoEventoId, limit: 1, offset: 0 });
      serviciosTotal.value = totalResp.total;
      if (serviciosTotal.value < 10) {
        // Client-side: cargar todos
        const allResp = await catalogApi.getServicios({ tipoEventoId });
        servicios.value = allResp.items.map((s: any) => ({
          ...s,
          disponible: s.status !== undefined ? Number(s.status) === 1 : !!s.disponible,
        }));
        serviciosServerSide.value = false;
      } else {
        // Server-side: solo página actual
        const offset = (page - 1) * pageSize;
        const pageResp = await catalogApi.getServicios({ tipoEventoId, limit: pageSize, offset });
        servicios.value = pageResp.items.map((s: any) => ({
          ...s,
          disponible: s.status !== undefined ? Number(s.status) === 1 : !!s.disponible,
        }));
        serviciosServerSide.value = true;
      }
      lastFetchServicios.value = now;
      saveToStorage();
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar servicios';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Fetch opciones for a single servicio (with cache). Returns array (may be empty).
  async function fetchOpcionesForServicio(servicioId: string, opts: { force?: boolean } = {}): Promise<any[]> {
    const id = String(servicioId);
    if (!opts.force && opcionesCache.value[id] && opcionesCache.value[id].length > 0) {
      return opcionesCache.value[id];
    }
    if (opcionesLoading.value[id]) {
      // If already loading, wait until it's set in cache by the other call.
      return new Promise((resolve) => {
        const check = () => {
          if (!opcionesLoading.value[id]) {
            resolve(opcionesCache.value[id] || []);
          } else {
            setTimeout(check, 50);
          }
        };
        check();
      });
    }

    opcionesLoading.value[id] = true;
    try {
      const opciones = await catalogApi.getOpciones(id);
      opcionesCache.value = { ...opcionesCache.value, [id]: opciones || [] };
      return opciones || [];
    } catch (e) {
      opcionesCache.value = { ...opcionesCache.value, [id]: [] };
      return [];
    } finally {
      opcionesLoading.value[id] = false;
    }
  }

  // Prefetch opciones for given servicio ids (limit to `limit`), with a small delay to avoid bursts.
  // Prefetch opciones for given servicio ids (limit to `limit`). By default fetches in parallel
  // for faster UI fill. If you want to limit parallelism, call fetchOpcionesForServicio individually.
  function prefetchOpcionesFor(servicioIds: Array<string | number>, limit = 10, delayMs = 300): void {
    const ids = servicioIds.slice(0, limit).map(String);
    if (ids.length === 0) return;
    setTimeout(async () => {
      try {
        await Promise.all(ids.map(id => fetchOpcionesForServicio(id)));
      } catch (e) {
        // ignore individual failures; fetchOpcionesForServicio already records empty arrays on error
        // eslint-disable-next-line no-console
        console.debug('[catalogStore] prefetchOpcionesFor parallel failed', e);
      }
    }, delayMs);
  }

  // Prefetch opciones in parallel but limit concurrency if needed (simple token bucket)
  async function prefetchOpcionesWithConcurrency(servicioIds: Array<string | number>, limit = 10, concurrency = 4): Promise<void> {
    const ids = servicioIds.slice(0, limit).map(String);
    if (ids.length === 0) return;
    const queue = [...ids];
    const workers: Promise<void>[] = [];
    const runWorker = async () => {
      while (queue.length > 0) {
        const id = queue.shift() as string;
        try {
          // eslint-disable-next-line no-await-in-loop
          await fetchOpcionesForServicio(id);
        } catch (e) {
          console.debug('[catalogStore] prefetch worker failed for', id, e);
        }
      }
    };
    for (let i = 0; i < concurrency; i++) workers.push(runWorker());
    await Promise.all(workers);
  }

  async function createServicio(data: CreateServicioRequest): Promise<Servicio> {
    loading.value = true;
    error.value = null;

    try {
      const newServicio = await catalogApi.createServicio(data);
      // Normalize returned servicio (map status -> disponible)
      const svc = { ...newServicio, disponible: newServicio.status !== undefined ? Number(newServicio.status) === 1 : !!newServicio.disponible };
      servicios.value.push(svc);
      saveToStorage();
      // If frontend provided a category or precio_unitario, create an opcion linked to this servicio
      try {
        const monto = (data as any).precio_unitario;
        const categoria = (data as any).categoria;
        if (monto !== undefined && monto !== null) {
          const opcionPayload: any = {
            servicio_id: String(newServicio.id),
            nombre: `${newServicio.nombre} - opción`,
            moneda: 'PEN',
            monto: Number(monto),
            detalles: {},
          };
          if (categoria) opcionPayload.detalles.categoria = categoria;
          await catalogApi.createOpcion(opcionPayload);
        }
      } catch (e) {
        // Non-fatal: log and continue
        console.error('[catalogStore] failed to create opcion for servicio', e);
      }
      return newServicio;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al crear servicio';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateServicio(id: number | string, data: Partial<CreateServicioRequest>): Promise<Servicio> {
    loading.value = true;
    error.value = null;

    try {
      let updated = await catalogApi.updateServicio(id, data);

      // If backend did not provide `status` in the response, perform a read-after-write
      // to ensure we have authoritative data (some deployments/proxies may strip the field).
      if (updated && updated.status === undefined) {
        try {
          const fresh = await catalogApi.getServicio(id);
          if (fresh) updated = fresh as any;
        } catch (e) {
          // ignore and proceed with whatever we have
          console.debug('[catalogStore] get-after-put failed', e);
        }
      }

      const index = servicios.value.findIndex(s => String(s.id) === String(id));
      if (index !== -1) {
        // Normalize updated servicio
        const svc = { ...updated, disponible: updated.status !== undefined ? Number(updated.status) === 1 : !!updated.disponible };
        servicios.value[index] = svc;
        saveToStorage();
      }
      // If price/category provided, attempt to create a new opcion (non-fatal)
      try {
        const monto = (data as any).precio_unitario;
        const categoria = (data as any).categoria;
        if (monto !== undefined && monto !== null) {
          const opcionPayload: any = {
            servicio_id: String(id),
            nombre: `${updated.nombre} - opción`,
            moneda: 'PEN',
            monto: Number(monto),
            detalles: {},
          };
          if (categoria) opcionPayload.detalles.categoria = categoria;
          await catalogApi.createOpcion(opcionPayload);
        }
      } catch (e) {
        console.error('[catalogStore] failed to create opcion on servicio update', e);
      }
      return updated;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar servicio';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteServicio(id: number | string): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      await catalogApi.deleteServicio(id);
      servicios.value = servicios.value.filter(s => String(s.id) !== String(id));
      saveToStorage();
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al eliminar servicio';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Actions - Paquetes
  /**
   * fetchPaquetes soporta paginación híbrida:
   * - Si hay menos de 10 paquetes en total, usa client-side (carga todos).
   * - Si hay 10 o más, usa server-side (limit/offset).
   * page y pageSize son opcionales (default: 1, 10).
   */
  async function fetchPaquetes(opts?: { tipoEventoId?: number; page?: number; pageSize?: number; forceRefresh?: boolean }): Promise<void> {
    const now = Date.now();
    const page = opts?.page ?? 1;
    const pageSize = opts?.pageSize ?? 10;
    const tipoEventoId = opts?.tipoEventoId;
    const forceRefresh = opts?.forceRefresh ?? false;

    if (!forceRefresh && paquetes.value.length > 0 && now - lastFetchPaquetes.value < CACHE_TTL && !tipoEventoId) {
      return; // Usar cache solo si no hay filtro
    }

    loading.value = true;
    error.value = null;

    try {
      // Primer fetch: obtener total (limit=1 para eficiencia)
      const totalResp = await catalogApi.getPaquetes({ tipoEventoId, limit: 1, offset: 0 });
      paquetesTotal.value = totalResp.total;
      if (paquetesTotal.value < 10) {
        // Client-side: cargar todos
        const allResp = await catalogApi.getPaquetes({ tipoEventoId });
        paquetes.value = allResp.items;
        paquetesServerSide.value = false;
      } else {
        // Server-side: solo página actual
        const offset = (page - 1) * pageSize;
        const pageResp = await catalogApi.getPaquetes({ tipoEventoId, limit: pageSize, offset });
        paquetes.value = pageResp.items;
        paquetesServerSide.value = true;
      }
      if (!tipoEventoId) {
        lastFetchPaquetes.value = now;
        saveToStorage();
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar paquetes';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createPaquete(data: CreatePaqueteRequest): Promise<Paquete> {
    loading.value = true;
    error.value = null;

    try {
      const newPaquete = await catalogApi.createPaquete(data);
      // Do not push manually, let fetchPaquetes reload the full data with joins
      // paquetes.value.push(newPaquete); 
      // Force refresh to update list and storage
      await fetchPaquetes({ forceRefresh: true });
      return newPaquete;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al crear paquete';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updatePaquete(id: number | string, data: Partial<CreatePaqueteRequest>): Promise<Paquete> {
    loading.value = true;
    error.value = null;

    try {
      const updated = await catalogApi.updatePaquete(id, data);
      // Force refresh to update list and storage
      await fetchPaquetes({ forceRefresh: true });
      return updated;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar paquete';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deletePaquete(id: number | string): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      await catalogApi.deletePaquete(id);
      paquetes.value = paquetes.value.filter(p => String(p.id) !== String(id));
      saveToStorage();
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al eliminar paquete';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Fetch single paquete detalle (read-only) - returns backend paquete detalle
  async function getPaquete(id: number | string): Promise<any> {
    try {
      const p = await catalogApi.getPaquete(id);
      return p;
    } catch (e) {
      throw e;
    }
  }

  // Prefetch paquete detalles for a set of paquete ids (limited concurrency)
  async function prefetchPaqueteDetalles(paqueteIds: Array<string | number>, concurrency = 4): Promise<void> {
    const ids = paqueteIds.map(String);
    if (ids.length === 0) return;
    const queue = [...ids];
    const workers: Promise<void>[] = [];
    const runWorker = async () => {
      while (queue.length > 0) {
        const id = queue.shift() as string;
        try {
          const p = await getPaquete(id);
          paquetesCache.value = { ...paquetesCache.value, [id]: p || {} };
        } catch (e) {
          paquetesCache.value = { ...paquetesCache.value, [id]: {} };
        }
      }
    };
    for (let i = 0; i < concurrency; i++) workers.push(runWorker());
    await Promise.all(workers);
  }

  return {
    // State
    tiposEvento,
    servicios,
    opcionesCache,
    opcionesLoading,
    paquetesCache,
    paquetes,
    loading,
    error,
    // Actions
    fetchTiposEvento,
    createTipoEvento,
    updateTipoEvento,
    deleteTipoEvento,
    fetchServicios,
    fetchOpcionesForServicio,
    prefetchOpcionesFor,
    prefetchOpcionesWithConcurrency,
    createServicio,
    updateServicio,
    deleteServicio,
    fetchPaquetes,
    getPaquete,
    createPaquete,
    updatePaquete,
    deletePaquete,
    prefetchPaqueteDetalles,
  };
});
