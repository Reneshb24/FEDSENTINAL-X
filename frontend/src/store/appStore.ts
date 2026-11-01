// src/store/appStore.ts
// Zustand store for FedSentinel-X front-end state management
// Authoritative snapshot of backend data and WebSocket event handling.

import { create } from 'zustand'
import { AnyFedSentinelEvent } from '../ws/types'

export interface HospitalNode {
  id: string
  name: string
  code: string
  status: string
  lastSeen: string
  trustScore?: number
}

export interface RoundInfo {
  id: string
  round_number: number
  status: string
  start_time?: string
  end_time?: string
}

export interface UpdateRecord {
  id: string
  hospital_id: string
  round_id: string
  status: string
  created_at: string
}

export interface AppState {
  hospitals: Record<string, HospitalNode>
  rounds: Record<string, RoundInfo>
  updates: Record<string, UpdateRecord>
  eventLog: AnyFedSentinelEvent[]
  applyEvent: (event: AnyFedSentinelEvent) => void
  fetchInitialState: (token: string) => Promise<void>
}

export const useAppStore = create<AppState>()((set) => ({
  hospitals: {},
  rounds: {},
  updates: {},
  eventLog: [],

  applyEvent: (event) => {
    set((state) => {
      const newLog = [...state.eventLog, event]
      if (newLog.length > 1000) newLog.shift()

      const newHospitals = { ...state.hospitals }
      const newRounds = { ...state.rounds }
      const newUpdates = { ...state.updates }

      switch (event.event_type) {
        case 'HOSPITAL_CONNECTED':
        case 'HOSPITAL_STATUS_UPDATED': {
          const h = event.payload as HospitalNode
          if (h && h.id) {
            newHospitals[h.id] = { ...newHospitals[h.id], ...h }
          }
          break
        }
        case 'ROUND_CREATED':
        case 'ROUND_UPDATED': {
          const r = event.payload as RoundInfo
          if (r && r.id) {
            newRounds[r.id] = { ...newRounds[r.id], ...r }
          }
          break
        }
        case 'UPDATE_CREATED': {
          const u = event.payload as UpdateRecord
          if (u && u.id) {
            newUpdates[u.id] = { ...newUpdates[u.id], ...u }
          }
          break
        }
        case 'UPDATE_STATUS_CHANGED': {
          const payload = event.payload as { id: string; status: string }
          if (payload && payload.id && newUpdates[payload.id]) {
            newUpdates[payload.id] = { ...newUpdates[payload.id], status: payload.status }
          }
          break
        }
        default:
          break
      }

      return {
        eventLog: newLog,
        hospitals: newHospitals,
        rounds: newRounds,
        updates: newUpdates,
      }
    })
  },

  fetchInitialState: async (token: string) => {
    const base = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://127.0.0.1:8000'
    const cleanBase = base.replace(/\/+$/, '')
    const headers: Record<string, string> = { Authorization: `Bearer ${token}` }
    try {
      const [hRes, rRes, uRes] = await Promise.all([
        fetch(`${cleanBase}/api/v1/hospitals`, { headers }).then((r) => r.json()).catch(() => []),
        fetch(`${cleanBase}/api/v1/rounds`, { headers }).then((r) => r.json()).catch(() => []),
        fetch(`${cleanBase}/api/v1/updates`, { headers }).then((r) => r.json()).catch(() => []),
      ])

      set((state) => {
        const nextHospitals = { ...state.hospitals }
        const nextRounds = { ...state.rounds }
        const nextUpdates = { ...state.updates }

        if (Array.isArray(hRes)) {
          hRes.forEach((h: HospitalNode) => {
            if (h && h.id) nextHospitals[h.id] = h
          })
        }
        if (Array.isArray(rRes)) {
          rRes.forEach((r: RoundInfo) => {
            if (r && r.id) nextRounds[r.id] = r
          })
        }
        if (Array.isArray(uRes)) {
          uRes.forEach((u: UpdateRecord) => {
            if (u && u.id) nextUpdates[u.id] = u
          })
        }

        return {
          hospitals: nextHospitals,
          rounds: nextRounds,
          updates: nextUpdates,
        }
      })
    } catch (err) {
      console.error('Failed to fetch initial state', err)
    }
  },
}))
