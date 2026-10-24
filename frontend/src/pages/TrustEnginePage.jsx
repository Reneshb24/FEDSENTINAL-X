import React, { useState, useEffect, useMemo } from 'react'
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ArrowRight,
  Gauge,
  Sliders,
  Scale,
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

export default function TrustEnginePage({ data, token, onNavigate }) {
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []
  const [selectedRoundId, setSelectedRoundId] = useState('')
  const [trustRecords, setTrustRecords] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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

  async function loadTrust() {
    if (!activeRound?.id || !token) return
    try {
      setLoading(true)
      setError('')
      const res = await apiFetch(`/api/v1/security/rounds/${activeRound.id}/trust`, token)
      setTrustRecords(Array.isArray(res) ? res : [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTrust()
  }, [activeRound?.id, token])

  const trustedCount = trustRecords.filter((r) => r.status === 'TRUSTED').length
  const reviewCount = trustRecords.filter((r) => r.status === 'REVIEW').length
  const suspiciousCount = trustRecords.filter((r) => r.status === 'SUSPICIOUS').length
  const quarantinedCount = trustRecords.filter((r) => r.status === 'QUARANTINED').length

  return (
    <div className="security-page">
      <SecurityPageHeader
        title="Trust Engine & Operational Risk Posture"
        subtitle="Holistic policy engine assessing participant risk posture through multi-signal evidence aggregation."
        badgeText="DECISION ENGINE / RISK != VERDICT"
        rounds={rounds}
        selectedRoundId={activeRound?.id}
        onSelectRound={setSelectedRoundId}
        onRefresh={loadTrust}
        loading={loading}
      />

      <SecurityPhilosophyBanner
        principle="RISK != VERDICT"
        context="Trust scores quantify empirical risk based on observable update metrics. A low trust score triggers operational precautions (MONITOR or REVIEW) without asserting malicious criminality. The system generates actionable recommendations, leaving final authority to audited human operators."
      />

      <div className="security-metrics-row">
        <div className="sec-stat-card emerald">
          <span className="sec-stat-label">TRUSTED NODES</span>
          <span className="sec-stat-value">{trustedCount}</span>
          <span className="sec-stat-sub">Zero anomalous signals</span>
        </div>

        <div className="sec-stat-card amber">
          <span className="sec-stat-label">REVIEW POSTURE</span>
          <span className="sec-stat-value">{reviewCount}</span>
          <span className="sec-stat-sub">1 security signal flagged</span>
        </div>

        <div className="sec-stat-card purple">
          <span className="sec-stat-label">SUSPICIOUS POSTURE</span>
          <span className="sec-stat-value">{suspiciousCount}</span>
          <span className="sec-stat-sub">2 strong security signals</span>
        </div>

        <div className="sec-stat-card crimson">
          <span className="sec-stat-label">POLICY QUARANTINED</span>
          <span className="sec-stat-value">{quarantinedCount}</span>
          <span className="sec-stat-sub">3+ signals or integrity breach</span>
        </div>
      </div>

      {/* Trust Policy Rules Deck */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <Scale size={16} />
            Deterministic Policy Rules & Signal Weighting
          </h2>
          <span className="sec-badge sec-badge-neutral">DECISION POLICIES</span>
        </div>
        <div className="sec-panel-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14 }}>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <strong style={{ color: '#ff3b5c', fontSize: '0.8125rem' }}>CRITICAL RULE 1</strong>
              <p style={{ fontSize: '0.75rem', color: '#8b949e', margin: '4px 0 0 0' }}>
                <strong>L0 Integrity Failure</strong> → Immediate Automatic <strong>QUARANTINE</strong>
              </p>
            </div>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <strong style={{ color: '#ff3b5c', fontSize: '0.8125rem' }}>CRITICAL RULE 2</strong>
              <p style={{ fontSize: '0.75rem', color: '#8b949e', margin: '4px 0 0 0' }}>
                <strong>3+ Strong Signals</strong> → Policy Escalation to <strong>QUARANTINE</strong>
              </p>
            </div>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <strong style={{ color: '#a371f7', fontSize: '0.8125rem' }}>ELEVATED RULE 3</strong>
              <p style={{ fontSize: '0.75rem', color: '#8b949e', margin: '4px 0 0 0' }}>
                <strong>2 Strong Signals</strong> → Operational Posture <strong>SUSPICIOUS</strong>
              </p>
            </div>
            <div style={{ background: '#161b22', padding: 12, borderRadius: 6, border: '1px solid #30363d' }}>
              <strong style={{ color: '#ffb020', fontSize: '0.8125rem' }}>ADVISORY RULE 4</strong>
              <p style={{ fontSize: '0.75rem', color: '#8b949e', margin: '4px 0 0 0' }}>
                <strong>1 Strong Signal</strong> → Operational Posture <strong>REVIEW</strong>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Real Trust Records Table */}
      <div className="sec-panel">
        <div className="sec-panel-header">
          <h2>
            <Gauge size={16} />
            Persisted Hospital Trust Records ({trustRecords.length})
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
                <th>TRUST SCORE</th>
                <th>RISK STATUS</th>
                <th>OPERATIONAL DECISION & JUSTIFICATION</th>
                <th>TIMESTAMP</th>
                <th>INCIDENT ACTION</th>
              </tr>
            </thead>
            <tbody>
              {trustRecords.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '32px', color: '#8b949e' }}>
                    {loading ? 'Evaluating trust scores...' : 'No trust records found for this round.'}
                  </td>
                </tr>
              ) : (
                trustRecords.map((r) => {
                  const status = (r.status || '').toUpperCase()
                  const isQuarantined = status === 'QUARANTINED'
                  const isSuspicious = status === 'SUSPICIOUS'
                  const isReview = status === 'REVIEW'

                  return (
                    <tr key={r.id} className={isQuarantined ? 'highlight-danger' : ''}>
                      <td>
                        <strong>{r.hospital_code || 'NODE'}</strong>
                        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>
                          {r.hospital_name || r.hospital_id}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontFamily: 'monospace', fontWeight: 700, color: '#f0f6fc' }}>
                            {formatNumber(r.score, 1)}
                          </span>
                          <div style={{ width: 60 }} className="sec-bar-meter">
                            <div
                              className={`sec-bar-meter-fill ${
                                isQuarantined
                                  ? 'crimson'
                                  : isSuspicious
                                    ? 'purple'
                                    : isReview
                                      ? 'amber'
                                      : 'emerald'
                              }`}
                              style={{ width: `${Math.min(100, r.score)}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td>
                        <span
                          className={`sec-badge ${
                            isQuarantined
                              ? 'sec-badge-quarantined'
                              : isSuspicious
                                ? 'sec-badge-warning'
                                : isReview
                                  ? 'sec-badge-review'
                                  : 'sec-badge-pass'
                          }`}
                        >
                          {r.status || 'TRUSTED'}
                        </span>
                      </td>
                      <td style={{ maxWidth: 350 }}>
                        <span style={{ fontSize: '0.75rem', color: '#c9d1d9' }}>
                          {r.reason || 'Nominal behavior adhering to peer convergence standards.'}
                        </span>
                      </td>
                      <td style={{ color: '#8b949e', fontSize: '0.75rem' }}>
                        {formatDate(r.created_at)}
                      </td>
                      <td>
                        <button
                          type="button"
                          className="security-btn security-btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '0.7rem' }}
                          onClick={() => onNavigate?.('incidents')}
                        >
                          <span>INCIDENTS</span>
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
