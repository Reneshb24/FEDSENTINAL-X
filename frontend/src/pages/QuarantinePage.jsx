import React, { useState, useEffect, useMemo } from 'react'
import {
  ShieldAlert,
  ShieldCheck,
  AlertOctagon,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Building2,
  FileCode,
  ArrowRight,
  Lock,
  Unlock,
  AlertTriangle,
} from 'lucide-react'
import {
  apiFetch,
  parseEvidence,
  formatHash,
  formatDate,
  formatNumber,
  SecurityPageHeader,
  SecurityPhilosophyBanner,
} from './securityUtils'
import './pages.css'

export default function QuarantinePage({ data, token, onNavigate, onDataRefresh }) {
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []
  const hospitals = Array.isArray(data?.hospitals) ? data.hospitals : []
  const [selectedRoundId, setSelectedRoundId] = useState('')
  const [updates, setUpdates] = useState([])
  const [loading, setLoading] = useState(false)
  const [actionInProgress, setActionInProgress] = useState(false)
  const [actionError, setActionError] = useState('')
  const [actionSuccess, setActionSuccess] = useState('')

  // Modal dialog states
  const [overrideModal, setOverrideModal] = useState({
    isOpen: false,
    type: 'UPDATE_RELEASE', // 'UPDATE_RELEASE' | 'UPDATE_QUARANTINE' | 'HOSPITAL_QUARANTINE' | 'HOSPITAL_RELEASE'
    targetId: null,
    targetLabel: '',
    reason: '',
  })

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

  async function loadUpdates() {
    if (!activeRound?.id || !token) return
    try {
      setLoading(true)
      setActionError('')
      const res = await apiFetch(`/api/v1/security/rounds/${activeRound.id}/updates`, token)
      setUpdates(Array.isArray(res) ? res : [])
    } catch (err) {
      setActionError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUpdates()
  }, [activeRound?.id, token])

  const quarantinedUpdates = updates.filter((u) => u.detection_status === 'QUARANTINED')
  const acceptedUpdates = updates.filter((u) => u.detection_status !== 'QUARANTINED')
  const quarantinedHospitals = hospitals.filter(
    (h) => String(h.status).toUpperCase() === 'QUARANTINED',
  )

  async function handleConfirmAction() {
    if (!overrideModal.targetId) return
    try {
      setActionInProgress(true)
      setActionError('')
      setActionSuccess('')

      const reason = overrideModal.reason || 'Administrator explicit override.'

      if (overrideModal.type === 'UPDATE_RELEASE') {
        await apiFetch(`/api/v1/security/updates/${overrideModal.targetId}/release`, token, {
          method: 'POST',
          body: JSON.stringify({ reason }),
        })
        setActionSuccess(`Update ${overrideModal.targetLabel} released from quarantine.`)
      } else if (overrideModal.type === 'UPDATE_QUARANTINE') {
        await apiFetch(`/api/v1/security/updates/${overrideModal.targetId}/quarantine`, token, {
          method: 'POST',
          body: JSON.stringify({ reason }),
        })
        setActionSuccess(`Update ${overrideModal.targetLabel} placed in quarantine.`)
      } else if (overrideModal.type === 'HOSPITAL_QUARANTINE') {
        await apiFetch(`/api/v1/hospitals/${overrideModal.targetId}/quarantine`, token, {
          method: 'POST',
          body: JSON.stringify({ reason }),
        })
        setActionSuccess(`Hospital ${overrideModal.targetLabel} quarantined.`)
      } else if (overrideModal.type === 'HOSPITAL_RELEASE') {
        await apiFetch(`/api/v1/hospitals/${overrideModal.targetId}/release`, token, {
          method: 'POST',
          body: JSON.stringify({ reason }),
        })
        setActionSuccess(`Hospital ${overrideModal.targetLabel} released.`)
      }

      setOverrideModal({ isOpen: false, type: '', targetId: null, targetLabel: '', reason: '' })
      loadUpdates()
      onDataRefresh?.()
    } catch (err) {
      setActionError(err.message)
    } finally {
      setActionInProgress(false)
    }
  }

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="Quarantine & Containment Operations"
        subtitle="Manage update-level containment, node-level isolation, and audited administrative overrides."
        badgeText="SECURITY CONTROL / CONTAINMENT"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadUpdates}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="SEPARATION OF QUARANTINE DOMAINS"
        context="Update Quarantine != Hospital Quarantine != Trust Status. An update can be quarantined for high statistical divergence while the hospital remains active in the network. Every administrative override is explicitly reasoned and recorded in the immutable audit log."
      />

      {actionSuccess && (
        <div style={{ background: 'rgba(0, 230, 118, 0.1)', border: '1px solid #00e676', padding: '10px 16px', borderRadius: 6, marginBottom: 16, color: '#00e676' }}>
          ✓ {actionSuccess}
        </div>
      )}

      {actionError && (
        <div style={{ background: 'rgba(255, 59, 92, 0.1)', border: '1px solid #ff3b5c', padding: '10px 16px', borderRadius: 6, marginBottom: 16, color: '#ff3b5c' }}>
          ⚠ {actionError}
        </div>
      )}

      <div className="security-metrics-row">
        <div className="sec-stat-card crimson">
          <span className="sec-stat-label">QUARANTINED UPDATES</span>
          <span className="sec-stat-value">{quarantinedUpdates.length}</span>
          <span className="sec-stat-sub">Excluded from R-{activeRound?.round_number || '--'} aggregation</span>
        </div>

        <div className="sec-stat-card amber">
          <span className="sec-stat-label">QUARANTINED HOSPITALS</span>
          <span className="sec-stat-value">{quarantinedHospitals.length}</span>
          <span className="sec-stat-sub">Suspended from federation participation</span>
        </div>

        <div className="sec-stat-card emerald">
          <span className="sec-stat-label">ACCEPTED UPDATES</span>
          <span className="sec-stat-value">{acceptedUpdates.length}</span>
          <span className="sec-stat-sub">Eligible for safe aggregation</span>
        </div>

        <div className="sec-stat-card cyan">
          <span className="sec-stat-label">ACTIVE HOSPITALS</span>
          <span className="sec-stat-value">{hospitals.length - quarantinedHospitals.length}</span>
          <span className="sec-stat-sub">Total {hospitals.length} registered nodes</span>
        </div>
      </div>

      {/* Domain 1: Quarantined Updates Deck */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <AlertOctagon size={16} color="#ff3b5c" />
            Update-Level Quarantine Console ({quarantinedUpdates.length})
          </h2>
          <span className="sec-badge sec-badge-quarantined">AGGREGATION SHIELD ACTIVE</span>
        </div>

        <div className="sec-table-container">
          <table className="sec-table">
            <thead>
              <tr>
                <th>HOSPITAL NODE</th>
                <th>ARTIFACT HASH</th>
                <th>QUARANTINE REASON</th>
                <th>L2 ANOMALY SCORE</th>
                <th>TRUST STATUS</th>
                <th>TIMESTAMP</th>
                <th>ADMIN OVERRIDE ACTION</th>
              </tr>
            </thead>
            <tbody>
              {quarantinedUpdates.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '32px', color: '#8b949e' }}>
                    No updates currently quarantined in this round.
                  </td>
                </tr>
              ) : (
                quarantinedUpdates.map((u) => {
                  const ev = parseEvidence(u.evidence)
                  return (
                    <tr key={u.id} className="highlight-danger">
                      <td>
                        <strong>{u.hospital_code || 'NODE'}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>
                          {u.hospital_name || u.hospital_id}
                        </div>
                      </td>
                      <td>
                        <code>{formatHash(u.artifact_hash, 8)}</code>
                      </td>
                      <td>
                        <span style={{ color: '#ffb020', fontSize: '0.75rem' }}>
                          {ev.trust.reason || 'L2 statistical anomaly / robust z-score threshold triggered'}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontFamily: 'monospace', color: '#ff3b5c', fontWeight: 700 }}>
                          {formatNumber(ev.l2.anomaly_score, 1)} (z: {formatNumber(ev.l2.z_score, 1)}σ)
                        </span>
                      </td>
                      <td>
                        <span className="sec-badge sec-badge-review">
                          {u.trust_status || 'REVIEW'}
                        </span>
                      </td>
                      <td style={{ color: '#8b949e', fontSize: '0.75rem' }}>
                        {formatDate(u.submitted_at)}
                      </td>
                      <td>
                        <button
                          type="button"
                          className="security-btn security-btn-success"
                          style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                          onClick={() =>
                            setOverrideModal({
                              isOpen: true,
                              type: 'UPDATE_RELEASE',
                              targetId: u.id,
                              targetLabel: `${u.hospital_code} (${formatHash(u.artifact_hash, 6)})`,
                              reason: '',
                            })
                          }
                        >
                          <Unlock size={12} />
                          <span>RELEASE TO AGGREGATION</span>
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

      {/* Domain 2: Accepted Updates Manual Quarantine */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <ShieldCheck size={16} color="#00e676" />
            Active / Accepted Updates in Round R-{activeRound?.round_number || '--'}
          </h2>
          <span className="sec-badge sec-badge-accepted">COHORT POOL</span>
        </div>

        <div className="sec-table-container">
          <table className="sec-table">
            <thead>
              <tr>
                <th>HOSPITAL NODE</th>
                <th>HASH</th>
                <th>L2 SCORE</th>
                <th>DETECTION</th>
                <th>STATUS</th>
                <th>MANUAL CONTAINMENT</th>
              </tr>
            </thead>
            <tbody>
              {acceptedUpdates.map((u) => {
                const ev = parseEvidence(u.evidence)
                return (
                  <tr key={u.id}>
                    <td>
                      <strong>{u.hospital_code || 'NODE'}</strong>
                    </td>
                    <td>
                      <code>{formatHash(u.artifact_hash, 8)}</code>
                    </td>
                    <td>{formatNumber(ev.l2.anomaly_score, 1)}</td>
                    <td>
                      <span className="sec-badge sec-badge-pass">ACCEPTED</span>
                    </td>
                    <td>{u.trust_status || 'NORMAL'}</td>
                    <td>
                      <button
                        type="button"
                        className="security-btn security-btn-danger"
                        style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                        onClick={() =>
                          setOverrideModal({
                            isOpen: true,
                            type: 'UPDATE_QUARANTINE',
                            targetId: u.id,
                            targetLabel: `${u.hospital_code} (${formatHash(u.artifact_hash, 6)})`,
                            reason: '',
                          })
                        }
                      >
                        <Lock size={12} />
                        <span>QUARANTINE UPDATE</span>
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Domain 3: Hospital Node Quarantine Management */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <Building2 size={16} />
            Hospital Enclave Node Isolation Controls
          </h2>
          <span className="sec-badge sec-badge-info">FEDERATION MEMBERSHIP</span>
        </div>

        <div className="sec-table-container">
          <table className="sec-table">
            <thead>
              <tr>
                <th>HOSPITAL</th>
                <th>REGION</th>
                <th>LIFECYCLE STATUS</th>
                <th>FEDERATION ISOLATION CONTROL</th>
              </tr>
            </thead>
            <tbody>
              {hospitals.map((h) => {
                const isQuarantined = String(h.status).toUpperCase() === 'QUARANTINED'
                return (
                  <tr key={h.id}>
                    <td>
                      <strong>{h.code || 'HOSP'}</strong> &bull; {h.name}
                    </td>
                    <td>{h.region || 'Default'}</td>
                    <td>
                      <span
                        className={`sec-badge ${
                          isQuarantined ? 'sec-badge-quarantined' : 'sec-badge-accepted'
                        }`}
                      >
                        {h.status}
                      </span>
                    </td>
                    <td>
                      {isQuarantined ? (
                        <button
                          type="button"
                          className="security-btn security-btn-success"
                          style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                          onClick={() =>
                            setOverrideModal({
                              isOpen: true,
                              type: 'HOSPITAL_RELEASE',
                              targetId: h.id,
                              targetLabel: `${h.code} - ${h.name}`,
                              reason: '',
                            })
                          }
                        >
                          <Unlock size={12} />
                          <span>RESTORE HOSPITAL</span>
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="security-btn security-btn-danger"
                          style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                          onClick={() =>
                            setOverrideModal({
                              isOpen: true,
                              type: 'HOSPITAL_QUARANTINE',
                              targetId: h.id,
                              targetLabel: `${h.code} - ${h.name}`,
                              reason: '',
                            })
                          }
                        >
                          <Lock size={12} />
                          <span>QUARANTINE HOSPITAL</span>
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Admin Action Override Modal */}
      {overrideModal.isOpen && (
        <div
          className="sec-modal-backdrop"
          onClick={() => setOverrideModal({ ...overrideModal, isOpen: false })}
        >
          <div className="sec-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="sec-modal-header">
              <h3>
                {overrideModal.type.includes('RELEASE')
                  ? 'Confirm Administrative Release'
                  : 'Confirm Administrative Containment'}
              </h3>
              <button
                type="button"
                className="security-btn security-btn-secondary"
                onClick={() => setOverrideModal({ ...overrideModal, isOpen: false })}
              >
                ✕
              </button>
            </div>

            <div className="sec-modal-body">
              <p style={{ margin: 0, fontSize: '0.875rem', color: '#c9d1d9' }}>
                You are performing an audited override on target:{' '}
                <strong style={{ color: '#00e5ff' }}>{overrideModal.targetLabel}</strong>.
              </p>

              <div className="sec-form-group">
                <label>MANDATORY AUDIT REASON / JUSTIFICATION</label>
                <textarea
                  rows={3}
                  placeholder="State the clinical, operational, or forensic rationale for this action..."
                  value={overrideModal.reason}
                  onChange={(e) =>
                    setOverrideModal({ ...overrideModal, reason: e.target.value })
                  }
                />
              </div>

              <div
                style={{
                  background: 'rgba(255, 176, 32, 0.1)',
                  border: '1px solid rgba(255, 176, 32, 0.3)',
                  padding: 10,
                  borderRadius: 6,
                  fontSize: '0.75rem',
                  color: '#ffb020',
                }}
              >
                ⚠ This decision will be cryptographically logged to the immutable audit trail with your user identity and timestamp.
              </div>
            </div>

            <div className="sec-modal-footer">
              <button
                type="button"
                className="security-btn security-btn-secondary"
                onClick={() => setOverrideModal({ ...overrideModal, isOpen: false })}
                disabled={actionInProgress}
              >
                CANCEL
              </button>
              <button
                type="button"
                className={
                  overrideModal.type.includes('RELEASE')
                    ? 'security-btn security-btn-success'
                    : 'security-btn security-btn-danger'
                }
                onClick={handleConfirmAction}
                disabled={actionInProgress}
              >
                {actionInProgress ? 'LOGGING AUDIT...' : 'CONFIRM OVERRIDE'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
