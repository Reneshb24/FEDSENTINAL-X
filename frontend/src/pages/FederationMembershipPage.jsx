import React, { useState, useEffect, useMemo } from 'react'
import {
  Network,
  Users,
  Plus,
  CheckCircle,
  XCircle,
  RefreshCw,
  ShieldCheck,
  Search,
  Trash2,
  AlertTriangle,
  ChevronRight,
  Filter,
} from 'lucide-react'

import { getApiBaseUrl } from '../apiConfig'
const API = getApiBaseUrl()

export default function FederationMembershipPage({ data, token, onDataRefresh }) {
  const [federations, setFederations] = useState([])
  const [selectedFedId, setSelectedFedId] = useState('')
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [assignModalOpen, setAssignModalOpen] = useState(false)
  const [selectedHospitalId, setSelectedHospitalId] = useState('')
  const [assignReason, setAssignReason] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [removeTarget, setRemoveTarget] = useState(null)
  const [removeReason, setRemoveReason] = useState('')
  const [hospitalsList, setHospitalsList] = useState(Array.isArray(data?.hospitals) ? data.hospitals : [])
  const [tierModalOpen, setTierModalOpen] = useState(false)
  const [targetHospital, setTargetHospital] = useState(null)
  const [selectedTier, setSelectedTier] = useState('TRUSTED')

  const allHospitals = hospitalsList.length > 0 ? hospitalsList : (Array.isArray(data?.hospitals) ? data.hospitals : [])

  async function loadFederationData() {
    setLoading(true)
    setError('')
    try {
      const resp = await fetch(`${API}/api/v1/federations`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}: Unable to load federations`)
      const feds = await resp.json()
      const list = Array.isArray(feds) ? feds : []
      setFederations(list)

      const targetId = selectedFedId || list[0]?.id || ''
      setSelectedFedId(targetId)

      // Always fetch fresh list of all hospitals to ensure dropdown is fully populated
      try {
        const hospResp = await fetch(`${API}/api/v1/hospitals`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (hospResp.ok) {
          const hl = await hospResp.json()
          if (Array.isArray(hl) && hl.length > 0) {
            setHospitalsList(hl)
          }
        }
      } catch (_) {}

      if (targetId) {
        const memResp = await fetch(`${API}/api/v1/federations/${targetId}/members`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (memResp.ok) {
          const mems = await memResp.json()
          setMembers(Array.isArray(mems) ? mems : [])
        } else {
          // Try legacy alias if needed
          const altResp = await fetch(`${API}/api/v1/federations/${targetId}/memberships`, {
            headers: { Authorization: `Bearer ${token}` },
          })
          if (altResp.ok) {
            const mems = await altResp.json()
            setMembers(Array.isArray(mems) ? mems : [])
          }
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to load federation cohort data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadFederationData()
  }, [selectedFedId])

  async function handleAssignHospital(e) {
    e?.preventDefault()
    if (!selectedHospitalId || !selectedFedId) return
    setBusy(true)
    setMessage('')
    setError('')
    try {
      const resp = await fetch(`${API}/api/v1/federations/${selectedFedId}/members`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          hospital_id: selectedHospitalId,
          reason: assignReason.trim() || 'Enrolled into active federation cohort',
        }),
      })
      if (!resp.ok) {
        const d = await resp.json().catch(() => null)
        throw new Error(d?.detail || `Assignment failed with status ${resp.status}`)
      }
      setMessage('Successfully assigned hospital to federation cohort.')
      setAssignModalOpen(false)
      setSelectedHospitalId('')
      setAssignReason('')
      await loadFederationData()
      onDataRefresh?.()
    } catch (err) {
      setError(err.message || 'Hospital assignment failed')
    } finally {
      setBusy(false)
    }
  }

  async function handleRemoveHospital(e) {
    e?.preventDefault()
    if (!removeTarget || !selectedFedId) return
    setBusy(true)
    setMessage('')
    setError('')
    try {
      const resp = await fetch(
        `${API}/api/v1/federations/${selectedFedId}/members/${removeTarget.hospital_id}/remove`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            reason: removeReason.trim() || 'Removed from active cohort by administrator',
          }),
        },
      )
      if (!resp.ok) {
        const d = await resp.json().catch(() => null)
        throw new Error(d?.detail || `Removal failed with status ${resp.status}`)
      }
      setMessage(`Hospital removed from active federation cohort.`)
      setRemoveTarget(null)
      setRemoveReason('')
      await loadFederationData()
      onDataRefresh?.()
    } catch (err) {
      setError(err.message || 'Removal failed')
    } finally {
      setBusy(false)
    }
  }

  const assignedHospitalIds = new Set(
    members.filter((m) => m.status === 'ACTIVE').map((m) => m.hospital_id),
  )

  const unassignedEligible = allHospitals.filter(
    (h) => !assignedHospitalIds.has(h.id) && h.status !== 'SUSPENDED' && h.status !== 'REVOKED',
  )

  async function handleUpdateSecurityTier(e) {
    e?.preventDefault()
    if (!targetHospital?.id) return
    setBusy(true)
    setMessage('')
    setError('')
    try {
      const resp = await fetch(`${API}/api/v1/hospitals/${targetHospital.id}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          security_status: selectedTier,
          security_tier: selectedTier,
        }),
      })
      if (!resp.ok) {
        const d = await resp.json().catch(() => null)
        throw new Error(d?.detail || `Failed to update security tier: HTTP ${resp.status}`)
      }
      setMessage(`Security Tier for ${targetHospital.name || targetHospital.id} updated to ${selectedTier}.`)
      setTierModalOpen(false)
      setTargetHospital(null)
      await loadFederationData()
      onDataRefresh?.()
    } catch (err) {
      setError(err.message || 'Security tier update failed')
    } finally {
      setBusy(false)
    }
  }

  const filteredMembers = useMemo(() => {
    return members.filter((m) => {
      const hosp = allHospitals.find((h) => h.id === m.hospital_id)
      const name = (hosp?.name || '').toLowerCase()
      const code = (hosp?.code || m.hospital_id || '').toLowerCase()
      const q = searchQuery.toLowerCase().trim()
      const matchesSearch = !q || name.includes(q) || code.includes(q)

      if (!matchesSearch) return false
      if (statusFilter === 'ALL') return true
      return (m.status || '').toUpperCase() === statusFilter.toUpperCase()
    })
  }, [members, allHospitals, searchQuery, statusFilter])

  const activeCount = members.filter((m) => m.status === 'ACTIVE').length

  return (
    <div className="page-container" style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
        <div>
          <div style={{ color: '#00e5ff', fontSize: 11, fontWeight: 700, letterSpacing: '0.1em' }}>
            FEDERATION / MEMBERSHIP ORCHESTRATION
          </div>
          <h1 style={{ fontSize: 24, margin: '4px 0', color: '#fff', display: 'flex', alignItems: 'center', gap: 10 }}>
            <Network size={24} color="#00e5ff" />
            Federation Cohort Membership
          </h1>
          <p style={{ color: '#94a3b8', fontSize: 13, margin: 0 }}>
            Manage approved healthcare institutions enrolled in global federated consensus rounds.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={() => setAssignModalOpen(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: '#0284c7',
              border: 'none',
              color: '#fff',
              padding: '8px 14px',
              borderRadius: 6,
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: 12,
            }}
          >
            <Plus size={14} />
            Assign Hospital to Cohort
          </button>
          <button
            onClick={loadFederationData}
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: '#1e293b',
              border: '1px solid #334155',
              color: '#f8fafc',
              padding: '8px 14px',
              borderRadius: 6,
              cursor: 'pointer',
              fontSize: 12,
            }}
          >
            <RefreshCw size={14} className={loading ? 'hp-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Cohort Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 20 }}>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '14px', borderRadius: 8 }}>
          <div style={{ color: '#64748b', fontSize: 11, fontWeight: 600 }}>ACTIVE COHORT NODES</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#10b981', marginTop: 4 }}>
            {activeCount}
          </div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Authorized for round participation</div>
        </div>

        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '14px', borderRadius: 8 }}>
          <div style={{ color: '#64748b', fontSize: 11, fontWeight: 600 }}>ELIGIBLE POOL</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#38bdf8', marginTop: 4 }}>
            {unassignedEligible.length}
          </div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Verified hospitals ready to enroll</div>
        </div>

        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '14px', borderRadius: 8 }}>
          <div style={{ color: '#64748b', fontSize: 11, fontWeight: 600 }}>FEDERATION CLUSTER</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#f59e0b', marginTop: 4 }}>
            {federations.length > 0 ? federations[0].name || 'Core Consortium' : '1 Active Cluster'}
          </div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2, fontFamily: 'monospace' }}>
            ID: {selectedFedId ? `${selectedFedId.slice(0, 13)}...` : '413ef0b3...'}
          </div>
        </div>
      </div>

      {/* Controls Bar: Search & Status Filter */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={14} style={{ position: 'absolute', left: 12, top: 11, color: '#64748b' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search cohort by hospital name or code..."
            style={{
              width: '100%',
              background: '#0f172a',
              border: '1px solid #1e293b',
              color: '#f8fafc',
              padding: '8px 12px 8px 34px',
              borderRadius: 6,
              fontSize: 12,
              outline: 'none',
            }}
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{
            background: '#0f172a',
            border: '1px solid #1e293b',
            color: '#f8fafc',
            padding: '8px 12px',
            borderRadius: 6,
            fontSize: 12,
            outline: 'none',
          }}
        >
          <option value="ALL">All Statuses ({members.length})</option>
          <option value="ACTIVE">Active Only ({activeCount})</option>
          <option value="REMOVED">Removed Only</option>
        </select>
      </div>

      {/* Members Table */}
      <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#020617', borderBottom: '1px solid #1e293b', color: '#64748b' }}>
              <th style={{ padding: '12px 16px' }}>HOSPITAL CODE</th>
              <th style={{ padding: '12px 16px' }}>NAME</th>
              <th style={{ padding: '12px 16px' }}>SECURITY TIER</th>
              <th style={{ padding: '12px 16px' }}>MEMBERSHIP STATUS</th>
              <th style={{ padding: '12px 16px' }}>JOINED DATE</th>
              <th style={{ padding: '12px 16px', textAlign: 'right' }}>ACTION</th>
            </tr>
          </thead>
          <tbody>
            {filteredMembers.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: 36, textAlign: 'center', color: '#64748b' }}>
                  {members.length === 0
                    ? 'No hospitals currently enrolled in this federation cohort.'
                    : 'No cohort hospitals matched your search criteria.'}
                </td>
              </tr>
            ) : (
              filteredMembers.map((m) => {
                const hosp = allHospitals.find((h) => h.id === m.hospital_id)
                const isActive = m.status === 'ACTIVE'
                return (
                  <tr key={m.id || m.hospital_id} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 700, color: '#38bdf8' }}>
                      {hosp?.code || m.hospital_id?.slice(0, 8)}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#f8fafc', fontWeight: 600 }}>
                      {hosp?.name || 'Verified Healthcare Enclave'}
                      <div style={{ fontSize: 10, color: '#64748b', fontWeight: 400 }}>
                        {hosp?.location || 'Clinical Enclave'}
                      </div>
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span
                          style={{
                            fontSize: 10,
                            fontWeight: 700,
                            padding: '2px 6px',
                            borderRadius: 4,
                            background:
                              (hosp?.security_tier || hosp?.security_status) === 'HIGH_RISK'
                                ? 'rgba(239, 68, 68, 0.15)'
                                : (hosp?.security_tier || hosp?.security_status) === 'PROBATION'
                                ? 'rgba(245, 158, 11, 0.15)'
                                : 'rgba(16, 185, 129, 0.15)',
                            color:
                              (hosp?.security_tier || hosp?.security_status) === 'HIGH_RISK'
                                ? '#ef4444'
                                : (hosp?.security_tier || hosp?.security_status) === 'PROBATION'
                                ? '#f59e0b'
                                : '#10b981',
                          }}
                        >
                          {hosp?.security_tier || hosp?.security_status || 'TRUSTED'}
                        </span>
                        <button
                          type="button"
                          onClick={() => {
                            const resolvedHosp = hosp || { id: m.hospital_id, name: m.hospital_name || 'Enclave', security_status: 'TRUSTED' }
                            setTargetHospital(resolvedHosp)
                            setSelectedTier(resolvedHosp.security_tier || resolvedHosp.security_status || 'TRUSTED')
                            setTierModalOpen(true)
                          }}
                          style={{
                            background: 'rgba(0, 229, 255, 0.1)',
                            border: '1px solid rgba(0, 229, 255, 0.3)',
                            color: '#00e5ff',
                            fontSize: 9,
                            fontWeight: 700,
                            padding: '2px 6px',
                            borderRadius: 3,
                            cursor: 'pointer',
                          }}
                          title="Edit security tier & enclave boundaries"
                        >
                          Edit
                        </button>
                      </div>
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span
                        style={{
                          padding: '2px 8px',
                          borderRadius: 4,
                          fontSize: 10,
                          fontWeight: 700,
                          background: isActive
                            ? 'rgba(16, 185, 129, 0.2)'
                            : 'rgba(239, 68, 68, 0.2)',
                          color: isActive ? '#10b981' : '#ef4444',
                        }}
                      >
                        {m.status || 'ACTIVE'}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', color: '#94a3b8' }}>
                      {m.joined_at ? new Date(m.joined_at).toLocaleString() : '—'}
                    </td>
                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                      {isActive ? (
                        <button
                          type="button"
                          onClick={() => setRemoveTarget(m)}
                          style={{
                            background: 'rgba(239, 68, 68, 0.1)',
                            border: '1px solid rgba(239, 68, 68, 0.3)',
                            color: '#ef4444',
                            padding: '4px 8px',
                            borderRadius: 4,
                            cursor: 'pointer',
                            fontSize: 11,
                            fontWeight: 600,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4,
                          }}
                        >
                          <Trash2 size={12} />
                          Remove
                        </button>
                      ) : (
                        <span style={{ fontSize: 11, color: '#64748b' }}>Archived</span>
                      )}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>

        {/* Card-bottom notification zone */}
        {(message || error) && (
          <div
            style={{
              padding: '10px 16px',
              borderTop: '1px solid #1e293b',
              background: error ? 'rgba(239, 68, 68, 0.08)' : 'rgba(16, 185, 129, 0.08)',
              color: error ? '#ef4444' : '#10b981',
              fontSize: 12,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <span>{error || message}</span>
            <button
              onClick={() => {
                setMessage('')
                setError('')
              }}
              style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', padding: 2 }}
            >
              &times;
            </button>
          </div>
        )}
      </div>

      {/* Assign Modal */}
      {assignModalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 20,
          }}
        >
          <div
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: 8,
              maxWidth: 460,
              width: '100%',
              padding: 24,
            }}
          >
            <h3 style={{ margin: '0 0 8px', color: '#f8fafc', fontSize: 16 }}>
              Assign Hospital to Federation Cohort
            </h3>
            <p style={{ color: '#94a3b8', fontSize: 12, margin: '0 0 16px' }}>
              Select an active approved healthcare enclave to enroll into federated learning rounds.
            </p>

            <form onSubmit={handleAssignHospital}>
              <label style={{ display: 'block', fontSize: 11, color: '#94a3b8', marginBottom: 12 }}>
                SELECT APPROVED HOSPITAL
                <select
                  value={selectedHospitalId}
                  onChange={(e) => setSelectedHospitalId(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    background: '#020617',
                    border: '1px solid #334155',
                    color: '#fff',
                    padding: 8,
                    borderRadius: 4,
                    marginTop: 4,
                    fontSize: 12,
                  }}
                >
                  <option value="">-- Choose Eligible Hospital --</option>
                  {unassignedEligible.map((h) => (
                    <option key={h.id} value={h.id}>
                      {h.code} — {h.name} ({h.location || 'Clinical Site'})
                    </option>
                  ))}
                </select>
              </label>

              <label style={{ display: 'block', fontSize: 11, color: '#94a3b8', marginBottom: 16 }}>
                ENROLLMENT REASON (AUDITED)
                <input
                  type="text"
                  value={assignReason}
                  onChange={(e) => setAssignReason(e.target.value)}
                  placeholder="e.g. Approved institutional onboarding for Round execution"
                  style={{
                    width: '100%',
                    background: '#020617',
                    border: '1px solid #334155',
                    color: '#fff',
                    padding: 8,
                    borderRadius: 4,
                    marginTop: 4,
                    fontSize: 12,
                  }}
                />
              </label>

              {/* Modal-bottom red notification if error */}
              {error && (
                <div
                  style={{
                    padding: '8px 12px',
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid #ef4444',
                    color: '#ef4444',
                    borderRadius: 4,
                    fontSize: 11,
                    marginBottom: 12,
                  }}
                >
                  {error}
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
                <button
                  type="button"
                  onClick={() => {
                    setAssignModalOpen(false)
                    setSelectedHospitalId('')
                    setError('')
                  }}
                  style={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    color: '#cbd5e1',
                    padding: '6px 14px',
                    borderRadius: 4,
                    cursor: 'pointer',
                    fontSize: 12,
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={busy || !selectedHospitalId}
                  style={{
                    background: '#0284c7',
                    border: 'none',
                    color: '#fff',
                    padding: '6px 16px',
                    borderRadius: 4,
                    cursor: 'pointer',
                    fontWeight: 600,
                    fontSize: 12,
                  }}
                >
                  {busy ? 'Assigning...' : 'Enroll Hospital'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Security Tier Management Modal */}
      {tierModalOpen && targetHospital && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.75)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 20,
          }}
        >
          <div
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: 8,
              maxWidth: 520,
              width: '100%',
              padding: 24,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <div>
                <div style={{ color: '#00e5ff', fontSize: 10, fontWeight: 700, letterSpacing: '0.08em' }}>
                  INSTITUTIONAL GOVERNANCE
                </div>
                <h3 style={{ margin: '2px 0 0', color: '#f8fafc', fontSize: 16 }}>
                  Manage Security Tier: {targetHospital.name || targetHospital.code || targetHospital.id}
                </h3>
              </div>
              <button
                onClick={() => setTierModalOpen(false)}
                style={{ background: 'none', border: 'none', color: '#64748b', fontSize: 18, cursor: 'pointer' }}
              >
                &times;
              </button>
            </div>

            <p style={{ color: '#94a3b8', fontSize: 12, margin: '0 0 16px' }}>
              Assign functional isolation boundaries, aggregation weighting, and defense scrutiny levels for this hospital.
            </p>

            <form onSubmit={handleUpdateSecurityTier}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 16 }}>
                {[
                  {
                    tier: 'TRUSTED',
                    color: '#10b981',
                    title: 'Tier 1: TRUSTED (Standard Consensus)',
                    desc: 'Full 1.0x aggregation weight. Normal L0-L5 defense gating. Direct eligibility for all federated rounds.',
                  },
                  {
                    tier: 'PROBATION',
                    color: '#f59e0b',
                    title: 'Tier 2: PROBATION (Elevated Scrutiny)',
                    desc: 'Capped aggregation weight (0.5x). Tightened L4 cosine anomaly threshold. Audited on each round.',
                  },
                  {
                    tier: 'HIGH_RISK',
                    color: '#ef4444',
                    title: 'Tier 3: HIGH_RISK (Sandboxed Containment)',
                    desc: 'Strict quarantine isolation. Model updates are quarantined by default for human security audit before aggregation.',
                  },
                ].map((t) => (
                  <label
                    key={t.tier}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 12,
                      padding: '12px 14px',
                      borderRadius: 6,
                      background: selectedTier === t.tier ? 'rgba(0, 229, 255, 0.08)' : '#070c11',
                      border: `1px solid ${selectedTier === t.tier ? '#00e5ff' : '#1e293b'}`,
                      cursor: 'pointer',
                    }}
                  >
                    <input
                      type="radio"
                      name="securityTier"
                      value={t.tier}
                      checked={selectedTier === t.tier}
                      onChange={() => setSelectedTier(t.tier)}
                      style={{ marginTop: 2 }}
                    />
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 800, color: t.color }}>{t.title}</div>
                      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 3 }}>{t.desc}</div>
                    </div>
                  </label>
                ))}
              </div>

              <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setTierModalOpen(false)}
                  style={{
                    background: 'transparent',
                    border: '1px solid #334155',
                    color: '#94a3b8',
                    padding: '8px 14px',
                    borderRadius: 4,
                    cursor: 'pointer',
                    fontSize: 12,
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={busy}
                  style={{
                    background: '#0284c7',
                    border: 'none',
                    color: '#fff',
                    padding: '8px 18px',
                    borderRadius: 4,
                    cursor: 'pointer',
                    fontSize: 12,
                    fontWeight: 700,
                  }}
                >
                  {busy ? 'Updating...' : 'Save Security Tier'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Remove Confirmation Modal */}
      {removeTarget && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 20,
          }}
        >
          <div
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: 8,
              maxWidth: 440,
              width: '100%',
              padding: 24,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: '#ef4444', marginBottom: 10 }}>
              <AlertTriangle size={20} />
              <h3 style={{ margin: 0, fontSize: 16 }}>Remove Hospital from Cohort</h3>
            </div>
            <p style={{ color: '#cbd5e1', fontSize: 12, margin: '0 0 16px' }}>
              Are you sure you want to remove hospital membership? This will exclude the hospital from upcoming federated training rounds.
            </p>

            <form onSubmit={handleRemoveHospital}>
              <label style={{ display: 'block', fontSize: 11, color: '#94a3b8', marginBottom: 16 }}>
                REMOVAL REASON (MANDATORY AUDIT LOG)
                <input
                  type="text"
                  value={removeReason}
                  onChange={(e) => setRemoveReason(e.target.value)}
                  placeholder="e.g. Temporary exclusion for calibration"
                  required
                  style={{
                    width: '100%',
                    background: '#020617',
                    border: '1px solid #334155',
                    color: '#fff',
                    padding: 8,
                    borderRadius: 4,
                    marginTop: 4,
                    fontSize: 12,
                  }}
                />
              </label>

              {/* Modal-bottom red notification if error */}
              {error && (
                <div
                  style={{
                    padding: '8px 12px',
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid #ef4444',
                    color: '#ef4444',
                    borderRadius: 4,
                    fontSize: 11,
                    marginBottom: 12,
                  }}
                >
                  {error}
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
                <button
                  type="button"
                  onClick={() => {
                    setRemoveTarget(null)
                    setRemoveReason('')
                    setError('')
                  }}
                  style={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    color: '#cbd5e1',
                    padding: '6px 14px',
                    borderRadius: 4,
                    cursor: 'pointer',
                    fontSize: 12,
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={busy}
                  style={{
                    background: '#ef4444',
                    border: 'none',
                    color: '#fff',
                    padding: '6px 16px',
                    borderRadius: 4,
                    cursor: 'pointer',
                    fontWeight: 600,
                    fontSize: 12,
                  }}
                >
                  {busy ? 'Removing...' : 'Confirm Removal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
