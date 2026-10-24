import React, { useState, useEffect, useMemo } from 'react'
import {
  Shield,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ChevronRight,
  ExternalLink,
  Layers,
  Database,
  Activity,
  Cpu,
} from 'lucide-react'

const rawApi = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://127.0.0.1:8000'
export const API = rawApi.replace(/\/+$/, '')
export const FEDERATION_ID = (import.meta.env && import.meta.env.VITE_FEDERATION_ID) || '413ef0b3-a947-4a02-a652-d963ef14b8da'

export async function apiFetch(path, token, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  })

  if (!response.ok) {
    let detail = `Request failed: ${response.status} ${response.statusText}`
    try {
      const data = await response.json()
      if (data?.detail) {
        detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      }
    } catch {
      // Non-JSON response
    }
    const err = new Error(detail)
    err.status = response.status
    throw err
  }

  if (response.status === 204) return null
  return response.json()
}

export function parseEvidence(evidenceList = []) {
  const result = {
    l0: { artifact_validation: false, forensic_eligibility: null },
    l1: { privacy_safe_fingerprint: null },
    l2: { anomaly_score: 0, z_score: 0, peer_similarity: 0, outlier: 0 },
    l3: { influence_score: 0, validation_delta: 0, harmful_influence: 0 },
    l4: { accuracy_delta: 0, loss_delta: 0, harmful_counterfactual: 0 },
    l5: { attribution_score: 0, hypothesis: 'UNKNOWN', confidence: 0, supporting_evidence: [] },
    trust: { risk_score: 0, confidence: 0, decision: 'UNKNOWN', reason: '' },
  }

  if (!Array.isArray(evidenceList)) return result

  for (const item of evidenceList) {
    const layer = (item.layer || '').toUpperCase()
    const sig = item.signal || ''
    const score = item.score != null ? Number(item.score) : null
    const exp = item.explanation || ''

    if (layer === 'L0') {
      if (sig === 'artifact_validation') result.l0.artifact_validation = true
      if (sig === 'forensic_eligibility') result.l0.forensic_eligibility = score
    } else if (layer === 'L1') {
      if (sig === 'privacy_safe_fingerprint') result.l1.privacy_safe_fingerprint = exp
    } else if (layer === 'L2') {
      if (sig === 'anomaly_score') result.l2.anomaly_score = score ?? 0
      if (sig === 'z_score') result.l2.z_score = score ?? 0
      if (sig === 'peer_similarity') result.l2.peer_similarity = score ?? 0
      if (sig === 'outlier') result.l2.outlier = score ?? 0
    } else if (layer === 'L3') {
      if (sig === 'influence_score') result.l3.influence_score = score ?? 0
      if (sig === 'validation_delta') result.l3.validation_delta = score ?? 0
      if (sig === 'harmful_influence') result.l3.harmful_influence = score ?? 0
    } else if (layer === 'L4') {
      if (sig === 'accuracy_delta') result.l4.accuracy_delta = score ?? 0
      if (sig === 'loss_delta') result.l4.loss_delta = score ?? 0
      if (sig === 'harmful_counterfactual') result.l4.harmful_counterfactual = score ?? 0
    } else if (layer === 'L5') {
      if (sig === 'attribution_score') result.l5.attribution_score = score ?? 0
      if (sig === 'confidence') result.l5.confidence = score ?? 0
      if (sig === 'hypothesis') {
        const match = exp.match(/L5 hypothesis:\s*([A-Za-z0-9_]+)/i)
        result.l5.hypothesis = match ? match[1] : exp || 'ANOMALOUS_UPDATE'
      }
      if (sig === 'supporting_evidence') {
        result.l5.supporting_evidence.push(exp)
      }
    } else if (layer === 'TRUST') {
      if (sig === 'risk_score') result.trust.risk_score = score ?? 0
      if (sig === 'confidence') result.trust.confidence = score ?? 0
      if (sig === 'decision') {
        const match = exp.match(/Trust decision:\s*([A-Za-z0-9_]+)/i)
        result.trust.decision = match ? match[1] : exp || 'MONITOR'
      }
      if (sig === 'reason') result.trust.reason = exp
    }
  }

  return result
}

export function formatHash(hash, len = 8) {
  if (!hash) return '--'
  if (hash.length <= len * 2) return hash
  return `${hash.slice(0, len)}...${hash.slice(-len)}`
}

export function formatNumber(num, decimals = 2) {
  if (num == null || isNaN(num)) return '--'
  return Number(num).toFixed(decimals)
}

export function formatPercent(num) {
  if (num == null || isNaN(num)) return '--'
  return `${(Number(num) * 100).toFixed(1)}%`
}

export function formatDate(dateStr) {
  if (!dateStr) return '--'
  try {
    const d = new Date(dateStr)
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch {
    return dateStr
  }
}

/**
 * Standard Header for Security Sub-Pages with Round Selector
 */
export function SecurityPageHeader({
  title,
  subtitle,
  badgeText = 'SECURITY CONTROL PLANE',
  rounds = [],
  selectedRoundId,
  onSelectRound,
  onRefresh,
  loading = false,
  extraControls = null,
}) {
  return (
    <header className="page-header security-subpage-header">
      <div className="security-subpage-title-group">
        <div className="panel-kicker">{badgeText}</div>
        <h1>{title}</h1>
        {subtitle && <p className="security-subpage-desc">{subtitle}</p>}
      </div>

      <div className="security-header-actions">
        {rounds && rounds.length > 0 && (
          <div className="security-round-select-wrapper">
            <label className="security-select-label">ACTIVE TELEMETRY ROUND</label>
            <select
              className="security-round-select"
              value={selectedRoundId || ''}
              onChange={(e) => onSelectRound?.(e.target.value)}
            >
              {rounds.map((r) => (
                <option key={r.id} value={r.id}>
                  R-{r.round_number} &bull; {r.status} &bull;{' '}
                  {r.configuration?.execution_mode || 'SIMULATION'} ({r.participating_clients || 0}{' '}
                  nodes)
                </option>
              ))}
            </select>
          </div>
        )}

        {extraControls}

        {onRefresh && (
          <button
            type="button"
            className="security-btn security-btn-secondary"
            onClick={onRefresh}
            disabled={loading}
            title="Refresh telemetry"
          >
            <RotateCcw size={14} className={loading ? 'spin-icon' : ''} />
            <span>{loading ? 'SYNCING...' : 'SYNC'}</span>
          </button>
        )}
      </div>
    </header>
  )
}

/**
 * Core Philosophy Security Banner
 */
export function SecurityPhilosophyBanner({ principle, context }) {
  return (
    <div className="security-philosophy-banner">
      <div className="philosophy-icon">
        <Shield size={20} />
      </div>
      <div className="philosophy-content">
        <span className="philosophy-title">CORE SECURITY PRINCIPLE: {principle}</span>
        <span className="philosophy-desc">{context}</span>
      </div>
    </div>
  )
}
