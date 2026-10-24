import React, { useState, useEffect, useMemo } from 'react'
import {
  Layers3,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  Database,
  Cpu,
  Filter,
  CheckCircle2,
  XCircle,
  FileCheck,
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

export default function SafeAggregationPage({ data, token, onNavigate }) {
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []
  const [selectedRoundId, setSelectedRoundId] = useState('')
  const [updates, setUpdates] = useState([])
  const [loading, setLoading] = useState(false)

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
      const res = await apiFetch(`/api/v1/security/rounds/${activeRound.id}/updates`, token)
      setUpdates(Array.isArray(res) ? res : [])
    } catch {
      // Ignore
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUpdates()
  }, [activeRound?.id, token])

  const accepted = updates.filter((u) => u.detection_status === 'ACCEPTED')
  const quarantined = updates.filter((u) => u.detection_status === 'QUARANTINED')

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="Safe Aggregation & Exclusion Gate"
        subtitle="Mathematical aggregation pipeline strictly isolating quarantined updates prior to global parameter averaging."
        badgeText="AGGREGATION SECURITY / ZERO POISONING LEAK"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadUpdates}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="VERIFIED AGGREGATION ISOLATION"
        context="Quarantined updates are mathematically severed from the FedAvg tensor summation: \theta_{t+1} = \sum_{k \in \mathcal{A}_t} \frac{n_k}{N_t} \theta_t^k. Poisoned weights or backdoor vectors never cross into the aggregate global model artifact."
      />

      <div className="security-metrics-row">
        <div className="sec-stat-card cyan">
          <span className="sec-stat-label">TOTAL PARTICIPATING</span>
          <span className="sec-stat-value">{updates.length}</span>
          <span className="sec-stat-sub">Ingress updates in R-{activeRound?.round_number || '--'}</span>
        </div>

        <div className="sec-stat-card emerald">
          <span className="sec-stat-label">ACCEPTED INTO AGGREGATE</span>
          <span className="sec-stat-value">{accepted.length}</span>
          <span className="sec-stat-sub">Weights integrated into global state</span>
        </div>

        <div className="sec-stat-card crimson">
          <span className="sec-stat-label">EXCLUDED VIA QUARANTINE</span>
          <span className="sec-stat-value">{quarantined.length}</span>
          <span className="sec-stat-sub">Strictly blocked from model parameters</span>
        </div>

        <div className="sec-stat-card purple">
          <span className="sec-stat-label">AGGREGATION METHOD</span>
          <span className="sec-stat-value">FEDAVG + SHIELD</span>
          <span className="sec-stat-sub">Multi-layer pre-filtered</span>
        </div>
      </div>

      {/* Aggregation Pipeline Flow Visualizer */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <Layers3 size={16} />
            Aggregation Gate Flowchart
          </h2>
          <span className="sec-badge sec-badge-info">FEDERATED TENSOR PIPELINE</span>
        </div>
        <div className="sec-panel-body">
          <div className="ingress-pipeline-flow">
            <div className="ingress-stage active">
              <Database size={20} color="#00e5ff" />
              <strong>{updates.length} Ingress Updates</strong>
              <small style={{ color: '#8b949e' }}>Raw Participant Weights</small>
            </div>
            <ArrowRight className="ingress-stage-arrow" size={18} />
            <div className="ingress-stage active" style={{ borderColor: '#ffb020' }}>
              <Filter size={20} color="#ffb020" />
              <strong>L0-L5 Security Gate</strong>
              <small style={{ color: '#ffb020' }}>Evidence & Policy</small>
            </div>
            <ArrowRight className="ingress-stage-arrow" size={18} />
            <div className="ingress-stage" style={{ borderColor: '#ff3b5c', background: 'rgba(255, 59, 92, 0.05)' }}>
              <XCircle size={20} color="#ff3b5c" />
              <strong>{quarantined.length} Quarantined</strong>
              <small style={{ color: '#ff3b5c' }}>EXCLUDED FROM AGGREGATE</small>
            </div>
            <ArrowRight className="ingress-stage-arrow" size={18} />
            <div className="ingress-stage active" style={{ borderColor: '#00e676' }}>
              <CheckCircle2 size={20} color="#00e676" />
              <strong>{accepted.length} Accepted</strong>
              <small style={{ color: '#00e676' }}>Passed All Checks</small>
            </div>
            <ArrowRight className="ingress-stage-arrow" size={18} />
            <div className="ingress-stage active" style={{ borderColor: '#a371f7' }}>
              <Cpu size={20} color="#a371f7" />
              <strong>Global Model Version</strong>
              <small style={{ color: '#a371f7' }}>Clean Aggregate Committed</small>
            </div>
          </div>
        </div>
      </div>

      {/* Cohort Tables */}
      <div className="sec-grid-2col">
        {/* Accepted Cohort */}
        <div className="sec-panel">
          <div className="sec-panel-header">
            <h2>
              <CheckCircle2 size={16} color="#00e676" />
              Integrated Accepted Updates ({accepted.length})
            </h2>
            <span className="sec-badge sec-badge-accepted">WEIGHT CONTRIBUTION ACTIVE</span>
          </div>
          <div className="sec-table-container">
            <table className="sec-table">
              <thead>
                <tr>
                  <th>NODE</th>
                  <th>HASH</th>
                  <th>SAMPLE WEIGHT</th>
                  <th>STATUS</th>
                </tr>
              </thead>
              <tbody>
                {accepted.length === 0 ? (
                  <tr>
                    <td colSpan="4" style={{ textAlign: 'center', padding: 20, color: '#8b949e' }}>
                      No accepted updates in this round.
                    </td>
                  </tr>
                ) : (
                  accepted.map((u) => (
                    <tr key={u.id}>
                      <td>
                        <strong>{u.hospital_code || 'NODE'}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>{u.hospital_name}</div>
                      </td>
                      <td>
                        <code>{formatHash(u.artifact_hash, 6)}</code>
                      </td>
                      <td>
                        <span style={{ fontFamily: 'monospace' }}>
                          {(100 / Math.max(1, accepted.length)).toFixed(1)}%
                        </span>
                      </td>
                      <td>
                        <span className="sec-badge sec-badge-pass">AGGREGATED</span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quarantined Exclusions */}
        <div className="sec-panel">
          <div className="sec-panel-header">
            <h2>
              <XCircle size={16} color="#ff3b5c" />
              Excluded Quarantined Updates ({quarantined.length})
            </h2>
            <span className="sec-badge sec-badge-quarantined">BLOCKED FROM GLOBAL WEIGHTS</span>
          </div>
          <div className="sec-table-container">
            <table className="sec-table">
              <thead>
                <tr>
                  <th>NODE</th>
                  <th>HASH</th>
                  <th>REASON</th>
                  <th>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {quarantined.length === 0 ? (
                  <tr>
                    <td colSpan="4" style={{ textAlign: 'center', padding: 20, color: '#8b949e' }}>
                      Zero quarantined updates in this round.
                    </td>
                  </tr>
                ) : (
                  quarantined.map((u) => (
                    <tr key={u.id} className="highlight-danger">
                      <td>
                        <strong>{u.hospital_code || 'NODE'}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>{u.hospital_name}</div>
                      </td>
                      <td>
                        <code>{formatHash(u.artifact_hash, 6)}</code>
                      </td>
                      <td>
                        <span style={{ color: '#ffb020', fontSize: '0.75rem' }}>
                          L2 Anomaly Divergence
                        </span>
                      </td>
                      <td>
                        <span className="sec-badge sec-badge-quarantined">SEVERED</span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
