import React, { useState } from 'react'
import { SlidersHorizontal, ShieldAlert, CheckCircle2, XCircle, AlertTriangle, RefreshCw, FileText } from 'lucide-react'

const rawApi = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://127.0.0.1:8000'
const API = rawApi.replace(/\/+$/, '')

export default function HumanOverridesPage({ data, token, onDataRefresh }) {
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [overrideDecision, setOverrideDecision] = useState('')
  const [justification, setJustification] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')

  const incidents = Array.isArray(data?.incidents) ? data.incidents : []
  const hospitals = Array.isArray(data?.hospitals) ? data.hospitals : []

  const openIncidents = incidents.filter(i => i.status === 'OPEN' || i.status === 'REVIEW')

  async function submitOverride() {
    if (!selectedIncident || !overrideDecision || !justification.trim()) {
      alert('Decision and justification are mandatory.')
      return
    }
    setBusy(true)
    setMessage('')
    try {
      const resp = await fetch(`${API}/api/v1/incidents/${selectedIncident.id}/override`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action: overrideDecision,
          notes: justification.trim()
        })
      })
      if (!resp.ok) {
        // Fallback to update incident status if override endpoint is different
        const patchResp = await fetch(`${API}/api/v1/incidents/${selectedIncident.id}`, {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            status: overrideDecision === 'ACCEPT' ? 'RESOLVED' : 'DISMISSED',
            resolution_notes: justification.trim()
          })
        })
        if (!patchResp.ok) {
          throw new Error('Failed to record manual override')
        }
      }
      setMessage(`Manual security override successfully committed for incident ${selectedIncident.id}.`)
      setSelectedIncident(null)
      setOverrideDecision('')
      setJustification('')
      onDataRefresh?.()
    } catch (err) {
      alert(`Override error: ${err.message}`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page-container" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <div style={{ color: '#00e5ff', fontSize: 11, fontWeight: 700, letterSpacing: '0.1em' }}>
            SECURITY DECISION / HUMAN-IN-THE-LOOP
          </div>
          <h1 style={{ fontSize: 26, margin: '4px 0', color: '#fff', display: 'flex', alignItems: 'center', gap: 10 }}>
            <SlidersHorizontal size={26} color="#00e5ff" />
            Human Overrides & Quarantine Adjudication
          </h1>
          <p style={{ color: '#94a3b8', fontSize: 13, margin: 0 }}>
            Adjudicate automated L0–L5 defense decisions, review adversarial anomaly scores, and commit authoritative overrides.
          </p>
        </div>

        <button
          onClick={onDataRefresh}
          className="hp-button"
          style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', padding: '8px 14px', borderRadius: 6, cursor: 'pointer' }}
        >
          <RefreshCw size={14} />
          Refresh Incidents
        </button>
      </div>

      {message && (
        <div style={{ padding: '12px 16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', color: '#10b981', borderRadius: 6, marginBottom: 16, fontSize: 13 }}>
          {message}
        </div>
      )}

      {/* Incidents List */}
      <div style={{ display: 'grid', gridTemplateColumns: openIncidents.length ? '1fr 1fr' : '1fr', gap: 16 }}>
        <div>
          <h3 style={{ fontSize: 14, color: '#f8fafc', marginBottom: 12 }}>
            Active Security Flags Requiring Human Review ({openIncidents.length})
          </h3>

          {openIncidents.length === 0 ? (
            <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, padding: 30, textAlign: 'center', color: '#64748b' }}>
              <CheckCircle2 size={32} color="#10b981" style={{ margin: '0 auto 8px' }} />
              <div style={{ color: '#cbd5e1', fontWeight: 600 }}>All Security Decisions Adjudicated</div>
              <div style={{ fontSize: 11, marginTop: 4 }}>No active quarantined updates or open incidents pending human review.</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {openIncidents.map(inc => {
                const hosp = hospitals.find(h => h.id === inc.hospital_id)
                const isSel = selectedIncident?.id === inc.id
                return (
                  <div
                    key={inc.id}
                    onClick={() => setSelectedIncident(inc)}
                    style={{
                      background: isSel ? 'rgba(56, 189, 248, 0.1)' : '#0f172a',
                      border: `1px solid ${isSel ? '#38bdf8' : '#1e293b'}`,
                      borderRadius: 6,
                      padding: 14,
                      cursor: 'pointer',
                      transition: 'all 0.15s'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 700, color: '#38bdf8' }}>{hosp?.code || 'HOSPITAL'}</span>
                      <span style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#ef4444', fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4 }}>
                        RISK {inc.risk_score ?? 'HIGH'}
                      </span>
                    </div>
                    <div style={{ color: '#f8fafc', fontSize: 12, fontWeight: 600, marginTop: 4 }}>
                      {inc.title || inc.description || 'Quarantined Update'}
                    </div>
                    <div style={{ color: '#64748b', fontSize: 10, marginTop: 4 }}>
                      Incident ID: {inc.id.slice(0, 8)} • Round: {inc.round_id ? inc.round_id.slice(0, 8) : '—'}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Adjudication Panel */}
        <div>
          <h3 style={{ fontSize: 14, color: '#f8fafc', marginBottom: 12 }}>
            Authoritative Override Console
          </h3>

          {selectedIncident ? (
            <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, padding: 18 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#f59e0b', fontSize: 12, fontWeight: 700 }}>
                <ShieldAlert size={16} />
                <span>ADJUDICATING INCIDENT {selectedIncident.id.slice(0, 8)}</span>
              </div>

              <div style={{ background: '#020617', padding: 12, borderRadius: 6, marginTop: 12, fontSize: 11 }}>
                <div><span style={{ color: '#64748b' }}>Reason:</span> <strong style={{ color: '#cbd5e1' }}>{selectedIncident.description || 'Statistical anomaly detected by L2/L3 defense.'}</strong></div>
                <div style={{ marginTop: 4 }}><span style={{ color: '#64748b' }}>Hypothesis:</span> <span style={{ color: '#38bdf8' }}>{selectedIncident.threat_hypothesis || 'TARGETED_POISONING'}</span></div>
              </div>

              <div style={{ marginTop: 16 }}>
                <label style={{ display: 'block', fontSize: 11, color: '#94a3b8', marginBottom: 6 }}>
                  SELECT HUMAN OVERRIDE ACTION *
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                  <button
                    type="button"
                    onClick={() => setOverrideDecision('ACCEPT')}
                    style={{
                      background: overrideDecision === 'ACCEPT' ? 'rgba(16, 185, 129, 0.2)' : '#1e293b',
                      border: `1px solid ${overrideDecision === 'ACCEPT' ? '#10b981' : '#334155'}`,
                      color: overrideDecision === 'ACCEPT' ? '#10b981' : '#cbd5e1',
                      padding: 10,
                      borderRadius: 6,
                      cursor: 'pointer',
                      fontWeight: 600,
                      fontSize: 11
                    }}
                  >
                    Overrule: Release Update
                  </button>
                  <button
                    type="button"
                    onClick={() => setOverrideDecision('DROP')}
                    style={{
                      background: overrideDecision === 'DROP' ? 'rgba(239, 68, 68, 0.2)' : '#1e293b',
                      border: `1px solid ${overrideDecision === 'DROP' ? '#ef4444' : '#334155'}`,
                      color: overrideDecision === 'DROP' ? '#ef4444' : '#cbd5e1',
                      padding: 10,
                      borderRadius: 6,
                      cursor: 'pointer',
                      fontWeight: 600,
                      fontSize: 11
                    }}
                  >
                    Confirm: Permanent Drop
                  </button>
                </div>
              </div>

              <label style={{ display: 'block', fontSize: 11, color: '#94a3b8', marginTop: 14 }}>
                AUDIT JUSTIFICATION NOTE *
                <textarea
                  value={justification}
                  onChange={(e) => setJustification(e.target.value)}
                  placeholder="State the scientific or clinical verification rationale for this override..."
                  required
                  style={{ width: '100%', background: '#020617', border: '1px solid #334155', color: '#fff', padding: 8, borderRadius: 4, marginTop: 4, minHeight: 70, fontSize: 12 }}
                />
              </label>

              <button
                type="button"
                onClick={submitOverride}
                disabled={busy || !overrideDecision || !justification.trim()}
                style={{
                  width: '100%',
                  marginTop: 16,
                  background: '#0284c7',
                  border: 'none',
                  color: '#fff',
                  padding: '10px 16px',
                  borderRadius: 6,
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: 12
                }}
              >
                {busy ? 'Committing Override...' : 'Commit Authoritative Override'}
              </button>
            </div>
          ) : (
            <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, padding: 30, textAlign: 'center', color: '#64748b' }}>
              Select an incident from the left to adjudicate.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
