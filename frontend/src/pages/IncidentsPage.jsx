import React, { useState, useEffect, useMemo } from 'react'
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Clock,
  UserCheck,
  FileText,
  RotateCcw,
  ArrowRight,
  Filter,
  Search,
  Sliders,
} from 'lucide-react'
import {
  apiFetch,
  formatHash,
  formatDate,
  formatNumber,
  SecurityPageHeader,
  SecurityPhilosophyBanner,
} from './securityUtils'
import './pages.css'

export default function IncidentsPage({ data, token, onNavigate, onDataRefresh }) {
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []
  const [selectedRoundId, setSelectedRoundId] = useState('')
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')

  // Incident state change modal
  const [editModal, setEditModal] = useState({
    isOpen: false,
    incident: null,
    newStatus: 'INVESTIGATING',
    notes: '',
  })
  const [updatingStatus, setUpdatingStatus] = useState(false)

  const activeRound = useMemo(() => {
    if (selectedRoundId) {
      return rounds.find((r) => r.id === selectedRoundId) || null
    }
    const running = rounds.find((r) => String(r.status).toUpperCase() === 'RUNNING')
    const completed = rounds.find((r) => String(r.status).toUpperCase() === 'COMPLETED')
    return running || completed || rounds[0] || null
  }, [selectedRoundId, rounds])

  useEffect(() => {
    if (activeRound && !selectedRoundId) {
      setSelectedRoundId(activeRound.id)
    }
  }, [activeRound, selectedRoundId])

  async function loadIncidents() {
    if (!activeRound?.id || !token) return
    try {
      setLoading(true)
      setError('')
      const res = await apiFetch(`/api/v1/security/rounds/${activeRound.id}/incidents`, token)
      setIncidents(Array.isArray(res) ? res : [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadIncidents()
  }, [activeRound?.id, token])

  const filteredIncidents = useMemo(() => {
    if (statusFilter === 'ALL') return incidents
    return incidents.filter((inc) => (inc.status || '').toUpperCase() === statusFilter)
  }, [incidents, statusFilter])

  async function handleUpdateIncidentStatus() {
    if (!editModal.incident?.id) return
    try {
      setUpdatingStatus(true)
      await apiFetch(`/api/v1/security/incidents/${editModal.incident.id}/status`, token, {
        method: 'POST',
        body: JSON.stringify({
          status: editModal.newStatus,
          resolution_notes: editModal.notes || undefined,
        }),
      })

      setEditModal({ isOpen: false, incident: null, newStatus: 'INVESTIGATING', notes: '' })
      loadIncidents()
      onDataRefresh?.()
    } catch (err) {
      alert(`Error updating incident: ${err.message}`)
    } finally {
      setUpdatingStatus(false)
    }
  }

  const criticalCount = incidents.filter(
    (i) => (i.severity || '').toUpperCase() === 'CRITICAL',
  ).length
  const openCount = incidents.filter(
    (i) => ['OPEN', 'INVESTIGATING'].includes((i.status || '').toUpperCase()),
  ).length
  const resolvedCount = incidents.filter(
    (i) => ['RESOLVED', 'CLOSED', 'FALSE_POSITIVE'].includes((i.status || '').toUpperCase()),
  ).length

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="Incident Response & Threat Management Center"
        subtitle="Operational triage, root-cause forensic tracking, and lifecycle disposition for federation security incidents."
        badgeText="SECURITY OPERATIONS / INCIDENTS"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadIncidents}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="ACTIONABLE INVESTIGATION != PRESUMPTION OF GUILT"
        context="An incident documents observable security anomalies and coordinates investigative workflow. Incidents can be resolved as FALSE_POSITIVE or CLOSED with audited explanations, maintaining institutional trust without ignoring risk signals."
      />

      <div className="security-metrics-row">
        <div className="sec-stat-card crimson">
          <span className="sec-stat-label">ACTIVE / OPEN INCIDENTS</span>
          <span className="sec-stat-value">{openCount}</span>
          <span className="sec-stat-sub">Requiring analyst investigation</span>
        </div>

        <div className="sec-stat-card amber">
          <span className="sec-stat-label">CRITICAL SEVERITY</span>
          <span className="sec-stat-value">{criticalCount}</span>
          <span className="sec-stat-sub">High confidence threat signals</span>
        </div>

        <div className="sec-stat-card emerald">
          <span className="sec-stat-label">RESOLVED / CONTAINED</span>
          <span className="sec-stat-value">{resolvedCount}</span>
          <span className="sec-stat-sub">Closed with forensic audit trail</span>
        </div>

        <div className="sec-stat-card cyan">
          <span className="sec-stat-label">TOTAL ROUND INCIDENTS</span>
          <span className="sec-stat-value">{incidents.length}</span>
          <span className="sec-stat-sub">In Round R-{activeRound?.round_number || '--'}</span>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <ShieldAlert size={16} />
            Security Incidents ({filteredIncidents.length})
          </h2>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>STATUS FILTER:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{
                background: '#161b22',
                border: '1px solid #30363d',
                borderRadius: 4,
                padding: '4px 8px',
                color: '#c9d1d9',
                fontSize: '0.75rem',
                outline: 'none',
              }}
            >
              <option value="ALL">ALL STATUSES</option>
              <option value="OPEN">OPEN</option>
              <option value="INVESTIGATING">INVESTIGATING</option>
              <option value="CONTAINED">CONTAINED</option>
              <option value="RESOLVED">RESOLVED</option>
              <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
              <option value="CLOSED">CLOSED</option>
            </select>
          </div>
        </div>

        <div className="sec-table-container">
          <table className="sec-table">
            <thead>
              <tr>
                <th>INCIDENT CODE</th>
                <th>HOSPITAL NODE</th>
                <th>SEVERITY</th>
                <th>THREAT CLASSIFICATION</th>
                <th>STATUS</th>
                <th>RECOMMENDED ACTION</th>
                <th>RISK / CONFIDENCE</th>
                <th>CREATED</th>
                <th>LIFECYCLE ACTION</th>
              </tr>
            </thead>
            <tbody>
              {filteredIncidents.length === 0 ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '32px', color: '#8b949e' }}>
                    {loading ? 'Querying incident database...' : 'No incidents matching criteria in this round.'}
                  </td>
                </tr>
              ) : (
                filteredIncidents.map((inc) => {
                  const severity = (inc.severity || '').toUpperCase()
                  const status = (inc.status || '').toUpperCase()
                  const isCrit = severity === 'CRITICAL'
                  const isOpen = ['OPEN', 'INVESTIGATING'].includes(status)

                  return (
                    <tr key={inc.id} className={isCrit && isOpen ? 'highlight-danger' : ''}>
                      <td>
                        <strong style={{ color: '#00e5ff' }}>{inc.incident_code || inc.id.slice(0, 8)}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>{inc.title}</div>
                      </td>
                      <td>
                        <strong>{inc.hospital_code || 'NODE'}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>
                          {inc.hospital_name || inc.hospital_id}
                        </div>
                      </td>
                      <td>
                        <span
                          className={`sec-badge ${
                            isCrit
                              ? 'sec-badge-quarantined'
                              : severity === 'HIGH'
                                ? 'sec-badge-warning'
                                : 'sec-badge-info'
                          }`}
                        >
                          {inc.severity}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.75rem', fontFamily: 'monospace' }}>
                          {inc.threat_type || 'ANOMALOUS_UPDATE'}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`sec-badge ${
                            isOpen
                              ? 'sec-badge-quarantined'
                              : status === 'CONTAINED'
                                ? 'sec-badge-warning'
                                : 'sec-badge-pass'
                          }`}
                        >
                          {inc.status}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.75rem', color: '#ffb020' }}>
                          {inc.recommended_action || 'MONITOR'}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontFamily: 'monospace' }}>
                          {formatNumber(inc.risk_score, 1)} / {formatNumber(inc.confidence, 2)}
                        </span>
                      </td>
                      <td style={{ color: '#8b949e', fontSize: '0.75rem' }}>
                        {formatDate(inc.created_at)}
                      </td>
                      <td>
                        <button
                          type="button"
                          className="security-btn security-btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '0.7rem' }}
                          onClick={() =>
                            setEditModal({
                              isOpen: true,
                              incident: inc,
                              newStatus: inc.status || 'INVESTIGATING',
                              notes: inc.resolution_notes || '',
                            })
                          }
                        >
                          <span>UPDATE STATUS</span>
                        </button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Incident Status Edit Modal */}
      {editModal.isOpen && editModal.incident && (
        <div className="sec-modal-backdrop" onClick={() => setEditModal({ ...editModal, isOpen: false })}>
          <div className="sec-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="sec-modal-header">
              <h3>Update Incident Status: {editModal.incident.incident_code || editModal.incident.title}</h3>
              <button
                type="button"
                className="security-btn security-btn-secondary"
                onClick={() => setEditModal({ ...editModal, isOpen: false })}
              >
                ✕
              </button>
            </div>
            <div className="sec-modal-body">
              <div className="sec-form-group">
                <label>NEW LIFECYCLE STATUS</label>
                <select
                  value={editModal.newStatus}
                  onChange={(e) => setEditModal({ ...editModal, newStatus: e.target.value })}
                >
                  <option value="OPEN">OPEN (Unassigned)</option>
                  <option value="INVESTIGATING">INVESTIGATING (Analyst In Progress)</option>
                  <option value="CONTAINED">CONTAINED (Update Quarantined)</option>
                  <option value="RESOLVED">RESOLVED (Mitigated & Audited)</option>
                  <option value="FALSE_POSITIVE">FALSE_POSITIVE (Clinical Variance Verified)</option>
                  <option value="CLOSED">CLOSED (Archived)</option>
                </select>
              </div>

              <div className="sec-form-group">
                <label>RESOLUTION / INVESTIGATION NOTES</label>
                <textarea
                  rows={4}
                  placeholder="Document findings, root cause, or clinical justification..."
                  value={editModal.notes}
                  onChange={(e) => setEditModal({ ...editModal, notes: e.target.value })}
                />
              </div>

              <div
                style={{
                  background: 'rgba(0, 229, 255, 0.08)',
                  border: '1px solid rgba(0, 229, 255, 0.25)',
                  padding: 10,
                  borderRadius: 6,
                  fontSize: '0.75rem',
                  color: '#c9d1d9',
                }}
              >
                ℹ Changing status records an immutable audit event under <code>INCIDENT_STATUS_UPDATED</code>.
              </div>
            </div>

            <div className="sec-modal-footer">
              <button
                type="button"
                className="security-btn security-btn-secondary"
                onClick={() => setEditModal({ ...editModal, isOpen: false })}
                disabled={updatingStatus}
              >
                CANCEL
              </button>
              <button
                type="button"
                className="security-btn security-btn-primary"
                onClick={handleUpdateIncidentStatus}
                disabled={updatingStatus}
              >
                {updatingStatus ? 'COMMITTING...' : 'SAVE TRANSITION'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
