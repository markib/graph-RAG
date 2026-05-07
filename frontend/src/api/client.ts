import axios from 'axios'
import type { GraphData } from '../types/graph'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function askQuestion(query: string) {
  const response = await client.get('/ask', { params: { q: query } })
  return response.data as { answer: string; cypher: string; graph: GraphData }
}

export async function fetchGraph() {
  const response = await client.get('/graph')
  return response.data as GraphData
}

export async function clearGraph() {
  const response = await client.delete('/graph/clear')
  return response.data as { message: string }
}
