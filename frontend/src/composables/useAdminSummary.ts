import { ref } from 'vue'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'

// Module-level cache + shared polling/listener so multiple components share state
let _cache: any = null
let _cacheTs = 0
const _TTL = Number(import.meta.env.VITE_ADMIN_SUMMARY_TTL_MS || 3000)
let _started = false
let _intervalId: number | null = null

async function _fetchAndCache(params: { from?: string; to?: string } = {}) {
  // Guard: only fetch admin summary for admin users
  try {
    const auth = useAuthStore()
    if (!auth?.isAdmin) {
      // Not authorized to fetch admin summary
      return null
    }
  } catch (e) {
    // If store is not available for any reason, skip fetching
    return null
  }

  try {
    const resp = await apiClient.get('/admin/summary', { params })
    _cache = resp.data
    _cacheTs = Date.now()
    return _cache
  } catch (e) {
    // don't clear cache on error; keep stale data for UX
    return null
  }
}

function _ensureBackgroundTasks() {
  if (_started) return

  // Only start background polling for admin users
  try {
    const auth = useAuthStore()
    if (!auth?.isAdmin) return
  } catch (e) {
    return
  }

  _started = true

  // Poll every few seconds to keep dashboard fresh in active sessions
  const intervalMs = Number(import.meta.env.VITE_ADMIN_SUMMARY_POLL_MS || 5000)
  _intervalId = window.setInterval(() => {
    void _fetchAndCache()
  }, intervalMs)

  // Revalidate on visibility change (when user focuses the tab)
  window.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      void _fetchAndCache()
    }
  })
}

export function useAdminSummary() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const data = ref<any>(null)

  async function load(params: { from?: string; to?: string } = {}) {
    loading.value = true
    error.value = null
    try {
      const resp = await apiClient.get('/admin/summary', { params })
      data.value = resp.data
      // update module cache
      _cache = resp.data
      _cacheTs = Date.now()
      return data.value
    } catch (e: any) {
      error.value = e?.message || 'Error fetching admin summary'
      return null
    } finally {
      loading.value = false
    }
  }

  // If there's a fresh cache, use it immediately for snappy UI
  if (_cache && (Date.now() - _cacheTs) < _TTL) {
    data.value = _cache
  } else {
    // kick off an initial background fetch but leave loading false so UI can show cached content
    // we still expose load() for explicit calls
    void (async () => {
      loading.value = true
      try {
        const fetched = await _fetchAndCache()
        if (fetched) data.value = fetched
      } finally {
        loading.value = false
      }
    })()
  }

  // Ensure background polling / focus revalidation only once per page
  if (typeof window !== 'undefined') {
    _ensureBackgroundTasks()
  }

  return { loading, error, data, load }
}

export default useAdminSummary
