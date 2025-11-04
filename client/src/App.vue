<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface ApiResponse {
  message: string
}

const message = ref<string>('')
const loading = ref<boolean>(true)
const error = ref<string | null>(null)

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const fetchMessage = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await fetch(`${API_URL}/`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data: ApiResponse = await response.json()
    message.value = data.message
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to fetch message'
    console.error('Error fetching message:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMessage()
})
</script>

<template>
  <div>
    <h1 v-if="loading">Loading...</h1>
    <h1 v-else-if="error" style="color: red;">Error: {{ error }}</h1>
    <h1 v-else>{{ message }}</h1>
  </div>
</template>

<style scoped></style>
