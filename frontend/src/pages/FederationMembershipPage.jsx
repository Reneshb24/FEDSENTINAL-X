import React, { useState, useEffect } from 'react'
import { Network, Users, Plus, CheckCircle, XCircle, RefreshCw, ShieldCheck } from 'lucide-react'

const rawApi = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://127.0.0.1:8000'
const API = rawApi.replace(/\/+$/, '')

export default function FederationMembershipPage({ data, token, onDataRefresh }) {
  const [federations, setFederations] = useState([])
  const [selectedFedId, setSelectedFedId] = useState('')
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [assignModalOpen, setAssignModalOpen] = useState(false)
  const [selectedHospitalId, setSelectedHospitalId] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')

  const allHospitals = Array.isArray(data?.hospitals) ? data.hospitals : []

  async function loadFederationData() {
    setLoading(true)
    try {
      const resp = await fetch(`${API}/api/v1/federations`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const feds = await resp.json()
      const list = Array.isArray(feds) ? feds : []
      setFederations(list)

      const targetId = selectedFedId || (list[0]?.id || '')
      setSelectedFedId(targetId)

      if (targetId) {
        const memResp = await fetch(`${API}/api/v1/federations/${targetId}/memberships`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (memResp.ok) {
          const mems = await memResp.json()
          setMembers(Array.isArray(mems) ? mems : [])
        }
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadFederationData()
  }, [selectedFedId])

  async function handleAssignHospital() {
    if (!selectedHospitalId || !selectedFedId) return
    setBusy(true)
    setMessage('')
    try {
      const resp = await fetch(`${API}/api/v1/federations/${selectedFedId}/memberships`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ hospital_id: selectedHospitalId })
      })
      if (!resp.ok) {
        const d = await resp.json().catch(() => null)
        throw new Error(d?.detail || `Assignment failed (${resp.status})`)
      }
      setMessage('Successfully assigned hospital to federation cohort.')
      setAssignModalOpen(false)
      setSelectedHospitalId('')
      await loadFederationData()
      onDataRefresh?.()
    } catch (err) {
      alert(`Error: ${err.message}`)
    } finally {
      setBusy(false)
    }
  }

  const assignedHospitalIds = new Set(members.map(m => m.hospital_id))
  const unassignedEligible = allHospitals.filter(h => !assignedHospitalIds.has(h.id) && h.status === 'ACTIVE')

  return (
    <div className="page-container" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <div style={{ color: '#00e5ff', fontSize: 11, fontWeight: 700, letterSpacing: '0.1em' }}>
            FEDERATION / MEMBERSHIP ORCHESTRATION
          </div>
          <h1 style={{ fontSize: 26, margin: '4px 0', color: '#fff', display: 'flex', alignItems: 'center', gap: 10 }}>
            <Network size={26} color="#00e5ff" />
            Federation Cohort Membership
          </h1>
          <p style={{ color: '#94a3b8', fontSize: 13, margin: 0 }}>
            Manage approved institutional membership in global federated learning rounds.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={() => setAssignModalOpen(true)}
            style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#0284c7', border: 'none', color: '#fff', padding: '8px 14px', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: 12 }}
          >
            <Plus size={14} />
            Assign Hospital to Cohort
          </button>
          <button
            onClick={loadFederationData}
            disabled={loading}
            style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', padding: '8px 14px', borderRadius: 6, cursor: 'pointer' }}
          >
            <RefreshCw size={14} className={loading ? 'hp-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {message && (
        <div style={{ padding: '12px 16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', color: '#10b981', borderRadius: 6, marginBottom: 16, fontSize: 13 }}>
          {message}
        </div>
      )}

      {/* Cohort Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12, marginBottom: 20 }}>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '14px', borderRadius: 6 }}>
          <div style={{ color: '#64748b', fontSize: 11 }}>ACTIVE COHORT NODES</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#10b981', marginTop: 4 }}>
            {members.filter(m => m.status === 'ACTIVE').length}
          </div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Authorized for round participation</div>
        </div>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '14px', borderRadius: 6 }}>
          <div style={{ color: '#64748b', fontSize: 11 }}>TOTAL FEDERATIONS</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#38bdf8', marginTop: 4 }}>
            {federations.length}
          </div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Secure federated learning clusters</div>
        </div>
      </div>

      {/* Members Table */}
      <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#020617', borderBottom: '1px solid #1e293b', color: '#64748b' }}>
              <th style={{ padding: '12px 16px' }}>HOSPITAL CODE</th>
              <th style={{ padding: '12px 16px' }}>NAME</th>
              <th style={{ padding: '12px 16px' }}>MEMBERSHIP STATUS</th>
              <th style={{ padding: '12px 16px' }}>JOINED DATE</th>
            </tr>
          </thead>
          <tbody>
            {members.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ padding: 30, textAlign: 'center', color: '#64748b' }}>
                  No hospitals currently enrolled in this federation cohort.
                </td>
              </tr>
            ) : (
              members.map((m) => {
                const hosp = allHospitals.find(h => h.id === m.hospital_id)
                return (
                  <tr key={m.id || m.hospital_id} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 700, color: '#38bdf8' }}>
                      {hosp?.code || m.hospital_id}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#f8fafc', fontWeight: 600 }}>
                      {hosp?.name || 'Verified Institution'}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: 4,
                        fontSize: 10,
                        fontWeight: 700,
                        background: m.status === 'ACTIVE' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                        color: m.status === 'ACTIVE' ? '#10b981' : '#ef4444'
                      }}>
                        {m.status || 'ACTIVE'}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', color: '#94a3b8' }}>
                      {m.joined_at ? new Date(m.joined_at).toLocaleString() : '—'}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Assign Modal */}
      {assignModalOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, maxWidth: 440, width: '100%', padding: 24 }}>
            <h3 style={{ margin: '0 0 10px', color: '#f8fafc' }}>
              Assign Hospital to Federation Cohort
            </h3>
            <p style={{ color: '#cbd5e1', fontSize: 12 }}>
              Select an active approved hospital to enroll into the federated learning cohort.
            </p>

            <label style={{ display: 'block', fontSize: 11, color: '#94a3b8', marginTop: 12 }}>
              SELECT APPROVED HOSPITAL
              <select
                value={selectedHospitalId}
                onChange={(e) => setSelectedHospitalId(e.target.value)}
                style={{ width: '100%', background: '#020617', border: '1px solid #334155', color: '#fff', padding: 8, borderRadius: 4, marginTop: 4, fontSize: 12 }}
              >
                <option value="">-- Choose Hospital --</option>
                {unassignedEligible.map(h => (
                  <option key={h.id} value={h.id}>
                    {h.code} - {h.name}
                  </option>
                ))}
              </select>
            </label>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 20 }}>
              <button
                type="button"
                onClick={() => { setAssignModalOpen(false); setSelectedHospitalId(''); }}
                style={{ background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 14px', borderRadius: 4, cursor: 'pointer', fontSize: 12 }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleAssignHospital}
                disabled={busy || !selectedHospitalId}
                style={{ background: '#0284c7', border: 'none', color: '#fff', padding: '6px 16px', borderRadius: 4, cursor: 'pointer', fontWeight: 600, fontSize: 12 }}
              >
                {busy ? 'Assigning...' : 'Enroll Hospital'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
