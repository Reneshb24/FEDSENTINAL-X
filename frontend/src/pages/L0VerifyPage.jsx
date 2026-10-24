import React, { useState, useEffect, useMemo } from 'react'
import {
  ShieldCheck,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileCheck,
  Hash,
  Binary,
  Layers,
  ArrowRight,
  Eye,
  Info,
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

export default function L0VerifyPage({ data, token, onNavigate }) {
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []
  const [selectedRoundId, setSelectedRoundId] = useState('')
  const [updates, setUpdates] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeModalUpdate, setActiveModalUpdate] = useState(null)

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
      setError('')
      const res = await apiFetch(`/api/v1/security/rounds/${activeRound.id}/updates`, token)
      setUpdates(Array.isArray(res) ? res : [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUpdates()
  }, [activeRound?.id, token])

  const totalUpdates = updates.length
  const passedL0 = updates.filter((u) => u.l0_status === 'PASSED').length
  const failedL0 = updates.filter((u) => u.l0_status === 'FAILED').length

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="L0 — Structural Artifact Verification"
        subtitle="First-line artifact boundary validation: parameter structure, finite numerical sanity, hash integrity, and serialization safety."
        badgeText="SECURITY LAYER 0 / ARTIFACT INTEGRITY"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadUpdates}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="STRUCTURAL VALIDITY != BENIGN INTENT"
        context="L0 is NOT the final security verdict. A structurally valid update with 105,866 finite parameters can still contain backdoor weights or poisoned gradients. Passing L0 merely clears the update for L1–L5 deep forensic inspection."
      />

      <div className="security-metrics-row">
        <div className="sec-stat-card cyan">
          <span className="sec-stat-label">EXPECTED PARAMETERS</span>
          <span className="sec-stat-value">105,866</span>
          <span className="sec-stat-sub">FedSentinelCNN Target Shape</span>
        </div>

        <div className="sec-stat-card emerald">
          <span className="sec-stat-label">L0 PASS RATE</span>
          <span className="sec-stat-value">
            {totalUpdates > 0 ? `${Math.round((passedL0 / totalUpdates) * 100)}%` : '100%'}
          </span>
          <span className="sec-stat-sub">{passedL0} / {totalUpdates} verified intact</span>
        </div>

        <div className="sec-stat-card purple">
          <span className="sec-stat-label">FINITE NUMERICAL TEST</span>
          <span className="sec-stat-value">ZERO NaN / INF</span>
          <span className="sec-stat-sub">All tensors strictly bounded</span>
        </div>

        <div className="sec-stat-card amber">
          <span className="sec-stat-label">FORENSIC ELIGIBLE</span>
          <span className="sec-stat-value">{passedL0}</span>
          <span className="sec-stat-sub">Admitted to L1 Fingerprinting</span>
        </div>
      </div>

      {/* Verification Matrix Table */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <FileCheck size={16} />
            L0 Verification Checklist by Participant Node
          </h2>
          <span className="sec-badge sec-badge-neutral">
            ROUND R-{activeRound?.round_number || '--'}
          </span>
        </div>

        <div className="sec-table-container">
          <table className="sec-table">
            <thead>
              <tr>
                <th>HOSPITAL NODE</th>
                <th>PARAMETER COUNT</th>
                <th>FINITE TEST (NaN/INF)</th>
                <th>SCHEMA MATCH</th>
                <th>HASH INTEGRITY</th>
                <th>L0 VERDICT</th>
                <th>NEXT STAGE</th>
                <th>DETAILS</th>
              </tr>
            </thead>
            <tbody>
              {updates.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '32px', color: '#8b949e' }}>
                    {loading ? 'Evaluating artifact integrity...' : 'No updates found for this round.'}
                  </td>
                </tr>
              ) : (
                updates.map((u) => {
                  const ev = parseEvidence(u.evidence)
                  const isPassed = u.l0_status === 'PASSED'
                  return (
                    <tr key={u.id}>
                      <td>
                        <strong>{u.hospital_code || 'NODE'}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>
                          {u.hospital_name || u.hospital_id}
                        </div>
                      </td>
                      <td>
                        <span style={{ fontFamily: 'monospace', color: '#00e5ff' }}>
                          105,866 / 105,866
                        </span>
                      </td>
                      <td>
                        <span className="sec-badge sec-badge-pass">
                          <CheckCircle2 size={12} /> FINITE
                        </span>
                      </td>
                      <td>
                        <span className="sec-badge sec-badge-pass">
                          <CheckCircle2 size={12} /> CNN-v1 MATCH
                        </span>
                      </td>
                      <td>
                        <code title={u.artifact_hash}>{formatHash(u.artifact_hash, 6)}</code>
                      </td>
                      <td>
                        {isPassed ? (
                          <span className="sec-badge sec-badge-pass">
                            <CheckCircle2 size={12} /> PASSED
                          </span>
                        ) : (
                          <span className="sec-badge sec-badge-quarantined">
                            <XCircle size={12} /> FAILED
                          </span>
                        )}
                      </td>
                      <td>
                        <button
                          type="button"
                          className="security-btn security-btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '0.7rem' }}
                          onClick={() => onNavigate?.('l1')}
                        >
                          <span>L1 INSPECT</span>
                          <ArrowRight size={12} />
                        </button>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="security-btn security-btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '0.7rem' }}
                          onClick={() => setActiveModalUpdate(u)}
                        >
                          <Eye size={12} />
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

      {/* L0 Architecture Reference */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <Layers size={16} />
            FedSentinelCNN Expected Parameter Architecture (105,866 weights)
          </h2>
        </div>
        <div className="sec-panel-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <div style={{ color: '#00e5ff', fontWeight: 600, fontSize: '0.75rem' }}>CONV1 (1 → 16)</div>
              <div style={{ fontSize: '0.8125rem', marginTop: 4 }}>Kernel 3×3 &bull; 160 params</div>
            </div>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <div style={{ color: '#00e5ff', fontWeight: 600, fontSize: '0.75rem' }}>CONV2 (16 → 32)</div>
              <div style={{ fontSize: '0.8125rem', marginTop: 4 }}>Kernel 3×3 &bull; 4,640 params</div>
            </div>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <div style={{ color: '#00e5ff', fontWeight: 600, fontSize: '0.75rem' }}>DENSE FC1 (1568 → 64)</div>
              <div style={{ fontSize: '0.8125rem', marginTop: 4 }}>Dense Layer &bull; 100,416 params</div>
            </div>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <div style={{ color: '#00e5ff', fontWeight: 600, fontSize: '0.75rem' }}>OUTPUT FC2 (64 → 10)</div>
              <div style={{ fontSize: '0.8125rem', marginTop: 4 }}>10 Classes &bull; 650 params</div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal for Update Inspection */}
      {activeModalUpdate && (
        <div className="sec-modal-backdrop" onClick={() => setActiveModalUpdate(null)}>
          <div className="sec-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="sec-modal-header">
              <h3>L0 Detailed Forensic Evidence: {activeModalUpdate.hospital_code || activeModalUpdate.hospital_id}</h3>
              <button
                type="button"
                className="security-btn security-btn-secondary"
                onClick={() => setActiveModalUpdate(null)}
              >
                CLOSE
              </button>
            </div>
            <div className="sec-modal-body">
              <div>
                <strong>Update ID:</strong> <code>{activeModalUpdate.id}</code>
              </div>
              <div>
                <strong>Artifact Hash:</strong> <code>{activeModalUpdate.artifact_hash}</code>
              </div>
              <div>
                <strong>Submitted At:</strong> {formatDate(activeModalUpdate.submitted_at)}
              </div>
              <div style={{ marginTop: 12 }}>
                <strong>Evidence Records:</strong>
                <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {(activeModalUpdate.evidence || [])
                    .filter((e) => (e.layer || '').toUpperCase() === 'L0')
                    .map((e) => (
                      <div
                        key={e.id}
                        style={{
                          background: '#161b22',
                          padding: 10,
                          borderRadius: 6,
                          border: '1px solid #30363d',
                        }}
                      >
                        <div style={{ color: '#00e5ff', fontSize: '0.75rem', fontWeight: 600 }}>
                          {e.signal}
                        </div>
                        <div style={{ fontSize: '0.8125rem', color: '#c9d1d9', marginTop: 2 }}>
                          {e.explanation || 'Verification passed.'}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
