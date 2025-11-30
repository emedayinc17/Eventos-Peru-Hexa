import { ref } from 'vue'
import apiClient from '@/api/client'

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
    } catch (e: any) {
      error.value = e?.message || 'Error fetching admin summary'
      data.value = null
    } finally {
      loading.value = false
    }
  }

  // initial load (caller can also call load explicitly)
  void load()

  return { loading, error, data, load }
}

export default useAdminSummary
