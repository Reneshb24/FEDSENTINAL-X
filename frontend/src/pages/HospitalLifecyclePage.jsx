import React, { useState, useEffect } from 'react'
import {
  Activity,
  Shield,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  Ban,
  Lock,
  Unlock,
  CheckCircle,
  Search,
  RefreshCw
} from 'lucide-react'

const rawApi = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://127.0.0.1:8000'
const API = rawApi.replace(/\/+$/, '')

export default function HospitalLifecyclePage({ data, token, onDataRefresh }) {
  const [hospitals, setHospitals] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedHospital, setSelectedHospital] = useState(null)
  const [actionType, setActionType] = useState('')
  const [reason, setReason] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')

  async function loadHospitals() {
    setLoading(true)
    try {
      const resp = await fetch(`${API}/api/v1/hospitals`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const d = await resp.json()
      setHospitals(Array.isArray(d) ? d : [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHospitals()
  }, [])

  const filtered = hospitals.filter(h => {
    if (!search.trim()) return true
    const q = search.toLowerCase()
    return (
      String(h.name || '').toLowerCase().includes(q) ||
      String(h.code || '').toLowerCase().includes(q)
    )
  })

  async function executeAction() {
    if (!selectedHospital || !actionType) return
    setBusy(true)
    setMessage('')
    try {
      const resp = await fetch(`${API}/api/v1/hospitals/${selectedHospital.id}/${actionType}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason: reason.trim() || undefined })
      })
      if (!resp.ok) {
        const d = await resp.json().catch(() => null)
        throw new Error(d?.detail || `Action failed with status ${resp.status}`)
      }
      setMessage(`Successfully executed ${actionType.toUpperCase()} on ${selectedHospital.name} (${selectedHospital.code}).`)
      setSelectedHospital(null)
      setActionType('')
      setReason('')
      await loadHospitals()
      onDataRefresh?.()
    } catch (err) {
      alert(`Lifecycle action error: ${err.message}`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page-container" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <div style={{ color: '#00e5ff', fontSize: 11, fontWeight: 700, letterSpacing: '0.1em' }}>
            FEDERATION / LIFECYCLE MANAGEMENT
          </div>
          <h1 style={{ fontSize: 26, margin: '4px 0', color: '#fff', display: 'flex', alignItems: 'center', gap: 10 }}>
            <Activity size={26} color="#00e5ff" />
            Hospital Lifecycle & Security Operations
          </h1>
          <p style={{ color: '#94a3b8', fontSize: 13, margin: 0 }}>
            Authorize, suspend, quarantine, or revoke hospital enclave nodes with cryptographic tracking and audit logging.
          </p>
        </div>

        <button
          onClick={loadHospitals}
          className="hp-button"
          disabled={loading}
          style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', padding: '8px 14px', borderRadius: 6, cursor: 'pointer' }}
        >
          <RefreshCw size={14} className={loading ? 'hp-spin' : ''} />
          Refresh
        </button>
      </div>

      {message && (
        <div style={{ padding: '12px 16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', color: '#10b981', borderRadius: 6, marginBottom: 16, fontSize: 13 }}>
          {message}
        </div>
      )}

      {/* Search */}
      <div style={{ marginBottom: 16 }}>
        <input
          type="text"
          placeholder="Filter hospitals by code or name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ background: '#0f172a', border: '1px solid #334155', color: '#fff', padding: '8px 12px', borderRadius: 4, width: '280px', fontSize: 12 }}
        />
      </div>

      {/* Hospitals Table */}
      <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#020617', borderBottom: '1px solid #1e293b', color: '#64748b' }}>
              <th style={{ padding: '12px 16px' }}>CODE</th>
              <th style={{ padding: '12px 16px' }}>HOSPITAL NAME</th>
              <th style={{ padding: '12px 16px' }}>STATUS</th>
              <th style={{ padding: '12px 16px' }}>SECURITY POSTURE</th>
              <th style={{ padding: '12px 16px' }}>FEDERATION ELIGIBLE</th>
              <th style={{ padding: '12px 16px', textAlign: 'right' }}>LIFECYCLE ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((h) => {
              const isActive = h.status === 'ACTIVE'
              const isSuspended = h.status === 'SUSPENDED'
              const isQuarantined = h.security_status === 'QUARANTINED'

              return (
                <tr key={h.id} style={{ borderBottom: '1px solid #1e293b' }}>
                  <td style={{ padding: '12px 16px', fontWeight: 700, color: '#38bdf8' }}>{h.code}</td>
                  <td style={{ padding: '12px 16px', color: '#f8fafc', fontWeight: 600 }}>{h.name}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: 4,
                      fontSize: 10,
                      fontWeight: 700,
                      background: isActive ? 'rgba(16, 185, 129, 0.2)' : isSuspended ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                      color: isActive ? '#10b981' : isSuspended ? '#ef4444' : '#f59e0b'
                    }}>
                      {h.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: 4,
                      fontSize: 10,
                      fontWeight: 700,
                      background: isQuarantined ? 'rgba(239, 68, 68, 0.2)' : 'rgba(56, 189, 248, 0.2)',
                      color: isQuarantined ? '#ef4444' : '#38bdf8'
                    }}>
                      {h.security_status || 'TRUSTED'}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', color: h.is_eligible ? '#10b981' : '#64748b' }}>
                    {h.is_eligible ? 'ELIGIBLE' : 'NOT ELIGIBLE'}
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: 6 }}>
                      {isActive && (
                        <button
                          onClick={() => { setSelectedHospital(h); setActionType('suspend'); }}
                          style={{ background: '#1e293b', border: '1px solid #ef4444', color: '#ef4444', padding: '4px 8px', borderRadius: 4, fontSize: 10, cursor: 'pointer' }}
                        >
                          Suspend
                        </button>
                      )}
                      {isSuspended && (
                        <button
                          onClick={() => { setSelectedHospital(h); setActionType('restore'); }}
                          style={{ background: '#1e293b', border: '1px solid #10b981', color: '#10b981', padding: '4px 8px', borderRadius: 4, fontSize: 10, cursor: 'pointer' }}
                        >
                          Restore
                        </button>
                      )}
                      {!isQuarantined && (
                        <button
                          onClick={() => { setSelectedHospital(h); setActionType('quarantine'); }}
                          style={{ background: '#1e293b', border: '1px solid #f59e0b', color: '#f59e0b', padding: '4px 8px', borderRadius: 4, fontSize: 10, cursor: 'pointer' }}
                        >
                          Quarantine
                        </button>
                      )}
                      {isQuarantined && (
                        <button
                          onClick={() => { setSelectedHospital(h); setActionType('release'); }}
                          style={{ background: '#1e293b', border: '1px solid #38bdf8', color: '#38bdf8', padding: '4px 8px', borderRadius: 4, fontSize: 10, cursor: 'pointer' }}
                        >
                          Release
                        </button>
                      )}
                      <button
                        onClick={() => { setSelectedHospital(h); setActionType('revoke'); }}
                        style={{ background: '#1e293b', border: '1px solid #64748b', color: '#94a3b8', padding: '4px 8px', borderRadius: 4, fontSize: 10, cursor: 'pointer' }}
                      >
                        Revoke
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Confirmation Modal */}
      {selectedHospital && actionType && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, maxWidth: 460, width: '100%', padding: 24 }}>
            <h3 style={{ margin: '0 0 10px', color: '#f8fafc' }}>
              Confirm {actionType.toUpperCase()}
            </h3>
            <p style={{ color: '#cbd5e1', fontSize: 12 }}>
              Are you sure you want to <strong>{actionType}</strong> hospital <strong>{selectedHospital.name} ({selectedHospital.code})</strong>?
            </p>

            <label style={{ display: 'block', fontSize: 11, color: '#94a3b8', marginTop: 12 }}>
              REASON / AUDIT JUSTIFICATION
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Reason for administrative lifecycle transition..."
                style={{ width: '100%', background: '#020617', border: '1px solid #334155', color: '#fff', padding: 8, borderRadius: 4, marginTop: 4, minHeight: 60, fontSize: 12 }}
              />
            </label>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 16 }}>
              <button
                type="button"
                onClick={() => { setSelectedHospital(null); setActionType(''); setReason(''); }}
                style={{ background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 14px', borderRadius: 4, cursor: 'pointer', fontSize: 12 }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={executeAction}
                disabled={busy}
                style={{ background: '#0284c7', border: 'none', color: '#fff', padding: '6px 16px', borderRadius: 4, cursor: 'pointer', fontWeight: 600, fontSize: 12 }}
              >
                {busy ? 'Processing...' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
