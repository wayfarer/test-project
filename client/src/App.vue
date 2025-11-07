<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

interface Player {
  id: number
  player_name: string
  position: string
  games: number
  at_bats: number
  runs: number
  hits: number
  doubles: number
  triples: number
  home_runs: number
  rbis: number
  walks: number
  strikeouts: number
  stolen_bases: number
  caught_stealing: number
  batting_average: number
  on_base_percentage: number
  slugging_percentage: number
  ops: number
  hits_per_game: number  // Computed field (hits / games)
  is_edited: boolean
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const players = ref<Player[]>([])
const loading = ref<boolean>(true)
const error = ref<string | null>(null)
const sortBy = ref<'hits' | 'home_runs' | 'hits_per_game'>('hits')
const selectedPlayer = ref<Player | null>(null)
const playerDescription = ref<string>('')
const loadingDescription = ref<boolean>(false)
const editingPlayer = ref<Player | null>(null)
const editForm = ref<Partial<Player>>({})

const fetchPlayers = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await fetch(`${API_URL}/api/players?sort_by=${sortBy.value}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data: Player[] = await response.json()
    players.value = data
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to fetch players'
    console.error('Error fetching players:', err)
  } finally {
    loading.value = false
  }
}

const fetchPlayerDescription = async (playerId: number) => {
  try {
    loadingDescription.value = true
    const response = await fetch(`${API_URL}/api/players/${playerId}/description`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    playerDescription.value = data.description
  } catch (err) {
    playerDescription.value = 'Failed to load description'
    console.error('Error fetching description:', err)
  } finally {
    loadingDescription.value = false
  }
}

const selectPlayer = async (player: Player) => {
  selectedPlayer.value = player
  playerDescription.value = ''
  await fetchPlayerDescription(player.id)
}

const closePlayerDetails = () => {
  selectedPlayer.value = null
  playerDescription.value = ''
}

const startEditing = (player: Player) => {
  editingPlayer.value = player
  editForm.value = { ...player }
}

const cancelEditing = () => {
  editingPlayer.value = null
  editForm.value = {}
}

const savePlayer = async () => {
  if (!editingPlayer.value || !editForm.value.id) return
  
  try {
    const response = await fetch(`${API_URL}/api/players/${editForm.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(editForm.value),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    // Refresh the player list
    await fetchPlayers()
    cancelEditing()
    
    // Update selected player if it's the one being edited
    if (selectedPlayer.value && selectedPlayer.value.id === editForm.value.id) {
      const updatedPlayer = await fetch(`${API_URL}/api/players/${editForm.value.id}`).then(r => r.json())
      selectedPlayer.value = updatedPlayer
      // Regenerate description if player was edited
      await fetchPlayerDescription(updatedPlayer.id)
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save player'
    console.error('Error saving player:', err)
  }
}

const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const formatAverage = (num: number) => {
  return num.toFixed(3)
}

onMounted(() => {
  fetchPlayers()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-4xl font-bold text-gray-900 mb-8">Baseball Players</h1>
      
      <!-- Sorting Controls -->
      <div class="mb-6 flex gap-4">
        <button
          @click="sortBy = 'hits'; fetchPlayers()"
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-colors',
            sortBy === 'hits' 
              ? 'bg-blue-600 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          ]"
        >
          Sort by Hits
        </button>
        <button
          @click="sortBy = 'home_runs'; fetchPlayers()"
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-colors',
            sortBy === 'home_runs' 
              ? 'bg-blue-600 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          ]"
        >
          Sort by Home Runs
        </button>
        <button
          @click="sortBy = 'hits_per_game'; fetchPlayers()"
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-colors',
            sortBy === 'hits_per_game' 
              ? 'bg-blue-600 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          ]"
        >
          Sort by Hits/Game
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
        {{ error }}
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">Loading players...</p>
      </div>

      <!-- Player List -->
      <div v-else class="bg-white rounded-lg shadow overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Player</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Position</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Games</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hits</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">HR</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RBI</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">AVG</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">H/G</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="player in players"
                :key="player.id"
                class="hover:bg-gray-50 cursor-pointer"
                @click="selectPlayer(player)"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ player.player_name }}</div>
                  <div v-if="player.is_edited" class="text-xs text-blue-600">Edited</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ player.position }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatNumber(player.games) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">{{ formatNumber(player.hits) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">{{ formatNumber(player.home_runs) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatNumber(player.rbis) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatAverage(player.batting_average) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatAverage(player.hits_per_game) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    @click.stop="startEditing(player)"
                    class="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Edit
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Player Details Modal -->
      <div
        v-if="selectedPlayer"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click="closePlayerDetails"
      >
        <div
          class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          @click.stop
        >
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <h2 class="text-2xl font-bold text-gray-900">{{ selectedPlayer.player_name }}</h2>
              <button
                @click="closePlayerDetails"
                class="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
            
            <div class="mb-6">
              <h3 class="text-lg font-semibold text-gray-700 mb-2">Description</h3>
              <div v-if="loadingDescription" class="text-gray-500">Loading description...</div>
              <p v-else class="text-gray-700 leading-relaxed">{{ playerDescription }}</p>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-500">Position:</span>
                <span class="ml-2 font-medium">{{ selectedPlayer.position }}</span>
              </div>
              <div>
                <span class="text-gray-500">Games:</span>
                <span class="ml-2 font-medium">{{ formatNumber(selectedPlayer.games) }}</span>
              </div>
              <div>
                <span class="text-gray-500">At-Bats:</span>
                <span class="ml-2 font-medium">{{ formatNumber(selectedPlayer.at_bats) }}</span>
              </div>
              <div>
                <span class="text-gray-500">Runs:</span>
                <span class="ml-2 font-medium">{{ formatNumber(selectedPlayer.runs) }}</span>
              </div>
              <div>
                <span class="text-gray-500">Hits:</span>
                <span class="ml-2 font-medium">{{ formatNumber(selectedPlayer.hits) }}</span>
              </div>
              <div>
                <span class="text-gray-500">Home Runs:</span>
                <span class="ml-2 font-medium">{{ formatNumber(selectedPlayer.home_runs) }}</span>
              </div>
              <div>
                <span class="text-gray-500">RBIs:</span>
                <span class="ml-2 font-medium">{{ formatNumber(selectedPlayer.rbis) }}</span>
              </div>
              <div>
                <span class="text-gray-500">AVG:</span>
                <span class="ml-2 font-medium">{{ formatAverage(selectedPlayer.batting_average) }}</span>
              </div>
              <div>
                <span class="text-gray-500">OBP:</span>
                <span class="ml-2 font-medium">{{ formatAverage(selectedPlayer.on_base_percentage) }}</span>
              </div>
              <div>
                <span class="text-gray-500">SLG:</span>
                <span class="ml-2 font-medium">{{ formatAverage(selectedPlayer.slugging_percentage) }}</span>
              </div>
              <div>
                <span class="text-gray-500">OPS:</span>
                <span class="ml-2 font-medium">{{ formatAverage(selectedPlayer.ops) }}</span>
              </div>
              <div>
                <span class="text-gray-500">Hits/Game:</span>
                <span class="ml-2 font-medium">{{ formatAverage(selectedPlayer.hits_per_game) }}</span>
              </div>
            </div>
            
            <div class="mt-6 flex justify-end">
              <button
                @click="startEditing(selectedPlayer)"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Edit Player
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Modal -->
      <div
        v-if="editingPlayer"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click="cancelEditing"
      >
        <div
          class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          @click.stop
        >
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <h2 class="text-2xl font-bold text-gray-900">Edit {{ editingPlayer.player_name }}</h2>
              <button
                @click="cancelEditing"
                class="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Player Name</label>
                <input
                  v-model="editForm.player_name"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Position</label>
                <input
                  v-model="editForm.position"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Games</label>
                <input
                  v-model.number="editForm.games"
                  type="number"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Hits</label>
                <input
                  v-model.number="editForm.hits"
                  type="number"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Home Runs</label>
                <input
                  v-model.number="editForm.home_runs"
                  type="number"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">RBIs</label>
                <input
                  v-model.number="editForm.rbis"
                  type="number"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Batting Average</label>
                <input
                  v-model.number="editForm.batting_average"
                  type="number"
                  step="0.001"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div class="mt-6 flex justify-end gap-4">
              <button
                @click="cancelEditing"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                @click="savePlayer"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
