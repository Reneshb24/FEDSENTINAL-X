import React, { useState, useEffect, useMemo } from 'react'
import {
  Radar,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  Activity,
  ArrowRight,
  TrendingUp,
  Sliders,
  CheckCircle2,
  XCircle,
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

export default function L2CorrelatePage({ data, token, onNavigate }) {
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

  const parsedUpdates = useMemo(() => {
    return updates.map((u) => ({
      ...u,
      parsed: parseEvidence(u.evidence),
    }))
  }, [updates])

  const outliers = parsedUpdates.filter((u) => u.parsed.l2.outlier === 1 || u.parsed.l2.z_score >= 3.0)
  const maxZScore = Math.max(0, ...parsedUpdates.map((u) => u.parsed.l2.z_score))
  const maxAnomalyScore = Math.max(0, ...parsedUpdates.map((u) => u.parsed.l2.anomaly_score))

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="L2 — Robust Statistical Anomaly Correlation"
        subtitle="Median-baseline robust statistics and Median Absolute Deviation (MAD) detecting multi-sigma divergence in update trajectory."
        badgeText="SECURITY LAYER 2 / CORRELATION"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadUpdates}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="ANOMALY != MALICIOUS"
        context="An outlier score measures statistical distance from the peer cohort, NOT malicious intent. High non-IID data distribution (e.g. Dirichlet \alpha=0.5) or rare patient pathology can trigger L2 statistical deviation. L2 anomaly is evidence, not a verdict."
      />

      <div className="security-metrics-row">
        <div className="sec-stat-card cyan">
          <span className="sec-stat-label">DETECTOR BASELINE</span>
          <span className="sec-stat-value">MEDIAN + MAD</span>
          <span className="sec-stat-sub">Breakdown point: 50%</span>
        </div>

        <div className="sec-stat-card amber">
          <span className="sec-stat-label">ROBUST THRESHOLD</span>
          <span className="sec-stat-value">3.0 σ</span>
          <span className="sec-stat-sub">MAD-normalized z-score cutoff</span>
        </div>

        <div className={`sec-stat-card ${outliers.length > 0 ? 'crimson' : 'emerald'}`}>
          <span className="sec-stat-label">DETECTED OUTLIERS</span>
          <span className="sec-stat-value">{outliers.length}</span>
          <span className="sec-stat-sub">
            {outliers.length > 0 ? 'Exceeds 3.0σ robust threshold' : 'Cohort within normal bounds'}
          </span>
        </div>

        <div className="sec-stat-card purple">
          <span className="sec-stat-label">PEAK ANOMALY SCORE</span>
          <span className="sec-stat-value">{formatNumber(maxAnomalyScore, 1)}</span>
          <span className="sec-stat-sub">Peak z-score: {formatNumber(maxZScore, 1)}σ</span>
        </div>
      </div>

      {/* Anomaly Distribution Chart & Table */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <Radar size={16} />
            Statistical Anomaly Matrix & Z-Score Deviation
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
                <th>ANOMALY SCORE</th>
                <th>ROBUST Z-SCORE (MAD)</th>
                <th>PEER SIMILARITY</th>
                <th>THRESHOLD (3.0σ)</th>
                <th>L2 OUTLIER STATUS</th>
                <th>NEXT LAYER</th>
              </tr>
            </thead>
            <tbody>
              {parsedUpdates.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '32px', color: '#8b949e' }}>
                    {loading ? 'Correlating statistical baselines...' : 'No updates for this round.'}
                  </td>
                </tr>
              ) : (
                parsedUpdates.map((u) => {
                  const l2 = u.parsed.l2
                  const isOutlier = l2.outlier === 1 || l2.z_score >= 3.0
                  return (
                    <tr key={u.id} className={isOutlier ? 'highlight-danger' : ''}>
                      <td>
                        <strong>{u.hospital_code || 'NODE'}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>
                          {u.hospital_name || u.hospital_id}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontFamily: 'monospace', fontWeight: 700, color: isOutlier ? '#ff3b5c' : '#f0f6fc' }}>
                            {formatNumber(l2.anomaly_score, 2)}
                          </span>
                          <div style={{ width: 60 }} className="sec-bar-meter">
                            <div
                              className={`sec-bar-meter-fill ${isOutlier ? 'crimson' : 'emerald'}`}
                              style={{ width: `${Math.min(100, l2.anomaly_score)}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td>
                        <span
                          style={{
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            color: l2.z_score >= 3.0 ? '#ff3b5c' : '#58a6ff',
                          }}
                        >
                          {formatNumber(l2.z_score, 2)} σ
                        </span>
                      </td>
                      <td>
                        <span style={{ fontFamily: 'monospace', color: '#8b949e' }}>
                          {formatNumber(l2.peer_similarity, 4)}
                        </span>
                      </td>
                      <td>
                        <span style={{ color: '#8b949e', fontSize: '0.75rem' }}>3.00 σ</span>
                      </td>
                      <td>
                        {isOutlier ? (
                          <span className="sec-badge sec-badge-quarantined">
                            <AlertTriangle size={12} /> OUTLIER DETECTED
                          </span>
                        ) : (
                          <span className="sec-badge sec-badge-pass">
                            <CheckCircle2 size={12} /> NORMAL BASELINE
                          </span>
                        )}
                      </td>
                      <td>
                        <button
                          type="button"
                          className="security-btn security-btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '0.7rem' }}
                          onClick={() => onNavigate?.('l3')}
                        >
                          <span>L3 INFLUENCE</span>
                          <ArrowRight size={12} />
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
    </div>
  )
}
