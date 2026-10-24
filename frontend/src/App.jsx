import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  Archive,
  BarChart3,
  Building2,
  Database,
  FileClock,
  FileText,
  Gauge,
  GitBranch,
  Globe2,
  History,
  Hospital,
  Layers3,
  Network,
  Radar,
  RefreshCw,
  Search,
  SearchX,
  Settings,
  Shield,
  ShieldAlert,
  ShieldCheck,
  SlidersHorizontal,
  Terminal,
  Upload,
  Users,
  Workflow,
  X,
} from 'lucide-react'
import './App.css'
import HospitalPortal from './HospitalPortal'
import UpdateIntakePage from './pages/UpdateIntakePage'
import L0VerifyPage from './pages/L0VerifyPage'
import L1InspectPage from './pages/L1InspectPage'
import L2CorrelatePage from './pages/L2CorrelatePage'
import QuarantinePage from './pages/QuarantinePage'
import L3InfluencePage from './pages/L3InfluencePage'
import L4SimulatePage from './pages/L4SimulatePage'
import L5AttributePage from './pages/L5AttributePage'
import TrustEnginePage from './pages/TrustEnginePage'
import IncidentsPage from './pages/IncidentsPage'
import SafeAggregationPage from './pages/SafeAggregationPage'
import GlobalModelPage from './pages/GlobalModelPage'
import AuditTrailPage from './pages/AuditTrailPage'
import RoundReplayPage from './pages/RoundReplayPage'
import ReportsPage from './pages/ReportsPage'

const rawApi = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://127.0.0.1:8000'
const API = rawApi.replace(/\/+$/, '')
const FEDERATION_ID = (import.meta.env && import.meta.env.VITE_FEDERATION_ID) || '413ef0b3-a947-4a02-a652-d963ef14b8da'

const navGroups = [
  {
    label: 'COMMAND',
    items: [{ id: 'command', label: 'Command Center', icon: 'command' }],
  },
  {
    label: 'FEDERATION',
    items: [
      { id: 'overview', label: 'Overview', icon: 'overview' },
      { id: 'hospitals', label: 'Hospitals', icon: 'hospitals' },
      { id: 'synthetic', label: 'Synthetic Data', icon: 'synthetic' },
    ],
  },
  {
    label: 'SECURITY',
    items: [
      { id: 'round-config', label: 'Round Configuration', icon: 'rounds' },
      { id: 'live-round', label: 'Live Round', icon: 'live' },
      { id: 'intake', label: 'Update Intake', icon: 'intake' },
    ],
  },
  {
    label: 'ANALYSIS',
    items: [
      { id: 'l0', label: 'L0 Verify', icon: 'verify' },
      { id: 'l1', label: 'L1 Inspect', icon: 'inspect' },
      { id: 'l2', label: 'L2 Correlate', icon: 'correlate' },
      { id: 'quarantine', label: 'Quarantine', icon: 'quarantine' },
      { id: 'l3', label: 'L3 Influence', icon: 'influence' },
      { id: 'l4', label: 'L4 Simulate', icon: 'simulate' },
      { id: 'l5', label: 'L5 Attribute', icon: 'attribute' },
    ],
  },
  {
    label: 'DECISION',
    items: [
      { id: 'trust', label: 'Trust Engine', icon: 'trust' },
      { id: 'incidents', label: 'Incidents', icon: 'incidents' },
    ],
  },
  {
    label: 'MODEL',
    items: [
      { id: 'aggregation', label: 'Safe Aggregation', icon: 'aggregation' },
      { id: 'model', label: 'Global Model', icon: 'model' },
    ],
  },
  {
    label: 'FORENSICS',
    items: [
      { id: 'audit', label: 'Audit Trail', icon: 'audit' },
      { id: 'replay', label: 'Round Replay', icon: 'replay' },
      { id: 'reports', label: 'Reports', icon: 'reports' },
    ],
  },
]

async function apiFetch(path, token, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers || {}),
      ...(token
        ? { Authorization: `Bearer ${token}` }
        : {}),
    },
  })

  if (response.status === 401) {
    localStorage.removeItem('fedsentinel_token')
    throw new Error('SESSION_EXPIRED')
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        `Request failed with status ${response.status}`,
    )
  }

  return data
}

function goTo(path) {
  window.history.pushState({}, '', path)
  window.dispatchEvent(new PopStateEvent('popstate'))
}

function Login({ onLogin, portal = 'admin' }) {
  const isHospital = portal === 'hospital'

  const [authMode, setAuthMode] = useState('login') // 'login' | 'signup' (only used in hospital portal)
  const [email, setEmail] = useState(
    isHospital ? 'admin@h21.local' : 'admin@fedsentinel.local',
  )
  const [password, setPassword] = useState(
    isHospital ? 'Hospital123!' : 'Admin123!',
  )
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [loading, setLoading] = useState(false)

  // Registration Form State (Hospital Enclave Onboarding)
  const [regForm, setRegForm] = useState({
    code: '',
    name: '',
    contact_email: '',
    location: '',
    admin_email: '',
    admin_password: '',
  })

  function fillDemo(e, p) {
    setEmail(e)
    setPassword(p)
    setError('')
  }

  async function submitLogin(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setSuccessMsg('')

    try {
      const response = await fetch(`${API}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed. Please verify credentials.')
      }

      const role = String(
        data.user?.role ||
        data.user?.user_role ||
        '',
      ).toUpperCase()

      const adminRoles = ['SUPER_ADMIN', 'ADMIN']
      const hospitalRoles = [
        'HOSPITAL_ADMIN',
        'HOSPITAL_OPERATOR',
      ]

      const allowed =
        isHospital
          ? hospitalRoles.includes(role)
          : adminRoles.includes(role)

      if (!allowed) {
        throw new Error(
          isHospital
            ? 'This account is not authorized for the Hospital Portal.'
            : 'This account is not authorized for the Administrator Control Plane.',
        )
      }

      localStorage.setItem('fedsentinel_token', data.access_token)
      localStorage.setItem('fedsentinel_portal', portal)
      localStorage.setItem('fedsentinel_role', role)

      if (data.user?.hospital_id) {
        localStorage.setItem(
          'fedsentinel_hospital_id',
          data.user.hospital_id,
        )
      }

      onLogin(data.access_token)
      goTo(isHospital ? '/hospital' : '/admin')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function submitSignup(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setSuccessMsg('')

    if (!regForm.code.trim() || !regForm.name.trim() || !regForm.admin_email.trim() || !regForm.admin_password) {
      setError('Please fill in all required hospital registration fields.')
      setLoading(false)
      return
    }

    try {
      const regResp = await fetch(`${API}/api/v1/hospitals/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: regForm.code.trim().toUpperCase(),
          name: regForm.name.trim(),
          contact_email: regForm.contact_email.trim() || regForm.admin_email.trim(),
          location: regForm.location.trim() || 'Clinical Enclave',
          admin_email: regForm.admin_email.trim().toLowerCase(),
          admin_password: regForm.admin_password,
          auto_enroll: true,
        }),
      })

      const regData = await regResp.json()
      if (!regResp.ok) {
        throw new Error(regData.detail || 'Hospital registration failed.')
      }

      setSuccessMsg('Hospital registered & cohort enrolled! Signing in...')

      // Automatically authenticate with new credentials
      const authResp = await fetch(`${API}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: regForm.admin_email.trim().toLowerCase(),
          password: regForm.admin_password,
        }),
      })

      const authData = await authResp.json()
      if (!authResp.ok) {
        throw new Error('Hospital registered successfully! Please sign in with your new credentials.')
      }

      localStorage.setItem('fedsentinel_token', authData.access_token)
      localStorage.setItem('fedsentinel_portal', 'hospital')
      localStorage.setItem('fedsentinel_role', 'HOSPITAL_ADMIN')
      if (authData.user?.hospital_id) {
        localStorage.setItem('fedsentinel_hospital_id', authData.user.hospital_id)
      }

      setTimeout(() => {
        onLogin(authData.access_token)
        goTo('/hospital')
      }, 500)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className={`login-screen ${isHospital ? 'hospital-login-screen' : 'admin-login-screen'}`}>
      <div className="login-grid" />

      <section className="login-card">
        <div className="brand-lockup">
          <div className="brand-mark">
            <span />
            <span />
            <span />
          </div>

          <div>
            <strong>FED SENTINEL</strong>
            <small>{isHospital ? 'HOSPITAL ENCLAVE PORTAL' : 'SECURITY CONTROL PLANE'}</small>
          </div>
        </div>

        {/* Tab switcher: ONLY visible on Hospital Portal for Login vs Register */}
        {isHospital && (
          <div style={{ display: 'flex', gap: 8, marginTop: 18, borderBottom: '1px solid var(--line)', paddingBottom: 12 }}>
            <button
              type="button"
              className={authMode === 'login' ? 'primary-button' : 'ghost-button'}
              style={{ flex: 1, height: 36, margin: 0, justifyContent: 'center' }}
              onClick={() => { setAuthMode('login'); setError(''); setSuccessMsg(''); }}
            >
              HOSPITAL SIGN IN
            </button>
            <button
              type="button"
              className={authMode === 'signup' ? 'primary-button' : 'ghost-button'}
              style={{ flex: 1, height: 36, margin: 0, justifyContent: 'center' }}
              onClick={() => { setAuthMode('signup'); setError(''); setSuccessMsg(''); }}
            >
              REGISTER HOSPITAL
            </button>
          </div>
        )}

        {/* Headline & Description */}
        <div className="login-copy" style={{ padding: '20px 0 16px' }}>
          <div className="eyebrow">
            {isHospital
              ? (authMode === 'signup' ? 'ENCLAVE REGISTRATION' : 'INSTITUTIONAL ACCESS')
              : 'AUTHORIZED ACCESS'}
          </div>

          <h1 style={{ fontSize: isHospital && authMode === 'signup' ? 24 : 34 }}>
            {!isHospital ? (
              <>Federated AI.<br /><em>Defended.</em></>
            ) : authMode === 'signup' ? (
              <>Register Clinical<br /><em>Enclave Node.</em></>
            ) : (
              <>Hospital Clinical<br /><em>Enclave Portal.</em></>
            )}
          </h1>

          <p style={{ fontSize: 12 }}>
            {!isHospital
              ? 'Security telemetry, privacy-safe update verification and model defense.'
              : authMode === 'signup'
                ? 'Join the federated learning cohort. Raw patient data never departs your institution.'
                : 'Manage local EHR/imaging datasets, run in situ PyTorch training, and submit verified model updates.'}
          </p>
        </div>

        {/* Form Body */}
        {(!isHospital || authMode === 'login') ? (
          <form onSubmit={submitLogin}>
            {/* Quick Demo Fill Chips */}
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 6 }}>
              <span style={{ fontSize: 9, color: 'var(--muted)', letterSpacing: '0.08em', alignSelf: 'center' }}>QUICK FILL:</span>
              {isHospital ? (
                <>
                  <button
                    type="button"
                    className="hp-small-button"
                    style={{ fontSize: 9, padding: '2px 8px' }}
                    onClick={() => fillDemo('admin@h21.local', 'Hospital123!')}
                  >
                    H21 Demo
                  </button>
                  <button
                    type="button"
                    className="hp-small-button"
                    style={{ fontSize: 9, padding: '2px 8px' }}
                    onClick={() => fillDemo('admin@demohospital.local', 'Hospital123!')}
                  >
                    H01 General
                  </button>
                  <button
                    type="button"
                    className="hp-small-button"
                    style={{ fontSize: 9, padding: '2px 8px' }}
                    onClick={() => fillDemo('admin@apollo.local', 'Hospital123!')}
                  >
                    H30 Apollo
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  className="hp-small-button"
                  style={{ fontSize: 9, padding: '2px 8px' }}
                  onClick={() => fillDemo('admin@fedsentinel.local', 'Admin123!')}
                >
                  Super Admin
                </button>
              )}
            </div>

            <label>
              {isHospital ? 'HOSPITAL ADMIN ACCOUNT' : 'ADMINISTRATOR EMAIL'}
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                type="email"
                autoComplete="username"
                required
              />
            </label>

            <label>
              ACCESS KEY
              <input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                type="password"
                autoComplete="current-password"
                placeholder="Enter access key"
                required
              />
            </label>

            {error && <div className="form-error">{error}</div>}
            {successMsg && <div style={{ padding: 8, background: 'rgba(0, 230, 118, 0.1)', border: '1px solid #00e676', color: '#00e676', fontSize: 11 }}>{successMsg}</div>}

            <button className="primary-button" disabled={loading}>
              {loading
                ? 'AUTHENTICATING...'
                : isHospital
                  ? 'ENTER HOSPITAL PORTAL'
                  : 'ENTER CONTROL PLANE'}
              <span>&rarr;</span>
            </button>

            {/* In Hospital mode, offer a direct text link to switch to signup */}
            {isHospital && (
              <div style={{ textAlign: 'center', fontSize: 11, color: 'var(--muted)', marginTop: 8 }}>
                Don't have an enclave account?{' '}
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#00e5ff', textDecoration: 'underline', cursor: 'pointer', padding: 0, font: 'inherit' }}
                  onClick={() => { setAuthMode('signup'); setError(''); }}
                >
                  Register new hospital &rarr;
                </button>
              </div>
            )}
          </form>
        ) : (
          <form onSubmit={submitSignup}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 10 }}>
              <label>
                CODE
                <input
                  value={regForm.code}
                  onChange={(e) => setRegForm({ ...regForm, code: e.target.value })}
                  placeholder="e.g. H40"
                  pattern="[A-Za-z0-9_-]+"
                  required
                />
              </label>
              <label>
                HOSPITAL NAME
                <input
                  value={regForm.name}
                  onChange={(e) => setRegForm({ ...regForm, name: e.target.value })}
                  placeholder="e.g. Metro Medical Center"
                  required
                />
              </label>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <label>
                CONTACT EMAIL
                <input
                  value={regForm.contact_email}
                  onChange={(e) => setRegForm({ ...regForm, contact_email: e.target.value })}
                  placeholder="contact@hospital.org"
                  type="email"
                />
              </label>
              <label>
                LOCATION
                <input
                  value={regForm.location}
                  onChange={(e) => setRegForm({ ...regForm, location: e.target.value })}
                  placeholder="City, Country"
                />
              </label>
            </div>

            <label>
              HOSPITAL ADMIN ACCOUNT
              <input
                value={regForm.admin_email}
                onChange={(e) => setRegForm({ ...regForm, admin_email: e.target.value })}
                placeholder="admin@hospital.org"
                type="email"
                required
              />
            </label>

            <label>
              PASSWORD (MIN 8 CHARS)
              <input
                value={regForm.admin_password}
                onChange={(e) => setRegForm({ ...regForm, admin_password: e.target.value })}
                type="password"
                placeholder="Secure access password"
                minLength={8}
                required
              />
            </label>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 10, color: 'var(--green)', padding: '6px 0' }}>
              <i className="status-dot" style={{ background: '#00e676' }} />
              <span>Instant Federation Enclave Provisioning (Active Dataset Included)</span>
            </div>

            {error && <div className="form-error">{error}</div>}
            {successMsg && <div style={{ padding: 8, background: 'rgba(0, 230, 118, 0.1)', border: '1px solid #00e676', color: '#00e676', fontSize: 11 }}>{successMsg}</div>}

            <button className="primary-button" disabled={loading} style={{ background: '#00e5ff' }}>
              {loading ? 'ONBOARDING ENCLAVE...' : 'REGISTER & ENTER PORTAL'}
              <span>&rarr;</span>
            </button>

            <div style={{ textAlign: 'center', fontSize: 11, color: 'var(--muted)', marginTop: 8 }}>
              Already registered?{' '}
              <button
                type="button"
                style={{ background: 'none', border: 'none', color: '#00e5ff', textDecoration: 'underline', cursor: 'pointer', padding: 0, font: 'inherit' }}
                onClick={() => { setAuthMode('login'); setError(''); }}
              >
                Sign in to existing account &rarr;
              </button>
            </div>
          </form>
        )}

        {/* Portal Switcher Link directly below */}
        <div className="login-directory" style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--line)', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 11, color: 'var(--muted)' }}>
            {isHospital
              ? 'FedSentinel platform administrator or security analyst?'
              : 'Are you a participating healthcare facility or research clinic?'}
          </span>

          <button
            type="button"
            className="ghost-button"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              color: isHospital ? 'var(--text)' : '#00e5ff',
              borderColor: isHospital ? 'var(--line-bright)' : 'rgba(0, 229, 255, 0.4)',
              background: isHospital ? 'transparent' : 'rgba(0, 229, 255, 0.05)',
              fontSize: 12,
              fontWeight: 600,
              padding: '8px 16px',
              borderRadius: 4,
              cursor: 'pointer'
            }}
            onClick={() => goTo(isHospital ? '/admin/login' : '/hospital/login')}
          >
            <span>{isHospital ? '&larr; Back to Admin Control Plane' : 'Hospital Portal (Login & Registration)'}</span>
            <span>&rarr;</span>
          </button>
        </div>

        <div className="login-footer">
          <span>
            <i className="status-dot" /> ENCRYPTED SESSION
          </span>
          <span>JWT AUTHENTICATION</span>
        </div>
      </section>
    </main>
  )
}

function Sidebar({ active, onNavigate, onLogout }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark small">
          <span />
          <span />
          <span />
        </div>

        <div>
          <strong>FED SENTINEL</strong>
          <small>SECURITY CONTROL PLANE</small>
        </div>
      </div>

      <div className="system-state">
        <span className="pulse" />

        <div>
          <strong>SYSTEM OPERATIONAL</strong>
          <small>ALL CORE SERVICES ONLINE</small>
        </div>
      </div>

      <nav>
        {navGroups.map((group) => (
          <div className="nav-group" key={group.label}>
            <div className="nav-label">{group.label}</div>

            {group.items.map((item) => (
              <button
                key={item.id}
                className={`nav-item ${active === item.id ? 'active' : ''}`}
                onClick={() => onNavigate(item.id)}
              >
                <span className="nav-icon"><NavIcon name={item.icon} /></span>
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="operator">
          <div className="avatar">SA</div>

          <div>
            <strong>SUPER ADMIN</strong>
            <small>CONTROL ACCESS</small>
          </div>
        </div>

        <button className="logout" onClick={onLogout}>
          Sign out <span>&rarr;</span>
        </button>
      </div>
    </aside>
  )
}

function Metric({ label, value, detail, warning }) {
  return (
    <div className={`metric ${warning ? 'warning' : ''}`}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-detail">{detail}</div>
    </div>
  )
}

function getRoundStatus(round) {
  if (!round) return 'NO ROUND'
  return String(round.status || 'UNKNOWN').replaceAll('_', ' ')
}

function Pipeline({ round, security }) {
  const total = round?.participating_clients ?? 0
  const evidence = security?.evidence_count ?? 0
  const quarantined = round?.quarantined_updates ?? 0

  const stages = [
    ['L0', 'VERIFY', total],
    ['L1', 'INSPECT', total],
    ['L2', 'CORRELATE', total],
    ['L3', 'INFLUENCE', total],
    ['L4', 'SIMULATE', total],
    ['L5', 'ATTRIBUTE', total],
  ]

  return (
    <>
      <div className="pipeline">
        {stages.map(([code, label, count], index) => (
          <div className="pipeline-stage" key={code}>
            <div className="pipeline-node">
              <span>{code}</span>
              <b>{count}</b>
            </div>

            <div className="pipeline-label">{label}</div>

            {index < stages.length - 1 && (
              <div className="pipeline-line" />
            )}
          </div>
        ))}
      </div>

      <div className="pipeline-result">
        <div>
          <span className="result-good">&#10003; {round?.accepted_updates ?? 0}</span>
          <small>SAFE UPDATES</small>
        </div>

        <div className="result-divider" />

        <div>
          <span className="result-danger">
            &#10005; {quarantined}
          </span>
          <small>QUARANTINED</small>
        </div>

        <div className="result-divider" />

        <div>
          <span>{total}</span>
          <small>UPDATES PROCESSED</small>
        </div>

        <div className="result-divider" />

        <div>
          <span>{evidence}</span>
          <small>EVIDENCE RECORDS</small>
        </div>
      </div>
    </>
  )
}

function HospitalTopology({ hospitals, incidents }) {
  const activeHospitals = hospitals.filter(
    (hospital) => hospital.status === 'ACTIVE',
  )

  const incidentHospitalIds = new Set(
    incidents
      .map((incident) => incident.hospital_id)
      .filter(Boolean),
  )

  const visibleHospitals = activeHospitals.slice(0, 24)

  if (!visibleHospitals.length) {
    return (
      <div className="empty-state">
        <span>&#9675;</span>
        <strong>No active hospitals</strong>
        <p>
          No active federation members are currently available.
        </p>
      </div>
    )
  }

  return (
    <div className="topology">
      <div className="topology-ring ring-one" />
      <div className="topology-ring ring-two" />

      <div className="central-node">
        <span className="core-glow" />
        <strong>FED</strong>
        <small>SECURITY</small>
      </div>

      {visibleHospitals.map((hospital, index) => {
        const angle =
          (index / visibleHospitals.length) * Math.PI * 2 -
          Math.PI / 2

        const radius = visibleHospitals.length > 12 ? 40 : 37
        const x = 50 + Math.cos(angle) * radius
        const y = 50 + Math.sin(angle) * radius

        const hasIncident = incidentHospitalIds.has(hospital.id)
        const securityStatus = String(
          hospital.security_status || '',
        ).toUpperCase()

        const isThreat =
          hasIncident ||
          securityStatus === 'QUARANTINED' ||
          securityStatus === 'REVOKED'

        return (
          <div
            key={hospital.id}
            className={`command-hospital-node ${isThreat ? 'threat' : ''}`}
            style={{
              left: `${x}%`,
              top: `${y}%`,
            }}
            title={`${hospital.code || hospital.name} - ${
              hospital.security_status || hospital.status
            }`}
          >
            <span />
            <small>{hospital.code || `H${index + 1}`}</small>
          </div>
        )
      })}
    </div>
  )
}

function IncidentPanel({ incident }) {
  if (!incident) {
    return (
      <section className="panel incident-panel">
        <div className="panel-heading">
          <div>
            <div className="panel-kicker">ACTIVE INCIDENT</div>
            <h2>Threat intelligence</h2>
          </div>

          <span className="severity-safe">CLEAR</span>
        </div>

        <div className="empty-state">
          <span>&#10003;</span>
          <strong>No active incidents</strong>
          <p>
            The federation currently has no persisted security incidents.
          </p>
        </div>
      </section>
    )
  }

  const risk = Number(incident.risk_score || 0)
  const confidence = Number(incident.confidence || 0)

  const severity = String(
    incident.severity || 'UNKNOWN',
  ).toUpperCase()

  const severityClass =
    severity === 'CRITICAL'
      ? 'severity-critical'
      : severity === 'HIGH'
        ? 'severity-high'
        : severity === 'MEDIUM'
          ? 'severity-medium'
          : 'severity-safe'

  return (
    <section className="panel incident-panel">
      <div className="panel-heading">
        <div>
          <div className="panel-kicker">ACTIVE INCIDENT</div>
          <h2>Threat intelligence</h2>
        </div>

        <span className={severityClass}>{severity}</span>
      </div>

      <div className="incident-title">
        <span className="threat-symbol">!</span>

        <div>
          <strong>{incident.title}</strong>
          <small>{incident.incident_id}</small>
        </div>
      </div>

      <div className="risk-display">
        <div>
          <span>RISK SCORE</span>
          <strong>{risk.toFixed(2)}</strong>
        </div>

        <div className="risk-bar">
          <span
            style={{
              width: `${Math.min(100, Math.max(0, risk))}%`,
            }}
          />
        </div>
      </div>

      <div className="incident-grid">
        <div>
          <span>HYPOTHESIS</span>
          <strong>
            {incident.threat_hypothesis || 'UNCLASSIFIED'}
          </strong>
        </div>

        <div>
          <span>CONFIDENCE</span>
          <strong>{Math.round(confidence * 100)}%</strong>
        </div>

        <div>
          <span>RECOMMENDATION</span>
          <strong>
            {incident.recommended_action || 'REVIEW'}
          </strong>
        </div>

        <div>
          <span>STATUS</span>
          <strong>{incident.status || 'UNKNOWN'}</strong>
        </div>
      </div>

      <div className="incident-note">
        <span>i</span>
        Risk-based operational decision. Not proof of maliciousness.
      </div>
    </section>
  )
}

function ModelLineage({ latestRound, previousRound }) {
  const currentVersion =
    latestRound?.global_model_version || '-'

  const previousVersion =
    previousRound?.global_model_version || 'INITIAL MODEL'

  const previousRoundNumber =
    previousRound?.round_number || 'BASE'

  const currentRoundNumber =
    latestRound?.round_number || '-'

  return (
    <section className="panel">
      <div className="panel-heading compact">
        <div>
          <div className="panel-kicker">MODEL LINEAGE</div>
          <h2>Global model</h2>
        </div>

        <span className="pipeline-round">
          {latestRound ? `R${currentRoundNumber}` : '-'}
        </span>
      </div>

      <div className="model-lineage">
        <div className="model-node">
          <span>
            {previousRoundNumber === 'BASE'
              ? 'BASE'
              : `R${previousRoundNumber}`}
          </span>

          <strong>{previousVersion}</strong>

          <small>
            Previous verified model
          </small>
        </div>

        <div className="lineage-arrow">&rarr;</div>

        <div className="model-node current">
          <span>R{currentRoundNumber}</span>

          <strong>{currentVersion}</strong>

          <small>
            {latestRound?.accepted_updates ?? 0}{' '}
            safe updates aggregated
          </small>
        </div>
      </div>
    </section>
  )
}

function CommandCenter({ data }) {
  const latestRound = data.rounds?.[0]
  const previousRound = data.rounds?.[1]
  const incident = data.incidents?.[0]

  const accepted = latestRound?.accepted_updates ?? 0
  const quarantined = latestRound?.quarantined_updates ?? 0
  const participants = latestRound?.participating_clients ?? 0

  const activeHospitals = data.hospitals.filter(
    (hospital) => hospital.status === 'ACTIVE',
  )

  const trustedHospitals = activeHospitals.filter(
    (hospital) =>
      String(hospital.security_status || '').toUpperCase() ===
      'TRUSTED',
  ).length

  const security = data.securityRound

  const federationPosture = useMemo(() => {
    if (!latestRound) return 'STANDBY'

    if (quarantined > 0) return 'GUARDED'

    if (String(latestRound.status).toUpperCase() === 'COMPLETED') {
      return 'PROTECTED'
    }

    return 'ACTIVE'
  }, [latestRound, quarantined])

  return (
    <div className="command-page">
      <header className="page-header">
        <div>
          <div className="eyebrow">FEDERATION / COMMAND</div>

          <h1>Command Center</h1>

          <p>
            Live security posture across the federated learning network.
          </p>
        </div>

        <div className="header-state">
          <span className="pulse" />

          <div>
            <strong>{federationPosture}</strong>
            <small>CONTROL PLANE ONLINE</small>
          </div>
        </div>
      </header>

      <section className="metrics-grid">
        <Metric
          label="ACTIVE HOSPITALS"
          value={activeHospitals.length}
          detail={`${trustedHospitals} currently trusted`}
        />

        <Metric
          label="CURRENT ROUND"
          value={
            latestRound
              ? `R-${latestRound.round_number}`
              : '-'
          }
          detail={getRoundStatus(latestRound)}
        />

        <Metric
          label="UPDATES ACCEPTED"
          value={accepted}
          detail={`${participants} processed`}
        />

        <Metric
          label="QUARANTINED"
          value={quarantined}
          detail="Before aggregation"
          warning={quarantined > 0}
        />
      </section>

      <div className="dashboard-grid">
        <section className="panel topology-panel">
          <div className="panel-heading">
            <div>
              <div className="panel-kicker">
                FEDERATION TOPOLOGY
              </div>

              <h2>Distributed update network</h2>
            </div>

            <span className="live-tag">
              <i /> LIVE
            </span>
          </div>

          <HospitalTopology
            hospitals={data.hospitals}
            incidents={data.incidents}
          />

          <div className="topology-legend">
            <span>
              <i className="legend-online" /> ACTIVE
            </span>

            <span>
              <i className="legend-threat" /> SECURITY ATTENTION
            </span>

            <span>
              <i className="legend-core" /> SECURITY PLANE
            </span>
          </div>
        </section>

        <IncidentPanel incident={incident} />
      </div>

      <section className="panel security-panel">
        <div className="panel-heading">
          <div>
            <div className="panel-kicker">
              SECURITY PIPELINE
            </div>

            <h2>Evidence moves through the control plane</h2>
          </div>

          <span className="pipeline-round">
            {latestRound
              ? `ROUND ${latestRound.round_number}`
              : 'NO ROUND'}
          </span>
        </div>

        <Pipeline
          round={latestRound}
          security={security}
        />
      </section>

      <section className="bottom-grid">
        <ModelLineage
          latestRound={latestRound}
          previousRound={previousRound}
        />

        <section className="panel">
          <div className="panel-heading compact">
            <div>
              <div className="panel-kicker">
                CONTROL PRINCIPLE
              </div>

              <h2>Risk &ne; Verdict</h2>
            </div>
          </div>

          <p className="principle">
            FedSentinel correlates independent security signals
            before recommending containment. Every decision remains
            explainable, auditable and reversible.
          </p>
        </section>
      </section>
    </div>
  )
}

function FederationOverview({ data }) {
  const hospitals = Array.isArray(data.hospitals)
    ? data.hospitals
    : []

  const rounds = Array.isArray(data.rounds)
    ? data.rounds
    : []

  const incidents = Array.isArray(data.incidents)
    ? data.incidents
    : []

  const latestRound = rounds[0]

  const [selectedHospitalId, setSelectedHospitalId] = useState(null)

  const selectedHospital =
    hospitals.find((hospital) => hospital.id === selectedHospitalId) || null

  const selectedIncident =
    incidents.find(
      (incident) =>
        incident.hospital_id === selectedHospitalId ||
        incident.hospitalId === selectedHospitalId,
    ) || null

  const activeHospitals = hospitals.filter(
    (hospital) => hospital.status === 'ACTIVE',
  )

  const trusted = hospitals.filter(
    (hospital) =>
      String(hospital.security_status || '').toUpperCase() === 'TRUSTED',
  ).length

  const review = hospitals.filter((hospital) => {
    const status = String(hospital.security_status || '').toUpperCase()
    return status === 'REVIEW' || status === 'SUSPICIOUS'
  }).length

  const quarantined = hospitals.filter(
    (hospital) =>
      String(hospital.status || '').toUpperCase() === 'QUARANTINED' ||
      String(hospital.security_status || '').toUpperCase() === 'QUARANTINED',
  ).length

  const pending = hospitals.filter(
    (hospital) => String(hospital.status || '').toUpperCase() === 'PENDING',
  ).length

  const suspended = hospitals.filter(
    (hospital) => String(hospital.status || '').toUpperCase() === 'SUSPENDED',
  ).length

  const revoked = hospitals.filter(
    (hospital) => String(hospital.status || '').toUpperCase() === 'REVOKED',
  ).length

  const incidentHospitalIds = new Set(
    incidents
      .map((incident) => incident.hospital_id || incident.hospitalId)
      .filter(Boolean),
  )

  function nodeState(hospital) {
    const status = String(hospital.status || '').toUpperCase()
    const security = String(hospital.security_status || '').toUpperCase()

    if (status === 'QUARANTINED' || security === 'QUARANTINED') {
      return 'quarantined'
    }

    if (incidentHospitalIds.has(hospital.id)) {
      return 'incident'
    }

    if (
      security === 'REVIEW' ||
      security === 'SUSPICIOUS' ||
      status === 'DEGRADED'
    ) {
      return 'review'
    }

    if (status === 'SUSPENDED') {
      return 'suspended'
    }

    if (status === 'REVOKED') {
      return 'revoked'
    }

    if (status === 'ACTIVE') {
      return 'active'
    }

    return 'offline'
  }

  function parseEvidence(incident) {
    if (!incident?.evidence) return []

    if (Array.isArray(incident.evidence)) {
      return incident.evidence
    }

    if (typeof incident.evidence === 'object') {
      return incident.evidence.evidence_items || []
    }

    try {
      const parsed = JSON.parse(incident.evidence)
      return parsed.evidence_items || []
    } catch {
      return []
    }
  }

  const selectedEvidence = parseEvidence(selectedIncident)

  const riskScore = selectedIncident
    ? Number(selectedIncident.risk_score || 0)
    : 0

  const confidence = selectedIncident
    ? Number(selectedIncident.confidence || 0)
    : 0

  return (
    <div className="overview-page">
      <header className="overview-hero">
        <div>
          <div className="eyebrow">FEDERATION / SECURITY NETWORK</div>
          <h1>Federation Overview</h1>
          <p>
            Live operational view of the federated learning security network.
          </p>
        </div>

        <div className="overview-status">
          <span className="pulse" />
          <div>
            <strong>{latestRound?.status || 'NO ACTIVE ROUND'}</strong>
            <small>CONTROL PLANE STATUS</small>
          </div>
        </div>
      </header>

      <section className="overview-metrics">
        <div className="overview-metric">
          <span>FEDERATION MEMBERS</span>
          <strong>{hospitals.length}</strong>
          <small>{activeHospitals.length} active</small>
        </div>

        <div className="overview-metric">
          <span>ACTIVE NODES</span>
          <strong>{activeHospitals.length}</strong>
          <small>Eligible network participants</small>
        </div>

        <div className="overview-metric">
          <span>CURRENT ROUND</span>
          <strong>
            {latestRound ? `R-${latestRound.round_number}` : '?'}
          </strong>
          <small>{latestRound?.status || 'No round'}</small>
        </div>

        <div className={`overview-metric ${incidents.length ? 'danger' : ''}`}>
          <span>SECURITY INCIDENTS</span>
          <strong>{incidents.length}</strong>
          <small>Persisted security records</small>
        </div>
      </section>

      <section className="overview-main-grid">
        <section className="panel overview-topology-panel">
          <div className="panel-heading">
            <div>
              <div className="panel-kicker">NETWORK TOPOLOGY</div>
              <h2>Federated Hospital Network</h2>
            </div>

            <span className="live-tag">
              <i /> LIVE
            </span>
          </div>

          <div className="interactive-topology">
            <div className="topology-orbit orbit-inner" />
            <div className="topology-orbit orbit-outer" />

            <div className="topology-core">
              <span className="topology-core-pulse" />
              <strong>FED</strong>
              <small>SECURITY</small>
            </div>

            {hospitals.map((hospital, index) => {
              const count = Math.max(hospitals.length, 1)
              const angle = (index / count) * Math.PI * 2 - Math.PI / 2
              const radius = hospitals.length > 18 ? 38 : 35

              const x = 50 + Math.cos(angle) * radius
              const y = 50 + Math.sin(angle) * radius

              const state = nodeState(hospital)
              const selected = hospital.id === selectedHospitalId

              return (
                <button
                  type="button"
                  key={hospital.id}
                  className={`interactive-hospital-node ${state} ${
                    selected ? 'selected' : ''
                  }`}
                  style={{
                    left: `${x}%`,
                    top: `${y}%`,
                  }}
                  onClick={() => setSelectedHospitalId(hospital.id)}
                  title={`${hospital.code || hospital.name} ? ${state}`}
                >
                  <span className="node-pulse" />
                  <b>{hospital.code || 'NODE'}</b>
                  <small>{state.toUpperCase()}</small>
                </button>
              )
            })}
          </div>

          <div className="topology-legend">
            <span>
              <i className="legend-online" /> ACTIVE
            </span>
            <span>
              <i className="legend-threat" /> INCIDENT
            </span>
            <span>
              <i className="legend-review" /> REVIEW
            </span>
            <span>
              <i className="legend-core" /> SECURITY PLANE
            </span>
          </div>
        </section>

        <aside className="panel network-posture">
          <div className="panel-heading">
            <div>
              <div className="panel-kicker">SECURITY POSTURE</div>
              <h2>Network Trust State</h2>
            </div>
          </div>

          {(() => {
            const trustRecords = Array.isArray(data.trustRecords)
              ? data.trustRecords
              : []

            const getTrustState = (record) =>
              String(
                record.decision ||
                  record.status ||
                  record.trust_status ||
                  '',
              ).toUpperCase()

            const trustedCount = trustRecords.filter(
              (record) => getTrustState(record) === 'TRUSTED',
            ).length

            const reviewCount = trustRecords.filter(
              (record) => getTrustState(record) === 'REVIEW',
            ).length

            const suspiciousCount = trustRecords.filter(
              (record) => getTrustState(record) === 'SUSPICIOUS',
            ).length

            const quarantinedCount = trustRecords.filter(
              (record) => getTrustState(record) === 'QUARANTINED',
            ).length

            const totalNodes = hospitals.length

            const barWidth = (value) =>
              totalNodes > 0
                ? `${Math.min(100, (value / totalNodes) * 100)}%`
                : '0%'

            return (
              <>
                <div className="posture-total">
                  <strong>{totalNodes}</strong>
                  <span>TOTAL FEDERATION NODES</span>
                </div>

                <div className="posture-bars">
                  <div>
                    <label>
                      <span>TRUSTED</span>
                      <b>{trustedCount}</b>
                    </label>
                    <div>
                      <i style={{ width: barWidth(trustedCount) }} />
                    </div>
                  </div>

                  <div>
                    <label>
                      <span>REVIEW</span>
                      <b>{reviewCount}</b>
                    </label>
                    <div>
                      <i style={{ width: barWidth(reviewCount) }} />
                    </div>
                  </div>

                  <div>
                    <label>
                      <span>SUSPICIOUS</span>
                      <b>{suspiciousCount}</b>
                    </label>
                    <div>
                      <i style={{ width: barWidth(suspiciousCount) }} />
                    </div>
                  </div>

                  <div>
                    <label>
                      <span>QUARANTINED</span>
                      <b>{quarantinedCount}</b>
                    </label>
                    <div>
                      <i style={{ width: barWidth(quarantinedCount) }} />
                    </div>
                  </div>
                </div>

                <div className="trust-record-summary">
                  {trustRecords.length > 0
                    ? `${trustRecords.length} trust records analyzed in R-${latestRound?.round_number || '?'}`
                    : 'NO TRUST RECORDS FOR CURRENT ROUND'}
                </div>
              </>
            )
          })()}

          <div className="lifecycle-grid">
            <div>
              <span>PENDING</span>
              <strong>{pending}</strong>
            </div>
            <div>
              <span>SUSPENDED</span>
              <strong>{suspended}</strong>
            </div>
            <div>
              <span>QUARANTINED</span>
              <strong>{quarantined}</strong>
            </div>
            <div>
              <span>REVOKED</span>
              <strong>{revoked}</strong>
            </div>
          </div>
        </aside>
      </section>

      <section className="overview-lower-grid">
        <section className="panel rounds-panel">
          <div className="panel-heading">
            <div>
              <div className="panel-kicker">ROUND ACTIVITY</div>
              <h2>Federation Rounds</h2>
            </div>
          </div>

          <div className="round-list">
            {rounds.slice(0, 5).map((round) => (
              <div className="round-row" key={round.id}>
                <div>
                  <strong>R-{round.round_number}</strong>
                  <small>{round.status}</small>
                </div>

                <span>{round.participating_clients ?? 0} participants</span>
                <span className="round-accepted">
                  {round.accepted_updates ?? 0} accepted
                </span>
                <span className="round-quarantined">
                  {round.quarantined_updates ?? 0} quarantined
                </span>
              </div>
            ))}

            {!rounds.length && (
              <div className="empty-state">
                <strong>No federation rounds</strong>
                <p>No persistent round records are available.</p>
              </div>
            )}
          </div>
        </section>

        <section className="panel pipeline-panel">
          <div className="panel-heading">
            <div>
              <div className="panel-kicker">CONTROL PLANE</div>
              <h2>Security Pipeline</h2>
            </div>
          </div>

          <div className="overview-security-pipeline">
            {[
              ['L0', 'VERIFY'],
              ['L1', 'INSPECT'],
              ['L2', 'CORRELATE'],
              ['L3', 'INFLUENCE'],
              ['L4', 'SIMULATE'],
              ['L5', 'ATTRIBUTE'],
            ].map(([code, label], index, stages) => (
              <div className="overview-stage" key={code}>
                <div className="overview-stage-node">
                  <strong>{code}</strong>
                  <small>{label}</small>
                </div>

                {index < stages.length - 1 && (
                  <span className="overview-stage-line" />
                )}
              </div>
            ))}
          </div>

          <div className="risk-principle">
            <div className="panel-kicker">CONTROL PRINCIPLE</div>
            <h3>RISK &ne; VERDICT</h3>
            <p>
              Independent security signals are correlated before containment
              is recommended. A risk signal is not proof of maliciousness.
            </p>
          </div>
        </section>
      </section>

      <section className="overview-activity panel">
        <div className="panel-heading">
          <div>
            <div className="panel-kicker">SECURITY ACTIVITY</div>
            <h2>Latest Federation State</h2>
          </div>

          <span className="activity-round">
            {latestRound ? `R-${latestRound.round_number}` : 'NO ROUND'}
          </span>
        </div>

        <div className="activity-strip">
          <div className="activity-step complete">
            <span>01</span>
            <strong>UPDATE INTAKE</strong>
            <small>{latestRound?.participating_clients ?? 0} submissions</small>
          </div>

          <div className="activity-connector" />

          <div className="activity-step complete">
            <span>02</span>
            <strong>L0 VERIFY</strong>
            <small>Artifact validation</small>
          </div>

          <div className="activity-connector" />

          <div className="activity-step complete">
            <span>03</span>
            <strong>L2 CORRELATE</strong>
            <small>{latestRound?.quarantined_updates ?? 0} quarantined</small>
          </div>

          <div className="activity-connector" />

          <div className="activity-step complete">
            <span>04</span>
            <strong>TRUST ENGINE</strong>
            <small>{incidents.length} incident(s)</small>
          </div>

          <div className="activity-connector" />

          <div className="activity-step complete">
            <span>05</span>
            <strong>MODEL STATE</strong>
            <small>
              {latestRound?.global_model_version || 'No verified model'}
            </small>
          </div>
        </div>
      </section>

      {selectedHospital && (
        <div
          className="hospital-drawer-backdrop"
          onClick={() => setSelectedHospitalId(null)}
          role="presentation"
        >
          <aside
            className="hospital-drawer"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="drawer-header">
              <div>
                <div className="panel-kicker">NODE INTELLIGENCE</div>
                <h2>{selectedHospital.code}</h2>
                <p>{selectedHospital.name}</p>
              </div>

              <button
                type="button"
                className="drawer-close"
                onClick={() => setSelectedHospitalId(null)}
              >
                <X size={16} strokeWidth={1.8} />
              </button>
            </div>

            <div className="drawer-state">
              <span className={`drawer-state-dot ${nodeState(selectedHospital)}`} />
              <div>
                <strong>{selectedHospital.status || 'UNKNOWN'}</strong>
                <small>
                  {selectedHospital.security_status || 'NO SECURITY STATE'}
                </small>
              </div>
            </div>

            <div className="drawer-section">
              <div className="drawer-section-title">FEDERATION MEMBERSHIP</div>

              <div className="drawer-grid">
                <div>
                  <span>ELIGIBLE</span>
                  <strong>
                    {selectedHospital.is_eligible ? 'YES' : 'NO'}
                  </strong>
                </div>

                <div>
                  <span>LOCATION</span>
                  <strong>{selectedHospital.location || '?'}</strong>
                </div>

                <div>
                  <span>CONTACT</span>
                  <strong>{selectedHospital.contact_email || '?'}</strong>
                </div>

                <div>
                  <span>LAST UPDATED</span>
                  <strong>
                    {selectedHospital.updated_at
                      ? new Date(selectedHospital.updated_at).toLocaleString()
                      : '?'}
                  </strong>
                </div>
              </div>
            </div>

            <div className="drawer-section">
              <div className="drawer-section-title">
                LATEST ROUND
              </div>

              <div className="drawer-round-card">
                <div>
                  <span>ROUND</span>
                  <strong>
                    {latestRound ? `R-${latestRound.round_number}` : '?'}
                  </strong>
                </div>

                <div>
                  <span>STATUS</span>
                  <strong>{latestRound?.status || '?'}</strong>
                </div>
              </div>
            </div>

            {selectedIncident ? (
              <div className="drawer-section incident-evidence">
                <div className="drawer-section-title">
                  SECURITY EVIDENCE
                </div>

                <div className="drawer-risk">
                  <div>
                    <span>RISK SCORE</span>
                    <strong>{riskScore.toFixed(2)}</strong>
                  </div>

                  <div>
                    <span>CONFIDENCE</span>
                    <strong>{Math.round(confidence * 100)}%</strong>
                  </div>
                </div>

                <div className="drawer-evidence-grid">
                  <div>
                    <span>HYPOTHESIS</span>
                    <strong>
                      {selectedIncident.threat_hypothesis ||
                        selectedIncident.threat_type ||
                        'ANOMALOUS UPDATE'}
                    </strong>
                  </div>

                  <div>
                    <span>RECOMMENDATION</span>
                    <strong>
                      {selectedIncident.recommended_action || 'REVIEW'}
                    </strong>
                  </div>

                  <div>
                    <span>INCIDENT STATUS</span>
                    <strong>{selectedIncident.status || 'OPEN'}</strong>
                  </div>

                  <div>
                    <span>SEVERITY</span>
                    <strong>{selectedIncident.severity || '?'}</strong>
                  </div>
                </div>

                <div className="evidence-list">
                  {selectedEvidence.length ? (
                    selectedEvidence.map((item, index) => (
                      <div className="evidence-item" key={`${item}-${index}`}>
                        <span>{String(index + 1).padStart(2, '0')}</span>
                        <p>{item}</p>
                      </div>
                    ))
                  ) : (
                    <div className="evidence-item">
                      <span className="preview-mark">?</span>
                      <p>Incident evidence is not available in this response.</p>
                    </div>
                  )}
                </div>

                <div className="drawer-warning">
                  <strong>RISK &ne; VERDICT</strong>
                  <p>
                    This security record represents accumulated evidence and
                    an operational recommendation. It is not proof of
                    maliciousness.
                  </p>
                </div>
              </div>
            ) : (
              <div className="drawer-section">
                <div className="drawer-section-title">
                  SECURITY STATE
                </div>

                <div className="drawer-clean-state">
                  <span className="preview-mark">?</span>
                  <div>
                    <strong>No persisted incident for this node</strong>
                    <p>
                      The absence of an incident is not a claim that the
                      hospital is permanently trusted.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </aside>
        </div>
      )}
    </div>
  )
}


function HospitalsPage({ data, token, onDataRefresh }) {
  const hospitals = Array.isArray(data.hospitals)
    ? data.hospitals
    : []

  const incidents = Array.isArray(data.incidents) ? data.incidents : []
  const incidentHospitalIds = new Set(incidents.map((incident) => incident.hospital_id || incident.hospitalId).filter(Boolean))

  const incidentByHospitalId = new Map(
    incidents.map((incident) => [
      incident.hospital_id || incident.hospitalId,
      incident,
    ])
  )

  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [securityFilter, setSecurityFilter] = useState('ALL')
  const [selected, setSelected] = useState(null)
  const [busyId, setBusyId] = useState(null)
  const [actionError, setActionError] = useState('')
  const [showAdd, setShowAdd] = useState(false)

  const selectedIncident = selected
    ? incidents.find(
        (incident) =>
          incident.hospital_id === selected.id ||
          incident.hospitalId === selected.id,
      ) || null
    : null

  const selectedRiskScore = selectedIncident
    ? Number(
        selectedIncident.risk_score ??
          selectedIncident.riskScore ??
          0,
      )
    : 0

  const selectedConfidence = selectedIncident
    ? Number(selectedIncident.confidence ?? 0)
    : 0

  const selectedRiskLevel =
    selectedRiskScore >= 70
      ? 'HIGH'
      : selectedRiskScore >= 30
        ? 'MEDIUM'
        : selectedRiskScore > 0
          ? 'LOW'
          : 'NORMAL'

  const filteredHospitals = hospitals.filter((hospital) => {
    const query = search.trim().toLowerCase()

    const matchesSearch =
      !query ||
      String(hospital.code || '').toLowerCase().includes(query) ||
      String(hospital.name || '').toLowerCase().includes(query) ||
      String(hospital.location || '').toLowerCase().includes(query)

    const matchesStatus =
      statusFilter === 'ALL' ||
      String(hospital.status || '').toUpperCase() === statusFilter

    const matchesSecurity =
      securityFilter === 'ALL' ||
      String(hospital.security_status || '').toUpperCase() ===
        securityFilter

    return matchesSearch && matchesStatus && matchesSecurity
  })

  const statusCounts = {
    ALL: hospitals.length,
    ACTIVE: hospitals.filter(
      (h) => String(h.status).toUpperCase() === 'ACTIVE',
    ).length,
    PENDING: hospitals.filter(
      (h) => String(h.status).toUpperCase() === 'PENDING',
    ).length,
    SUSPENDED: hospitals.filter(
      (h) => String(h.status).toUpperCase() === 'SUSPENDED',
    ).length,
    QUARANTINED: hospitals.filter(
      (h) => String(h.status).toUpperCase() === 'QUARANTINED',
    ).length,
    REVOKED: hospitals.filter(
      (h) => String(h.status).toUpperCase() === 'REVOKED',
    ).length,
  }

  async function hospitalAction(hospital, action, reason = '') {
    setBusyId(hospital.id)
    setActionError('')

    try {
      const body =
        reason.trim().length > 0
          ? JSON.stringify({ reason: reason.trim() })
          : undefined

      await apiFetch(
        `/api/v1/hospitals/${hospital.id}/${action}`,
        token,
        {
          method: 'POST',
          ...(body ? { body } : {}),
        },
      )

      setSelected(null)

      if (onDataRefresh) {
        await onDataRefresh()
      }
    } catch (err) {
      if (err.message !== 'SESSION_EXPIRED') {
        setActionError(err.message || 'Hospital action failed')
      }
    } finally {
      setBusyId(null)
    }
  }

  function getSecurityClass(status) {
    const value = String(status || '').toUpperCase()

    if (value === 'TRUSTED') return 'trusted'
    if (value === 'REVIEW') return 'review'
    if (value === 'SUSPICIOUS') return 'suspicious'
    if (value === 'QUARANTINED') return 'quarantined'

    return 'neutral'
  }

  function getStatusClass(status) {
    return String(status || 'UNKNOWN')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
  }

  return (
    <div className="hospitals-page">

      <header className="page-header hospitals-header">
        <div>
          <div className="eyebrow">FEDERATION / HOSPITALS</div>
          <h1>Hospital Control Center</h1>
          <p>
            Manage federation membership, lifecycle state, and security
            posture across participating hospitals.
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={() => {
            setActionError('')
            setShowAdd(true)
          }}
        >
          + ADD HOSPITAL
        </button>
      </header>

      <section className="hospital-metrics">

        <div className="hospital-stat">
          <span>FEDERATION NODES</span>
          <strong>{hospitals.length}</strong>
          <small>Registered hospitals</small>
        </div>

        <div className="hospital-stat">
          <span>ACTIVE</span>
          <strong>{statusCounts.ACTIVE}</strong>
          <small>Eligible lifecycle nodes</small>
        </div>

        <div className="hospital-stat">
          <span>QUARANTINED</span>
          <strong>{statusCounts.QUARANTINED}</strong>
          <small>Lifecycle quarantine</small>
        </div>

        <div className="hospital-stat">
          <span>INCIDENTS</span>
          <strong>{data.incidents?.length || 0}</strong>
          <small>Current security records</small>
        </div>

      </section>

      <section className="panel hospital-controls">

        <div className="hospital-search">
          <Search size={15} />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search code, hospital name, or location..."
          />
        </div>

        <div className="hospital-filters">

          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            <option value="ALL">ALL STATUS</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="PENDING">PENDING</option>
            <option value="SUSPENDED">SUSPENDED</option>
            <option value="QUARANTINED">QUARANTINED</option>
            <option value="REVOKED">REVOKED</option>
          </select>

          <select
            value={securityFilter}
            onChange={(event) => setSecurityFilter(event.target.value)}
          >
            <option value="ALL">ALL SECURITY</option>
            <option value="TRUSTED">TRUSTED</option>
            <option value="REVIEW">REVIEW</option>
            <option value="SUSPICIOUS">SUSPICIOUS</option>
            <option value="QUARANTINED">QUARANTINED</option>
          </select>

        </div>

      </section>

      {actionError && (
        <div className="hospital-action-error">
          <AlertTriangle size={14} />
          <span>{actionError}</span>
        </div>
      )}

      <section className="panel hospital-list-panel">

        <div className="panel-heading">
          <div>
            <div className="panel-kicker">FEDERATION DIRECTORY</div>
            <h2>Participating Hospitals</h2>
          </div>

          <span className="pipeline-round">
            {filteredHospitals.length} / {hospitals.length}
          </span>
        </div>

        <div className="hospital-list">

          {filteredHospitals.length === 0 ? (
            <div className="hospital-empty">
              <Hospital size={24} />
              <strong>NO HOSPITALS MATCH</strong>
              <small>
                Adjust the search or lifecycle/security filters.
              </small>
            </div>
          ) : (
            filteredHospitals.map((hospital) => {

              const securityStatus =
                String(hospital.security_status || 'UNKNOWN').toUpperCase()

              const lifecycleStatus =
                String(hospital.status || 'UNKNOWN').toUpperCase()

              const hospitalIncident =
                incidentByHospitalId.get(hospital.id)

              const riskScore = hospitalIncident
                ? Number(
                    hospitalIncident.risk_score ??
                      hospitalIncident.riskScore ??
                      0,
                  )
                : 0

              const riskLevel =
                riskScore >= 70
                  ? 'HIGH'
                  : riskScore >= 30
                    ? 'MEDIUM'
                    : riskScore > 0
                      ? 'LOW'
                      : 'NORMAL'


              const isBusy = busyId === hospital.id

              return (
                <article
                  className={`hospital-row ${incidentHospitalIds.has(hospital.id) ? 'has-incident' : ''}`}
                  key={hospital.id}
                  role="button"
                  tabIndex={0}
                  onClick={() => setSelected(hospital)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault()
                      setSelected(hospital)
                    }
                  }}
                >

                  <div className="hospital-identity">

                    <div className={`hospital-node ${getSecurityClass(securityStatus)}`}>
                      {hospital.code}
                    </div>

                    <div>
                      <strong>{hospital.name}</strong>

                      <small>
                        {hospital.location || 'Location not provided'}
                      </small>

                      <small>
                        {hospital.contact_email || 'No contact email'}
                      </small>
                    </div>

                  </div>

                                    {hospitalIncident ? (
                    <div className="hospital-security-attention">
                      <div className="security-attention-label">
                        SECURITY ATTENTION
                      </div>

                      <div className="hospital-risk-metrics">
                        <div className="hospital-risk-metric">
                          <span>RISK SCORE</span>
                          <strong>
                            {Math.round(riskScore)} / 100
                          </strong>
                        </div>

                        <div className="hospital-risk-metric">
                          <span>SEVERITY</span>
                          <strong>
                            {String(
                              hospitalIncident.severity || riskLevel
                            ).toUpperCase()}
                          </strong>
                        </div>
                      </div>

                      <div className="hospital-incident-type">
                        {String(
                          hospitalIncident.incident_type ||
                          hospitalIncident.incidentType ||
                          hospitalIncident.type ||
                          'SECURITY INCIDENT'
                        ).replaceAll('_', ' ')}
                      </div>
                    </div>
                  ) : (
                    <div className="hospital-security-normal">
                      <div className="security-normal-label">
                        SECURITY STATUS
                      </div>

                      <strong>NORMAL</strong>

                      <div className="hospital-risk-normal">
                        RISK SCORE <b>0 / 100</b>
                      </div>
                    </div>
                  )}
<div className="hospital-state">

                    <span
                      className={`hospital-badge status-${getStatusClass(
                        lifecycleStatus,
                      )}`}
                    >
                      {lifecycleStatus}
                    </span>

                    <span
                      className={`hospital-badge security-${getSecurityClass(
                        securityStatus,
                      )}`}
                    >
                      {securityStatus}
                    </span>

                    <span
                      className={
                        hospital.is_eligible
                          ? 'eligibility yes'
                          : 'eligibility no'
                      }
                    >
                      {hospital.is_eligible ? 'ELIGIBLE' : 'INELIGIBLE'}
                    </span>

                  </div>

                  <div className="hospital-card-entry">
                    <span>INSPECT NODE</span>
                    <strong>?</strong>
                  </div>

                </article>
              )
            })
          )}

        </div>

      </section>

      {selected && (
        <div
          className="hospital-drawer-backdrop"
          role="presentation"
          onClick={() => setSelected(null)}
        >
          <aside
            className="hospital-management-drawer"
            role="dialog"
            aria-modal="true"
            onClick={(event) => event.stopPropagation()}
          >

            <div className="hospital-drawer-header">
              <div>
                <div className="panel-kicker">
                  NODE MANAGEMENT
                </div>
                <h2>{selected.code}</h2>
                <p>{selected.name}</p>
              </div>

              <button
                type="button"
                className="drawer-close"
                aria-label="Close"
                onClick={() => setSelected(null)}
              >
                ?
              </button>
            </div>

            <div className="hospital-detail-status">
              <span
                className={`hospital-badge status-${getStatusClass(
                  selected.status,
                )}`}
              >
                {String(selected.status || 'UNKNOWN').toUpperCase()}
              </span>

              <span
                className={`hospital-badge security-${getSecurityClass(
                  selected.security_status,
                )}`}
              >
                {String(
                  selected.security_status || 'UNKNOWN',
                ).toUpperCase()}
              </span>
            </div>

            <div className="hospital-detail-grid">

              <div>
                <span>HOSPITAL CODE</span>
                <strong>{selected.code}</strong>
              </div>

              <div>
                <span>ELIGIBILITY</span>
                <strong>
                  {selected.is_eligible ? 'YES' : 'NO'}
                </strong>
              </div>

              <div>
                <span>LOCATION</span>
                <strong>
                  {selected.location || 'Not specified'}
                </strong>
              </div>

              <div>
                <span>CONTACT</span>
                <strong>
                  {selected.contact_email || 'Not provided'}
                </strong>
              </div>

              <div>
                <span>PHONE</span>
                <strong>
                  {selected.contact_phone || 'Not provided'}
                </strong>
              </div>

              <div>
                <span>CREATED</span>
                <strong>
                  {selected.created_at
                    ? new Date(selected.created_at).toLocaleDateString()
                    : 'Not available'}
                </strong>
              </div>

            </div>

            <section className="hospital-control-section">
              <div className="hospital-control-section-header">
                <span>SECURITY STATE</span>
                <Shield size={13} />
              </div>

              <div className="hospital-security-state">
                <div className="security-state-row">
                  <span>TRUST STATUS</span>
                  <strong>
                    {String(
                      selected.security_status || 'UNKNOWN',
                    ).toUpperCase()}
                  </strong>
                </div>

                <div className="security-state-row">
                  <span>ROUND ELIGIBILITY</span>
                  <strong>
                    {selected.is_eligible ? 'ELIGIBLE' : 'NOT ELIGIBLE'}
                  </strong>
                </div>

                {selectedIncident ? (
                  <div className="hospital-incident-state">
                    <div className="incident-state-heading">
                      <span>ACTIVE INCIDENT</span>
                      <span className="incident-state-badge">
                        {String(
                          selectedIncident.severity || 'UNKNOWN',
                        ).toUpperCase()}
                      </span>
                    </div>

                    <strong>
                      {String(
                        selectedIncident.incident_type ||
                        selectedIncident.type ||
                        'SECURITY INCIDENT',
                      ).replaceAll('_', ' ')}
                    </strong>

                    <div className="incident-state-details">
                      <div>
                        <span>RISK</span>
                        <strong>
                          {selectedRiskScore != null
                            ? Number(selectedRiskScore).toFixed(2)
                            : 'N/A'}
                        </strong>
                      </div>

                      <div>
                        <span>CONFIDENCE</span>
                        <strong>
                          {selectedConfidence != null
                            ? `${(
                                Number(selectedConfidence) * 100
                              ).toFixed(1)}%`
                            : 'N/A'}
                        </strong>
                      </div>

                      <div>
                        <span>STATUS</span>
                        <strong>
                          {String(
                            selectedIncident.status || 'OPEN',
                          ).toUpperCase()}
                        </strong>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="hospital-security-clear">
                    <Shield size={14} />
                    <span>No active incident recorded for this hospital.</span>
                  </div>
                )}
              </div>
            </section>

            <div className="hospital-management-actions">

              <div className="panel-kicker">
                LIFECYCLE CONTROL
              </div>

              {String(selected.status).toUpperCase() === 'PENDING' && (
                <button
                  type="button"
                  disabled={busyId === selected.id}
                  onClick={() =>
                    hospitalAction(selected, 'approve')
                  }
                >
                  APPROVE HOSPITAL
                </button>
              )}

              {String(selected.status).toUpperCase() === 'ACTIVE' && (
                <>
                  <button
                    type="button"
                    disabled={busyId === selected.id}
                    onClick={() =>
                      hospitalAction(
                        selected,
                        'suspend',
                        'Suspended by federation administrator',
                      )
                    }
                  >
                    SUSPEND
                  </button>

                  <button
                    type="button"
                    disabled={busyId === selected.id}
                    onClick={() =>
                      hospitalAction(
                        selected,
                        'quarantine',
                        'Hospital quarantined by federation administrator',
                      )
                    }
                  >
                    QUARANTINE
                  </button>

                  <button
                    type="button"
                    disabled={busyId === selected.id}
                    onClick={() =>
                      hospitalAction(
                        selected,
                        'remove',
                        'Removed from federation membership',
                      )
                    }
                  >
                    REMOVE FROM FEDERATION
                  </button>

                  <button
                    type="button"
                    disabled={busyId === selected.id}
                    onClick={() =>
                      hospitalAction(
                        selected,
                        'revoke',
                        'Federation access revoked by administrator',
                      )
                    }
                  >
                    REVOKE
                  </button>
                </>
              )}

              {String(selected.status).toUpperCase() === 'SUSPENDED' && (
                <button
                  type="button"
                  disabled={busyId === selected.id}
                  onClick={() =>
                    hospitalAction(selected, 'restore')
                  }
                >
                  RESTORE HOSPITAL
                </button>
              )}

              {String(selected.status).toUpperCase() === 'QUARANTINED' && (
                <button
                  type="button"
                  disabled={busyId === selected.id}
                  onClick={() =>
                    hospitalAction(selected, 'release')
                  }
                >
                  RELEASE QUARANTINE
                </button>
              )}

            </div>

            <div className="hospital-management-note">
              <Shield size={14} />
              <span>
                Lifecycle actions are audited and do not bypass the
                federated security pipeline.
              </span>
            </div>

          </aside>
        </div>
      )}

      {showAdd && (
        <AddHospitalModal
          token={token}
          onClose={() => setShowAdd(false)}
          onCreated={async () => {
            setShowAdd(false)
            if (onDataRefresh) {
              await onDataRefresh()
            }
          }}
        />
      )}

    </div>
  )
}

function AddHospitalModal({ token, onClose, onCreated }) {
  const [form, setForm] = useState({
    code: '',
    name: '',
    contact_email: '',
    contact_phone: '',
    location: '',
    description: '',
  })

  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function submit(event) {
    event.preventDefault()
    setSaving(true)
    setError('')

    try {
      await apiFetch(
        '/api/v1/hospitals',
        token,
        {
          method: 'POST',
          body: JSON.stringify(form),
        },
      )

      await onCreated()
    } catch (err) {
      if (err.message !== 'SESSION_EXPIRED') {
        setError(err.message || 'Unable to create hospital')
      }
    } finally {
      setSaving(false)
    }
  }

  function update(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }))
  }

  return (
    <div
      className="hospital-modal-backdrop"
      role="presentation"
      onClick={onClose}
    >
      <form
        className="hospital-modal add-hospital-modal"
        onSubmit={submit}
        onClick={(event) => event.stopPropagation()}
      >

        <div className="hospital-modal-header">
          <div>
            <div className="panel-kicker">
              FEDERATION ADMINISTRATION
            </div>
            <h2>Add Hospital</h2>
            <p>Register a new federation node.</p>
          </div>

          <button
            type="button"
            className="drawer-close"
            aria-label="Close"
            onClick={onClose}
          >
            ?
          </button>
        </div>

        <label>
          HOSPITAL CODE
          <input
            required
            value={form.code}
            onChange={(event) =>
              update('code', event.target.value)
            }
            placeholder="H22"
          />
        </label>

        <label>
          HOSPITAL NAME
          <input
            required
            value={form.name}
            onChange={(event) =>
              update('name', event.target.value)
            }
            placeholder="Federated Medical Center"
          />
        </label>

        <label>
          CONTACT EMAIL
          <input
            type="email"
            value={form.contact_email}
            onChange={(event) =>
              update('contact_email', event.target.value)
            }
          />
        </label>

        <label>
          CONTACT PHONE
          <input
            value={form.contact_phone}
            onChange={(event) =>
              update('contact_phone', event.target.value)
            }
          />
        </label>

        <label>
          LOCATION
          <input
            value={form.location}
            onChange={(event) =>
              update('location', event.target.value)
            }
            placeholder="Chennai, India"
          />
        </label>

        <label>
          DESCRIPTION
          <textarea
            value={form.description}
            onChange={(event) =>
              update('description', event.target.value)
            }
            rows={3}
          />
        </label>

        {error && (
          <div className="form-error">
            {error}
          </div>
        )}

        <div className="add-hospital-actions">
          <button
            type="button"
            onClick={onClose}
          >
            CANCEL
          </button>

          <button
            type="submit"
            className="primary-button"
            disabled={saving}
          >
            {saving ? 'REGISTERING...' : 'REGISTER HOSPITAL'}
          </button>
        </div>

      </form>
    </div>
  )
}


function HospitalControlCenter({ data, token, onDataRefresh }) {
  const hospitals = Array.isArray(data.hospitals) ? data.hospitals : []
  const incidents = Array.isArray(data.incidents) ? data.incidents : []

  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [securityFilter, setSecurityFilter] = useState('ALL')
  const [selectedHospitalId, setSelectedHospitalId] = useState(null)
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState('')

  const selectedHospital =
    hospitals.find((hospital) => hospital.id === selectedHospitalId) || null

  const filteredHospitals = useMemo(() => {
    const query = search.trim().toLowerCase()

    return [...hospitals]
      .filter((hospital) => {
        if (!query) return true

        return [
          hospital.code,
          hospital.name,
          hospital.location,
          hospital.contact_email,
          hospital.contact_phone,
        ]
          .filter(Boolean)
          .some((value) =>
            String(value).toLowerCase().includes(query),
          )
      })
      .filter((hospital) => {
        if (statusFilter === 'ALL') return true
        return String(hospital.status || '').toUpperCase() === statusFilter
      })
      .filter((hospital) => {
        if (securityFilter === 'ALL') return true
        return (
          String(hospital.security_status || '').toUpperCase() ===
          securityFilter
        )
      })
      .sort((a, b) =>
        String(a.code || '').localeCompare(String(b.code || ''), undefined, {
          numeric: true,
        }),
      )
  }, [hospitals, search, statusFilter, securityFilter])

  const activeCount = hospitals.filter(
    (hospital) =>
      String(hospital.status || '').toUpperCase() === 'ACTIVE',
  ).length

  const quarantinedCount = hospitals.filter(
    (hospital) =>
      String(hospital.status || '').toUpperCase() === 'QUARANTINED',
  ).length

  const incidentHospitalIds = new Set(
    incidents.map((incident) => incident.hospital_id).filter(Boolean),
  )

  const incidentCount = incidents.length

  const statusLabel = (value) =>
    String(value || 'UNKNOWN').replaceAll('_', ' ')

  async function performAction(action) {
    if (!selectedHospital) return

    setActionLoading(true)
    setActionError('')

    try {
      const endpoint =
        `/api/v1/hospitals/${selectedHospital.id}/${action}`

      await apiFetch(endpoint, token, {
        method: 'POST',
        body: JSON.stringify({
          reason: `Hospital lifecycle action: ${action}`,
        }),
      })

      setSelectedHospitalId(null)

      if (onDataRefresh) {
        await onDataRefresh()
      }
    } catch (error) {
      setActionError(error.message || 'Action failed')
    } finally {
      setActionLoading(false)
    }
  }

  return (
    <div className="hospital-page">
      <header className="page-header hospital-page-header">
        <div>
          <div className="eyebrow">FEDERATION / HOSPITALS</div>
          <h1>Hospital Control Center</h1>
          <p>
            Manage federation membership, lifecycle state, and security
            posture across participating hospitals.
          </p>
        </div>

        <button
          className="primary-button hospital-add-button"
          type="button"
          onClick={() => {
            window.alert(
              'Hospital registration is available through the backend registration workflow.',
            )
          }}
        >
          <span>+</span>
          ADD HOSPITAL
        </button>
      </header>

      <section className="hospital-metrics">
        <div className="hospital-metric">
          <span>FEDERATION NODES</span>
          <strong>{hospitals.length}</strong>
          <small>Registered hospitals</small>
          <div className="metric-icon"><Building2 size={16} /></div>
        </div>

        <div className="hospital-metric">
          <span>ACTIVE</span>
          <strong>{activeCount}</strong>
          <small>Eligible lifecycle nodes</small>
          <div className="metric-icon"><Building2 size={16} /></div>
        </div>

        <div className="hospital-metric">
          <span>QUARANTINED</span>
          <strong>{quarantinedCount}</strong>
          <small>Under lifecycle quarantine</small>
          <div className="metric-icon danger-icon"><ShieldAlert size={16} /></div>
        </div>

        <div className="hospital-metric">
          <span>INCIDENTS</span>
          <strong>{incidentCount}</strong>
          <small>Current security records</small>
          <div className="metric-icon"><Building2 size={16} /></div>
        </div>
      </section>

      <section className="hospital-toolbar panel">
        <div className="hospital-search">
          <Search size={15} />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search hospitals by code, name, location, or contact..."
          />
        </div>

        <select
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
        >
          <option value="ALL">ALL STATUS</option>
          <option value="ACTIVE">ACTIVE</option>
          <option value="PENDING">PENDING</option>
          <option value="SUSPENDED">SUSPENDED</option>
          <option value="QUARANTINED">QUARANTINED</option>
          <option value="REVOKED">REVOKED</option>
          <option value="INACTIVE">INACTIVE</option>
        </select>

        <select
          value={securityFilter}
          onChange={(event) => setSecurityFilter(event.target.value)}
        >
          <option value="ALL">ALL SECURITY</option>
          <option value="TRUSTED">TRUSTED</option>
          <option value="REVIEW">REVIEW</option>
          <option value="SUSPICIOUS">SUSPICIOUS</option>
          <option value="QUARANTINED">QUARANTINED</option>
        </select>

        <div className="hospital-result-count">
          {filteredHospitals.length} / {hospitals.length} NODES
        </div>
      </section>

      <section className="hospital-directory panel">
        <div className="hospital-directory-header">
          <div>
            <div className="panel-kicker">FEDERATION DIRECTORY</div>
            <h2>Participating Hospitals</h2>
          </div>

          <span className="directory-count">
            {filteredHospitals.length} / {hospitals.length}
          </span>
        </div>

        {filteredHospitals.length === 0 ? (
          <div className="hospital-empty">
            <div className="empty-symbol"><SearchX size={18} /></div>
            <strong>NO HOSPITALS MATCH</strong>
            <span>Adjust the search or security filters.</span>
          </div>
        ) : (
          <div className="hospital-node-grid">
            {filteredHospitals.map((hospital) => {
              const status = String(
                hospital.status || 'UNKNOWN',
              ).toUpperCase()

              const security = String(
                hospital.security_status || 'UNKNOWN',
              ).toUpperCase()

              const hasIncident = incidentHospitalIds.has(hospital.id)

              const selected =
                selectedHospitalId === hospital.id

              return (
                <button
                  key={hospital.id}
                  type="button"
                  className={`hospital-node-card ${
                    selected ? 'selected' : ''
                  } ${hasIncident ? 'has-incident' : ''}`}
                  onClick={() => {
                    setSelectedHospitalId(hospital.id)
                    setActionError('')
                  }}
                >
                  <div className="hospital-node-glow" />

                  <div className="hospital-node-top">
                    <div className="hospital-code">
                      {hospital.code}
                    </div>

                    <div className="hospital-online">
                      <i />
                      {status === 'ACTIVE'
                        ? 'ONLINE'
                        : statusLabel(status)}
                    </div>
                  </div>

                  <div className="hospital-node-main">
                    <div className="hospital-building">
                      <Building2 size={22} />
                    </div>

                    <div className="hospital-identity">
                      <strong>{hospital.name}</strong>

                      <span>
                        {hospital.location || 'Location not specified'}
                      </span>

                      <small>
                        {hospital.contact_email ||
                          'No contact email'}
                      </small>
                    </div>
                  </div>

                  <div className="hospital-node-bottom">
                    <div className={`state-badge ${status.toLowerCase()}`}>
                      {statusLabel(status)}
                    </div>

                    <div
                      className={`security-badge ${security.toLowerCase()}`}
                    >
                      {statusLabel(security)}
                    </div>

                    <div
                      className={`eligibility-badge ${
                        hospital.is_eligible
                          ? 'eligible'
                          : 'ineligible'
                      }`}
                    >
                      {hospital.is_eligible
                        ? 'ELIGIBLE'
                        : 'INELIGIBLE'}
                    </div>

                    <span className="hospital-open">
                      ?
                    </span>
                  </div>

                  {hasIncident && (
                    <div className="hospital-incident-marker">
                      SECURITY ATTENTION
                    </div>
                  )}
                </button>
              )
            })}
          </div>
        )}
      </section>

      {selectedHospital && (
        <div
          className="hospital-drawer-backdrop"
          onClick={() => setSelectedHospitalId(null)}
          role="presentation"
        >
          <aside
            className="hospital-management-drawer"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="hospital-drawer-header">
              <div>
                <div className="panel-kicker">NODE MANAGEMENT</div>

                <h2>
                  {selectedHospital.code}
                  <span
                    className={`drawer-status-dot ${
                      String(selectedHospital.status).toLowerCase()
                    }`}
                  />
                </h2>

                <p>{selectedHospital.name}</p>
              </div>

              <button
                type="button"
                className="drawer-close"
                aria-label="Close"
                onClick={() => setSelectedHospitalId(null)}
              >
                ?
              </button>
            </div>

            <div className="drawer-tabs">
              <span className="active">OVERVIEW</span>
              <span>SECURITY</span>
              <span>ROUNDS</span>
              <span>INCIDENTS</span>
            </div>

            <div className="hospital-drawer-body">
              <div className="drawer-visual">
                <div className="drawer-building">
                  ?
                </div>

                <div>
                  <span>HOSPITAL CODE</span>
                  <strong>{selectedHospital.code}</strong>

                  <span>HOSPITAL NAME</span>
                  <strong>{selectedHospital.name}</strong>

                  <span>LOCATION</span>
                  <strong>
                    {selectedHospital.location || 'Not specified'}
                  </strong>

                  <span>CONTACT EMAIL</span>
                  <strong>
                    {selectedHospital.contact_email || 'Not provided'}
                  </strong>

                  <span>CONTACT PHONE</span>
                  <strong>
                    {selectedHospital.contact_phone || 'Not provided'}
                  </strong>

                  <span>CREATED</span>
                  <strong>
                    {selectedHospital.created_at
                      ? new Date(
                          selectedHospital.created_at,
                        ).toLocaleDateString()
                      : '?'}
                  </strong>
                </div>
              </div>

              <div className="drawer-state-grid">
                <div>
                  <span>STATUS</span>
                  <strong>
                    {statusLabel(selectedHospital.status)}
                  </strong>
                </div>

                <div>
                  <span>SECURITY POSTURE</span>
                  <strong>
                    {statusLabel(
                      selectedHospital.security_status,
                    )}
                  </strong>
                </div>

                <div>
                  <span>ELIGIBILITY</span>
                  <strong>
                    {selectedHospital.is_eligible
                      ? 'ELIGIBLE'
                      : 'INELIGIBLE'}
                  </strong>
                </div>

                <div>
                  <span>SECURITY RECORDS</span>
                  <strong>
                    {
                      incidents.filter(
                        (incident) =>
                          incident.hospital_id ===
                          selectedHospital.id,
                      ).length
                    }
                  </strong>
                </div>
              </div>

              <section className="drawer-action-section">
                <div className="drawer-section-title">
                  LIFECYCLE CONTROL
                </div>

                <div className="drawer-actions">
                  {String(selectedHospital.status).toUpperCase() ===
                    'PENDING' && (
                    <button
                      type="button"
                      className="drawer-action approve"
                      disabled={actionLoading}
                      onClick={() => performAction('approve')}
                    >
                      <strong>? APPROVE</strong>
                      <small>Enable participation</small>
                    </button>
                  )}

                  {String(selectedHospital.status).toUpperCase() ===
                    'ACTIVE' && (
                    <>
                      <button
                        type="button"
                        className="drawer-action suspend"
                        disabled={actionLoading}
                        onClick={() => performAction('suspend')}
                      >
                        <strong>? SUSPEND</strong>
                        <small>Temporarily disable</small>
                      </button>

                      <button
                        type="button"
                        className="drawer-action quarantine"
                        disabled={actionLoading}
                        onClick={() => performAction('quarantine')}
                      >
                        <strong>? QUARANTINE</strong>
                        <small>Isolate from federation</small>
                      </button>
                    </>
                  )}

                  {String(selectedHospital.status).toUpperCase() ===
                    'SUSPENDED' && (
                    <button
                      type="button"
                      className="drawer-action restore"
                      disabled={actionLoading}
                      onClick={() => performAction('restore')}
                    >
                      <strong>? RESTORE</strong>
                      <small>Reinstate access</small>
                    </button>
                  )}

                  {String(selectedHospital.status).toUpperCase() ===
                    'QUARANTINED' && (
                    <button
                      type="button"
                      className="drawer-action restore"
                      disabled={actionLoading}
                      onClick={() => performAction('release')}
                    >
                      <strong>? RELEASE</strong>
                      <small>Release quarantine</small>
                    </button>
                  )}

                  {!['REVOKED', 'INACTIVE'].includes(
                    String(selectedHospital.status).toUpperCase(),
                  ) && (
                    <button
                      type="button"
                      className="drawer-action revoke"
                      disabled={actionLoading}
                      onClick={() => performAction('revoke')}
                    >
                      <strong>? REVOKE</strong>
                      <small>Remove access permanently</small>
                    </button>
                  )}
                </div>

                {actionLoading && (
                  <div className="drawer-action-loading">
                    APPLYING LIFECYCLE CHANGE...
                  </div>
                )}

                {actionError && (
                  <div className="drawer-action-error">
                    {actionError}
                  </div>
                )}

                <div className="drawer-security-note">
                  <span className="preview-mark">?</span>
                  <small>
                    Lifecycle actions are audited and do not bypass
                    the federated security pipeline.
                  </small>
                </div>
              </section>
            </div>
          </aside>
        </div>
      )}
    </div>
  )
}


function SyntheticDataPage({ data }) {
  const hospitals = Array.isArray(data?.hospitals)
    ? data.hospitals
    : []

  const rounds = Array.isArray(data?.rounds)
    ? data.rounds
    : []

  const latestRound = rounds[0]

  const activeCount = hospitals.filter(
    (hospital) =>
      String(hospital.status || '').toUpperCase() === 'ACTIVE',
  ).length

  const simulatedClients = 20

  return (
    <div className="synthetic-page">

      <header className="synthetic-hero">
        <div>
          <div className="eyebrow">
            FEDERATION / SIMULATION LAB
          </div>

          <h1>Synthetic Data</h1>

          <p>
            Controlled synthetic environment for reproducing
            federated-learning conditions without exposing
            hospital-local datasets.
          </p>
        </div>

        <div className="synthetic-status">
          <span className="pulse" />

          <div>
            <strong>SIMULATION BASELINE</strong>
            <small>FEDERATION DATA ENVIRONMENT</small>
          </div>
        </div>
      </header>


      <section className="synthetic-metrics">

        <div className="synthetic-metric">
          <span>SIMULATED CLIENTS</span>
          <strong>20</strong>
          <small>Federation baseline</small>
        </div>

        <div className="synthetic-metric">
          <span>DATASET</span>
          <strong>MNIST</strong>
          <small>10 classes</small>
        </div>

        <div className="synthetic-metric">
          <span>MODEL PARAMETERS</span>
          <strong>105,866</strong>
          <small>FedSentinel CNN</small>
        </div>

        <div className="synthetic-metric">
          <span>NON-IID CONCENTRATION</span>
          <strong>ALPHA 0.5</strong>
          <small>Dirichlet partition</small>
        </div>

      </section>


      <section className="synthetic-main-grid">

        <section className="panel synthetic-pipeline-panel">

          <div className="panel-heading">
            <div>
              <div className="panel-kicker">
                SYNTHETIC FEDERATION PIPELINE
              </div>

              <h2>Data becomes federated updates</h2>
            </div>

            <span className="synthetic-tag">
              SIMULATION
            </span>
          </div>


          <div className="synthetic-flow">

            <div className="synthetic-flow-node active">
              <Database size={17} />
              <strong>MNIST</strong>
              <small>BASE DATASET</small>
            </div>

            <div className="synthetic-flow-line" />

            <div className="synthetic-flow-node">
              <GitBranch size={17} />
              <strong>NON-IID PARTITION</strong>
              <small>DIRICHLET ALPHA = 0.5</small>
            </div>

            <div className="synthetic-flow-line" />

            <div className="synthetic-flow-node">
              <Building2 size={17} />
              <strong>CLIENT SHARDS</strong>
              <small>20 SIMULATED CLIENTS</small>
            </div>

            <div className="synthetic-flow-line" />

            <div className="synthetic-flow-node">
              <Workflow size={17} />
              <strong>LOCAL TRAINING</strong>
              <small>MODEL UPDATE</small>
            </div>

            <div className="synthetic-flow-line" />

            <div className="synthetic-flow-node security">
              <ShieldCheck size={17} />
              <strong>SECURITY PIPELINE</strong>
              <small>VERIFY ? INSPECT ? CORRELATE</small>
            </div>

          </div>


          <div className="synthetic-explanation">
            <Activity size={16} />

            <div>
              <strong>
                Synthetic data is a controlled simulation input ? not hospital data.
              </strong>

              <p>
                The simulation layer creates controlled client
                conditions and produces model updates. Security
                analysis evaluates the resulting updates independently.
              </p>
            </div>
          </div>

        </section>


        <section className="panel synthetic-model-panel">

          <div className="panel-heading">

            <div>
              <div className="panel-kicker">
                SHARED MODEL
              </div>

              <h2>FedSentinel CNN</h2>
            </div>

            <span className="model-param-count">
              105,866
            </span>

          </div>


          <div className="synthetic-network">

            <div className="network-layer input">
              <span>INPUT</span>
              <strong>28 &times; 28</strong>
              <small>GRAYSCALE IMAGE</small>
            </div>

            <div className="network-connector" />

            <div className="network-layer">
              <span>CONV1</span>
              <strong>1 &rarr; 16</strong>
              <small>FEATURE EXTRACTION</small>
            </div>

            <div className="network-connector" />

            <div className="network-layer">
              <span>CONV2</span>
              <strong>16 &rarr; 32</strong>
              <small>FEATURE EXTRACTION</small>
            </div>

            <div className="network-connector" />

            <div className="network-layer">
              <span>FLATTEN</span>
              <strong>1568</strong>
              <small>FEATURE VECTOR</small>
            </div>

            <div className="network-connector" />

            <div className="network-layer">
              <span>FC1</span>
              <strong>1568 &rarr; 64</strong>
              <small>REPRESENTATION</small>
            </div>

            <div className="network-connector" />

            <div className="network-layer output">
              <span>OUTPUT</span>
              <strong>64 &rarr; 10</strong>
              <small>CLASSIFICATION</small>
            </div>

          </div>

        </section>

      </section>


      <section className="panel synthetic-shards-panel">

        <div className="panel-heading">

          <div>
            <div className="panel-kicker">
              FEDERATION SHARD MAP
            </div>

            <h2>Simulated client population</h2>
          </div>

          <span className="synthetic-count">
            {activeCount} ACTIVE HOSPITALS
          </span>

        </div>


        <div className="synthetic-client-grid">

          {Array.from(
            { length: simulatedClients },
            (_, index) => {

              const hospital =
                hospitals[index % Math.max(hospitals.length, 1)]

              const code =
                hospital?.code ||
                `H${String(index + 1).padStart(2, '0')}`

              const isActive =
                String(hospital?.status || '').toUpperCase() ===
                'ACTIVE'

              return (
                <div
                  className={`synthetic-client ${
                    isActive ? 'active' : ''
                  }`}
                  key={index}
                >
                  <div className="synthetic-client-head">
                    <span className="synthetic-client-dot" />
                    <strong>{code}</strong>
                  </div>

                  <div className="synthetic-client-bars">
                    <i />
                    <i />
                    <i />
                    <i />
                  </div>

                  <small>
                    {isActive ? 'AVAILABLE' : 'SIMULATED'}
                  </small>
                </div>
              )
            },
          )}

        </div>


        <div className="synthetic-shard-note">
          <Database size={15} />

          <span>
            Client shards represent the non-IID distribution used
            by the simulation engine. They do not represent copies
            of private hospital datasets.
          </span>
        </div>

      </section>


      <section className="panel synthetic-boundary-panel">

        <div className="panel-heading">

          <div>
            <div className="panel-kicker">
              DATA BOUNDARY
            </div>

            <h2>
              Simulation and hospital data remain separate
            </h2>
          </div>

        </div>


        <div className="synthetic-boundary">

          <div className="boundary-side simulation">

            <div className="boundary-label">
              SIMULATION ENVIRONMENT
            </div>

            <div className="boundary-item">
              <Database size={14} />
              <span>MNIST simulation input</span>
            </div>

            <div className="boundary-item">
              <GitBranch size={14} />
              <span>Non-IID client partition</span>
            </div>

            <div className="boundary-item">
              <Workflow size={14} />
              <span>Local training simulation</span>
            </div>

            <div className="boundary-item">
              <ShieldCheck size={14} />
              <span>Generated model updates</span>
            </div>

          </div>


          <div className="boundary-arrow">
            <span className="boundary-arrow-label">MODEL UPDATE</span>
            <span className="boundary-arrow-line">?</span>
          </div>


          <div className="boundary-side hospital">

            <div className="boundary-label">
              HOSPITAL ENVIRONMENT
            </div>

            <div className="boundary-item">
              <Building2 size={14} />
              <span>Private hospital dataset</span>
            </div>

            <div className="boundary-item">
              <Database size={14} />
              <span>Private samples</span>
            </div>

            <div className="boundary-item">
              <Workflow size={14} />
              <span>Local model state</span>
            </div>

            <div className="boundary-item">
              <ShieldCheck size={14} />
              <span>Only model updates cross boundary</span>
            </div>

          </div>

        </div>


        <div className="synthetic-principle">

          <strong>DATASET &ne; MODEL UPDATE</strong>

          <span>
            The security control plane analyzes model updates,
            not hospital raw data.
          </span>

        </div>

      </section>


      <section className="synthetic-context">

        <div>
          <span>LAST FEDERATION ROUND</span>
          <strong>
            {latestRound
              ? `R-${latestRound.round_number}`
              : 'NO ROUND'}
          </strong>
        </div>

        <div>
          <span>ROUND STATUS</span>
          <strong>
            {latestRound?.status || 'STANDBY'}
          </strong>
        </div>

        <div>
          <span>ACTIVE HOSPITALS</span>
          <strong>{activeCount}</strong>
        </div>

        <div>
          <span>SIMULATION CLIENT BASELINE</span>
          <strong>{simulatedClients}</strong>
        </div>

      </section>

    </div>
  )
}


function RoundConfigurationPage({ data, token, onDataRefresh, onNavigate }) {
  const hospitals = Array.isArray(data?.hospitals) ? data.hospitals : []
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []

  const latestRound = rounds[0] || null

  const runningRound = useMemo(() => {
    return rounds.find(
      (round) => String(round?.status || '').toUpperCase() === 'RUNNING',
    ) || null
  }, [rounds])

  const sortedHospitals = useMemo(() => {
    return [...hospitals].sort((a, b) => {
      const codeA = a.code || a.hospital_code || ''
      const codeB = b.code || b.hospital_code || ''
      return codeA.localeCompare(codeB, undefined, { numeric: true })
    })
  }, [hospitals])

  const eligibleHospitals = useMemo(() => {
    return sortedHospitals.filter(
      (hospital) =>
        String(hospital?.status || '').toUpperCase() === 'ACTIVE' &&
        hospital?.is_eligible !== false,
    )
  }, [sortedHospitals])

  const [config, setConfig] = useState({
    execution_mode: 'SIMULATION',
    num_clients: 20,
    seed: 42,
    concentration: 0.5,
    local_epochs: 1,
    batch_size: 32,
    learning_rate: 0.001,
    validation_sample_size: 1000,
    validation_batch_size: 64,
    device: 'cpu',
    inject_attack: true,
    attack_scale: 25,
  })

  const [creating, setCreating] = useState(false)
  const [startingId, setStartingId] = useState('')
  const [cancellingId, setCancellingId] = useState('')
  const [actionError, setActionError] = useState('')
  const [actionMessage, setActionMessage] = useState('')

  useEffect(() => {
    const saved =
      latestRound?.status === 'CREATED'
        ? latestRound?.configuration
        : null

    if (!saved) return

    setConfig((current) => ({
      ...current,
      execution_mode: saved.execution_mode || current.execution_mode,
      num_clients: Number(saved.num_clients ?? current.num_clients),
      seed: Number(saved.seed ?? current.seed),
      concentration: Number(
        saved.concentration ?? current.concentration,
      ),
      local_epochs: Number(
        saved.local_epochs ?? current.local_epochs,
      ),
      batch_size: Number(
        saved.batch_size ?? current.batch_size,
      ),
      learning_rate: Number(
        saved.learning_rate ?? current.learning_rate,
      ),
      validation_sample_size: Number(
        saved.validation_sample_size ??
          current.validation_sample_size,
      ),
      validation_batch_size: Number(
        saved.validation_batch_size ??
          current.validation_batch_size,
      ),
      device: saved.device || current.device,
      inject_attack:
        typeof saved.inject_attack === 'boolean'
          ? saved.inject_attack
          : current.inject_attack,
      attack_scale: Number(
        saved.attack_scale ?? current.attack_scale,
      ),
    }))
  }, [latestRound?.id])

  const simulationMode = config.execution_mode === 'SIMULATION'

  const participantCapacity = simulationMode
    ? 20
    : Math.max(2, eligibleHospitals.length)

  const setField = (name, value) => {
    setConfig((current) => {
      const next = {
        ...current,
        [name]: value,
      }

      if (
        name === 'execution_mode' &&
        value === 'HOSPITAL'
      ) {
        next.inject_attack = false
        next.attack_scale = 0

        const hospitalCapacity = Math.max(
          2,
          eligibleHospitals.length,
        )

        next.num_clients = Math.max(
          2,
          Math.min(Number(next.num_clients) || 2, hospitalCapacity),
        )
      }

      if (
        name === 'execution_mode' &&
        value === 'SIMULATION'
      ) {
        next.inject_attack =
          typeof next.inject_attack === 'boolean'
            ? next.inject_attack
            : true

        next.num_clients = Math.max(
          2,
          Math.min(Number(next.num_clients) || 2, 20),
        )
      }

      return next
    })

    setActionError('')
    setActionMessage('')
  }

  const participantsReady =
    Number(config.num_clients) >= 2 &&
    Number(config.num_clients) <= participantCapacity

  const configurationValid =
    Number(config.num_clients) >= 2 &&
    Number(config.seed) >= 0 &&
    Number(config.concentration) > 0 &&
    Number(config.local_epochs) >= 1 &&
    Number(config.batch_size) >= 1 &&
    Number(config.learning_rate) > 0 &&
    Number(config.validation_sample_size) >= 1 &&
    Number(config.validation_batch_size) >= 1 &&
    Number(config.attack_scale) >= 0 &&
    participantsReady

  async function createRound() {
    setActionError('')
    setActionMessage('')

    if (runningRound) {
      setActionError(
        `Round R-${runningRound.round_number} is currently RUNNING. Complete or cancel it first.`
      )
      return
    }

    if (!configurationValid) {
      setActionError(
        simulationMode
          ? 'Configuration is invalid (requires 2-20 clients).'
          : `Only ${eligibleHospitals.length} eligible active hospital(s) are available (minimum 2).`,
      )
      return
    }

    setCreating(true)

    try {
      const created = await apiFetch(
        `/api/v1/federations/${FEDERATION_ID}/rounds`,
        token,
        {
          method: 'POST',
          body: JSON.stringify({
            configuration: {
              ...config,
              num_clients: Number(config.num_clients),
              seed: Number(config.seed),
              concentration: Number(config.concentration),
              local_epochs: Number(config.local_epochs),
              batch_size: Number(config.batch_size),
              learning_rate: Number(config.learning_rate),
              validation_sample_size: Number(
                config.validation_sample_size,
              ),
              validation_batch_size: Number(
                config.validation_batch_size,
              ),
              attack_scale: Number(config.attack_scale),
            },
          }),
        },
      )

      setActionMessage(
        `ROUND R-${created?.round_number || '?'} CREATED`,
      )

      onDataRefresh?.()
    } catch (error) {
      setActionError(error.message || 'Unable to create round')
    } finally {
      setCreating(false)
    }
  }

  async function startRound(round) {
    if (!round?.id || round.status !== 'CREATED') return

    if (runningRound) {
      setActionError(
        `Cannot start: Round R-${runningRound.round_number} is currently RUNNING.`
      )
      return
    }

    setActionError('')
    setActionMessage('')
    setStartingId(round.id)

    try {
      await apiFetch(
        `/api/v1/federations/${FEDERATION_ID}/rounds/${round.id}/start`,
        token,
        {
          method: 'POST',
        },
      )

      setActionMessage(
        `ROUND R-${round.round_number} STARTED`,
      )

      onDataRefresh?.()
    } catch (error) {
      setActionError(error.message || 'Unable to start round')
    } finally {
      setStartingId('')
    }
  }

  async function cancelRound(round) {
    if (!round?.id) return

    setActionError('')
    setActionMessage('')
    setCancellingId(round.id)

    try {
      await apiFetch(
        `/api/v1/federations/${FEDERATION_ID}/rounds/${round.id}/cancel`,
        token,
        {
          method: 'POST',
          body: JSON.stringify({
            reason: 'Cancelled by operator via round control',
          }),
        },
      )

      setActionMessage(
        `ROUND R-${round.round_number} CANCELLED`,
      )

      onDataRefresh?.()
    } catch (error) {
      setActionError(error.message || 'Unable to cancel round')
    } finally {
      setCancellingId('')
    }
  }

  const visibleRounds = rounds.slice(0, 8)

  return (
    <div className="round-config-page">

      <header className="round-config-hero">
        <div>
          <div className="eyebrow">
            SECURITY / ROUND CONTROL
          </div>

          <h1>Round Configuration</h1>

          <p>
            Define a reproducible federation execution before
            model updates enter the security control plane.
          </p>
        </div>

        <div className="round-config-state">
          <span className={`round-state-dot ${runningRound ? 'running' : configurationValid ? 'ready' : 'review'}`} />
          <div>
            <small>CONTROL STATE</small>
            <strong>
              {runningRound ? `RUNNING (R-${runningRound.round_number})` : configurationValid ? 'READY' : 'REVIEW'}
            </strong>
          </div>
        </div>
      </header>

      {runningRound && (
        <div className="active-round-banner">
          <AlertTriangle size={16} />
          <div>
            <strong>ACTIVE EXECUTION IN PROGRESS</strong>
            <span>
              Round R-{runningRound.round_number} ({runningRound.configuration?.execution_mode || 'HOSPITAL'} mode)
              is currently RUNNING. Only one round may run concurrently. Complete or cancel it before starting another.
            </span>
          </div>
          <button
            type="button"
            className="banner-action-button"
            onClick={() => onNavigate?.('live-round')}
          >
            VIEW LIVE ROUND &rarr;
          </button>
        </div>
      )}

      <section className="round-mode-panel">

        <div className="round-section-heading">
          <div>
            <span className="panel-kicker">
              EXECUTION MODE
            </span>
            <h2>Choose federation runtime</h2>
          </div>

          <span className="round-mode-code">
            {config.execution_mode}
          </span>
        </div>

        <div className="round-mode-grid">

          <button
            type="button"
            className={`round-mode-card ${
              simulationMode ? 'selected' : ''
            }`}
            onClick={() =>
              setField('execution_mode', 'SIMULATION')
            }
          >
            <div className="round-mode-icon">
              <Radar size={20} strokeWidth={1.4} />
            </div>

            <div>
              <span>CONTROLLED LAB</span>
              <strong>SIMULATION</strong>
              <small>
                Run reproducible federated-learning experiments
                using synthetic clients and controlled security tests.
              </small>
            </div>

            <i>
              {simulationMode ? 'SELECTED' : 'CHOOSE'}
            </i>
          </button>

          <button
            type="button"
            className={`round-mode-card ${
              !simulationMode ? 'selected' : ''
            }`}
            onClick={() =>
              setField('execution_mode', 'HOSPITAL')
            }
          >
            <div className="round-mode-icon">
              <Hospital size={20} strokeWidth={1.4} />
            </div>

            <div>
              <span>PRODUCTION PATH</span>
              <strong>HOSPITAL</strong>
              <small>
                Run a federation round with registered hospitals
                that are currently eligible to participate.
              </small>
            </div>

            <i>
              {!simulationMode ? 'SELECTED' : 'CHOOSE'}
            </i>
          </button>

        </div>

        <div className="round-mode-explanation">
          <div className="round-mode-explanation-icon">
            {config.execution_mode === 'HOSPITAL'
              ? <Hospital size={15} strokeWidth={1.6} />
              : <Radar size={15} strokeWidth={1.6} />}
          </div>

          <div>
            <strong>
              {config.execution_mode === 'HOSPITAL'
                ? 'PRODUCTION PATH - HOSPITAL FEDERATION'
                : 'CONTROLLED LAB - SIMULATION ENVIRONMENT'}
            </strong>

            <p>
              {config.execution_mode === 'HOSPITAL'
                ? <>
                    Participating hospitals train locally and submit model updates through the federation workflow.
                    <b> Raw hospital datasets remain inside each hospital environment.</b>
                    Attack injection is locked.
                  </>
                : <>
                    Synthetic federation used for reproducible experiments, non-IID data generation,
                    security evaluation and controlled attack scenarios.
                  </>}
            </p>
          </div>
        </div>

      </section>

      <div className="round-config-grid">

        <section className="round-config-panel federation-panel">

          <div className="round-section-heading">
            <div>
              <span className="panel-kicker">
                FEDERATION PARAMETERS
              </span>
              <h2>Participant topology</h2>
            </div>

            <Users size={18} strokeWidth={1.4} />
          </div>

          <div className="round-field">

            <div className="round-field-top">
              <label>
                {simulationMode
                  ? 'CLIENT COUNT (SIMULATED)'
                  : 'CLIENT COUNT (HOSPITAL NODES)'}
              </label>
              <strong>{config.num_clients} SELECTED</strong>
            </div>

            <input
              type="range"
              min="2"
              max={participantCapacity}
              step="1"
              value={Math.max(
                2,
                Math.min(
                  Number(config.num_clients) || 2,
                  participantCapacity,
                ),
              )}
              onChange={(event) =>
                setField(
                  'num_clients',
                  Number(event.target.value),
                )
              }
            />

            <div className="round-range-meta">
              <span>MIN 2 CLIENTS</span>
              <span>
                CAPACITY: {participantCapacity} AVAILABLE
              </span>
            </div>

            <div className="client-presets-row">
              <span className="preset-label">PRESETS:</span>
              {[2, 5, 10, participantCapacity]
                .filter((v, i, arr) => arr.indexOf(v) === i && v <= participantCapacity && v >= 2)
                .map((val) => (
                  <button
                    key={val}
                    type="button"
                    className={`preset-btn ${Number(config.num_clients) === val ? 'active' : ''}`}
                    onClick={() => setField('num_clients', val)}
                  >
                    {val === participantCapacity ? `ALL (${val})` : `${val} NODES`}
                  </button>
                ))}
            </div>

            <div className="client-count-control">
              <span>SET PARTICIPANTS</span>
              <input
                type="number"
                min="2"
                max={participantCapacity}
                step="1"
                value={config.num_clients}
                onChange={(event) => {
                  const raw = Number(event.target.value)
                  if (!Number.isFinite(raw)) return
                  setField(
                    'num_clients',
                    Math.max(2, Math.min(Math.trunc(raw), participantCapacity)),
                  )
                }}
                aria-label={
                  simulationMode
                    ? 'Number of simulated clients'
                    : 'Number of hospital participants'
                }
              />
              <small>
                {simulationMode
                  ? 'Choose 2-20 synthetic clients'
                  : `${eligibleHospitals.length} eligible hospital node${
                      eligibleHospitals.length === 1 ? '' : 's'
                    } ready for federation`}
              </small>
            </div>

          </div>

          <div className="round-input-row">

            <label>
              <span>RANDOM SEED</span>
              <input
                type="number"
                min="0"
                value={config.seed}
                onChange={(event) =>
                  setField(
                    'seed',
                    Number(event.target.value),
                  )
                }
              />
            </label>

            <label>
              <span>DIRICHLET ALPHA</span>
              <input
                type="number"
                min="0.01"
                step="0.05"
                value={config.concentration}
                onChange={(event) =>
                  setField(
                    'concentration',
                    Number(event.target.value),
                  )
                }
              />
            </label>

          </div>

          <div className="alpha-visual">

            <div className="alpha-axis">
              <span>IID</span>

              <div className="alpha-track">
                <span
                  style={{
                    width: `${Math.min(
                      100,
                      Math.max(
                        4,
                        Number(config.concentration) * 25,
                      ),
                    )}%`,
                  }}
                />
              </div>

              <span>HIGH SKEW</span>
            </div>

            <small>
              Lower alpha produces stronger non-IID client
              distribution.
            </small>

          </div>

        </section>

        <section className="round-config-panel training-panel">

          <div className="round-section-heading">
            <div>
              <span className="panel-kicker">
                LOCAL TRAINING
              </span>
              <h2>Optimization controls</h2>
            </div>

            <Settings size={18} strokeWidth={1.4} />
          </div>

          <div className="round-input-grid">

            <label>
              <span>LOCAL EPOCHS</span>
              <input
                type="number"
                min="1"
                value={config.local_epochs}
                onChange={(event) =>
                  setField(
                    'local_epochs',
                    Number(event.target.value),
                  )
                }
              />
            </label>

            <label>
              <span>BATCH SIZE</span>
              <input
                type="number"
                min="1"
                value={config.batch_size}
                onChange={(event) =>
                  setField(
                    'batch_size',
                    Number(event.target.value),
                  )
                }
              />
            </label>

            <label>
              <span>LEARNING RATE</span>
              <input
                type="number"
                min="0.000001"
                step="0.0001"
                value={config.learning_rate}
                onChange={(event) =>
                  setField(
                    'learning_rate',
                    Number(event.target.value),
                  )
                }
              />
            </label>

            <label>
              <span>DEVICE</span>

              <select
                value={config.device}
                onChange={(event) =>
                  setField(
                    'device',
                    event.target.value,
                  )
                }
              >
                <option value="cpu">CPU</option>
                <option value="cuda">CUDA</option>
              </select>

            </label>

          </div>

          <div className="round-validation-strip">

            <div>
              <span>VALIDATION SAMPLE</span>
              <strong>
                {config.validation_sample_size}
              </strong>
            </div>

            <div>
              <span>VALIDATION BATCH</span>
              <strong>
                {config.validation_batch_size}
              </strong>
            </div>

          </div>

          <div className="round-input-row">

            <label>
              <span>VALIDATION SAMPLE SIZE</span>
              <input
                type="number"
                min="1"
                value={config.validation_sample_size}
                onChange={(event) =>
                  setField(
                    'validation_sample_size',
                    Number(event.target.value),
                  )
                }
              />
            </label>

            <label>
              <span>VALIDATION BATCH SIZE</span>
              <input
                type="number"
                min="1"
                value={config.validation_batch_size}
                onChange={(event) =>
                  setField(
                    'validation_batch_size',
                    Number(event.target.value),
                  )
                }
              />
            </label>

          </div>

        </section>

      </div>

      <section className="round-security-panel">

        <div className="round-section-heading">
          <div>
            <span className="panel-kicker">
              SECURITY EXPERIMENT
            </span>
            <h2>Adversarial simulation controls</h2>
          </div>

          <ShieldCheck size={19} strokeWidth={1.4} />
        </div>

        <div className="round-security-layout">

          <div className="attack-toggle-card">

            <div className="attack-toggle-copy">
              <span>ATTACK INJECTION</span>
              <strong>
                {!simulationMode
                  ? 'LOCKED (HOSPITAL MODE)'
                  : config.inject_attack
                    ? 'ENABLED'
                    : 'DISABLED'}
              </strong>

              <small>
                {simulationMode
                  ? 'Controlled attack injection enabled for laboratory evaluations.'
                  : 'Attack injection is strictly locked for production hospital execution.'}
              </small>
            </div>

            <button
              type="button"
              className={`binary-toggle ${
                config.inject_attack && simulationMode ? 'on' : ''
              }`}
              disabled={!simulationMode}
              onClick={() =>
                setField(
                  'inject_attack',
                  !config.inject_attack,
                )
              }
              aria-label="Toggle attack injection"
            >
              <span />
            </button>

          </div>

          <div className={`attack-scale-card ${!simulationMode ? 'disabled' : ''}`}>

            <div className="round-field-top">
              <label>ATTACK SCALE</label>
              <strong>
                {!simulationMode
                  ? '0.0 (LOCKED)'
                  : Number(config.attack_scale).toFixed(1)}
              </strong>
            </div>

            <input
              type="range"
              min="0"
              max="50"
              step="0.5"
              disabled={
                !simulationMode ||
                !config.inject_attack
              }
              value={config.attack_scale}
              onChange={(event) =>
                setField(
                  'attack_scale',
                  Number(event.target.value),
                )
              }
            />

            <div className="round-range-meta">
              <span>0</span>
              <span>{simulationMode ? 'SIMULATION ONLY' : 'DISABLED IN HOSPITAL MODE'}</span>
              <span>50</span>
            </div>

          </div>

        </div>

      </section>

      <section className="round-readiness-panel">

        <div className="round-section-heading">
          <div>
            <span className="panel-kicker">
              PARTICIPANT READINESS
            </span>
            <h2>
              {simulationMode
                ? 'Synthetic client pool (Click node to set count)'
                : 'Hospital participant nodes (Click eligible node to set count)'}
            </h2>
          </div>

          <div className="readiness-summary">
            <strong>{config.num_clients} / {participantCapacity}</strong>
            <span>SELECTED / AVAILABLE</span>
          </div>
        </div>

        <div className="participant-visual">

          {simulationMode
            ? Array.from({ length: 20 }, (_, index) => {
                const isSelected = index < config.num_clients
                return (
                  <div
                    className={`participant-node ${
                      isSelected ? 'selected' : 'standby'
                    }`}
                    key={`sim-${index}`}
                    onClick={() => setField('num_clients', Math.max(2, index + 1))}
                    title={`Click to set client count to ${index + 1}`}
                    style={{ cursor: 'pointer' }}
                  >
                    <span className="participant-node-id">
                      H{String(index + 1).padStart(2, '0')}
                    </span>

                    <div className="participant-signal">
                      <i />
                      <i />
                      <i />
                      <i />
                    </div>

                    <small>
                      {isSelected ? 'SELECTED' : 'STANDBY'}
                    </small>
                  </div>
                )
              })
            : sortedHospitals.map((hospital) => {
                const isEligible =
                  String(hospital?.status || '').toUpperCase() === 'ACTIVE' &&
                  hospital?.is_eligible !== false

                const eligibleIndex = isEligible
                  ? eligibleHospitals.indexOf(hospital)
                  : -1

                const isSelected = isEligible && eligibleIndex < config.num_clients

                let statusBadge = 'INELIGIBLE'
                let nodeClass = 'ineligible'

                if (isEligible) {
                  if (isSelected) {
                    statusBadge = 'SELECTED'
                    nodeClass = 'selected'
                  } else {
                    statusBadge = 'ELIGIBLE'
                    nodeClass = 'eligible'
                  }
                }

                return (
                  <div
                    className={`participant-node ${nodeClass}`}
                    key={hospital.id}
                    onClick={() => {
                      if (isEligible && eligibleIndex >= 0) {
                        setField('num_clients', Math.max(2, eligibleIndex + 1))
                      }
                    }}
                    title={
                      isEligible
                        ? `Click to select ${eligibleIndex + 1} participant node(s)`
                        : `${hospital.code || 'Node'} is ${hospital.status || 'INELIGIBLE'}`
                    }
                    style={{ cursor: isEligible ? 'pointer' : 'not-allowed' }}
                  >
                    <span className="participant-node-id">
                      {hospital.code ||
                        hospital.hospital_code ||
                        'NODE'}
                    </span>

                    <div className="participant-signal">
                      <i />
                      <i />
                      <i />
                      <i />
                    </div>

                    <small>
                      {statusBadge}
                    </small>
                  </div>
                )
              })}
        </div>

        <div
          className={`readiness-footer ${
            participantsReady ? 'ready' : 'blocked'
          }`}
        >
          <div>
            <span>REQUIRED</span>
            <strong>{config.num_clients}</strong>
          </div>

          <div>
            <span>AVAILABLE</span>
            <strong>{participantCapacity}</strong>
          </div>

          <div>
            <span>STATE</span>
            <strong>
              {participantsReady ? 'READY' : 'INSUFFICIENT'}
            </strong>
          </div>
        </div>

      </section>

      <section className="round-action-panel">

        <div className="round-preview">

          <div className="round-preview-heading">
            <span className="panel-kicker">
              EXECUTION PIPELINE
            </span>
            <h3>Configuration summary</h3>
          </div>

          <div className="round-preview-flow">

            <div>
              <strong>{config.execution_mode}</strong>
              <small>RUNTIME</small>
            </div>

            <span className="preview-mark">&rarr;</span>

            <div>
              <strong>{config.num_clients}</strong>
              <small>CLIENTS</small>
            </div>

            <span className="preview-mark">&rarr;</span>

            <div>
              <strong>{config.local_epochs}</strong>
              <small>EPOCHS</small>
            </div>

            <span className="preview-mark">&rarr;</span>

            <div>
              <strong>L0-L5</strong>
              <small>SECURITY</small>
            </div>

            <span className="preview-mark">&rarr;</span>

            <div>
              <strong>SAFE</strong>
              <small>AGGREGATION</small>
            </div>

          </div>

        </div>

        <button
          type="button"
          className="primary-round-action"
          disabled={creating || !configurationValid || !!runningRound}
          onClick={createRound}
          title={runningRound ? `Round R-${runningRound.round_number} is currently RUNNING` : 'Create round'}
        >
          {creating
            ? 'CREATING ROUND...'
            : runningRound
              ? `RUNNING (R-${runningRound.round_number})`
              : 'CREATE ROUND'}
        </button>

      </section>

      {(actionError || actionMessage) && (
        <section
          className={`round-action-feedback ${
            actionError ? 'error' : 'success'
          }`}
        >
          {actionError ? (
            <AlertTriangle size={15} />
          ) : (
            <ShieldCheck size={15} />
          )}

          <span>
            {actionError || actionMessage}
          </span>
        </section>
      )}

      <section className="round-history-panel">

        <div className="round-section-heading">

          <div>
            <span className="panel-kicker">
              ROUND HISTORY
            </span>
            <h2>Persistent federation rounds</h2>
          </div>

          <span className="round-history-count">
            {rounds.length} TOTAL
          </span>

        </div>

        {visibleRounds.length === 0 ? (
          <div className="round-empty-state">
            <Workflow size={20} strokeWidth={1.2} />
            <span>NO PERSISTED ROUNDS</span>
          </div>
        ) : (
          <div className="round-history-list">

            {visibleRounds.map((round) => {
              const roundConfig = round.configuration || {}
              const isCreated =
                String(round.status).toUpperCase() === 'CREATED'
              const isRunning =
                String(round.status).toUpperCase() === 'RUNNING'
              const isCompleted =
                String(round.status).toUpperCase() === 'COMPLETED'
              const isFailed =
                String(round.status).toUpperCase() === 'FAILED'
              const isCancelled =
                String(round.status).toUpperCase() === 'CANCELLED'

              return (
                <article
                  className="round-history-row"
                  key={round.id}
                >

                  <div className="history-round-number">
                    <span>ROUND</span>
                    <strong>
                      R-{round.round_number}
                    </strong>
                  </div>

                  <div className="history-status">
                    <span
                      className={`status-dot status-${String(
                        round.status || '',
                      ).toLowerCase()}`}
                    />
                    <strong>
                      {round.status || 'UNKNOWN'}
                    </strong>
                  </div>

                  <div className="history-meta">
                    <span>
                      {roundConfig.execution_mode ||
                        'SIMULATION'}
                    </span>

                    <span>
                      {round.participating_clients || 0}
                      {' '}CLIENTS
                    </span>

                    <span>
                      {round.accepted_updates || 0}
                      {' '}ACCEPTED
                    </span>

                    <span>
                      {round.quarantined_updates || 0}
                      {' '}QUARANTINED
                    </span>
                  </div>

                  <div className="history-actions">
                    {isCreated && (
                      <>
                        <button
                          type="button"
                          className="history-start-button"
                          disabled={
                            startingId === round.id || !!runningRound
                          }
                          title={
                            runningRound
                              ? `Round R-${runningRound.round_number} is RUNNING`
                              : 'Start round'
                          }
                          onClick={() =>
                            startRound(round)
                          }
                        >
                          {startingId === round.id
                            ? 'STARTING...'
                            : 'START ROUND'}
                        </button>
                        <button
                          type="button"
                          className="history-cancel-button"
                          disabled={cancellingId === round.id}
                          onClick={() => cancelRound(round)}
                        >
                          {cancellingId === round.id ? '...' : 'CANCEL'}
                        </button>
                      </>
                    )}

                    {isRunning && (
                      <>
                        <button
                          type="button"
                          className="history-live-button"
                          onClick={() => onNavigate?.('live-round')}
                        >
                          VIEW LIVE
                        </button>
                        <button
                          type="button"
                          className="history-cancel-button danger"
                          disabled={cancellingId === round.id}
                          title="Cancel this running round"
                          onClick={() => cancelRound(round)}
                        >
                          {cancellingId === round.id ? '...' : 'CANCEL'}
                        </button>
                      </>
                    )}

                    {isCompleted && (
                      <span className="history-lock status-completed">
                        FINALIZED
                      </span>
                    )}

                    {isFailed && (
                      <span className="history-lock status-failed">
                        FAILED
                      </span>
                    )}

                    {isCancelled && (
                      <span className="history-lock status-cancelled">
                        CANCELLED
                      </span>
                    )}
                  </div>

                </article>
              )
            })}

          </div>
        )}

      </section>

    </div>
  )
}

function LiveRoundPage({ data, token }) {
  const rounds = Array.isArray(data?.rounds) ? data.rounds : []
  const hospitals = Array.isArray(data?.hospitals) ? data.hospitals : []

  const runningRound =
    rounds.find(
      (round) =>
        String(round?.status || '').toUpperCase() === 'RUNNING',
    ) || null

  const [selectedRoundId, setSelectedRoundId] = useState('')

  const activeRound = useMemo(() => {
    if (selectedRoundId) {
      return rounds.find((r) => r.id === selectedRoundId) || null
    }
    return runningRound || rounds[0] || null
  }, [selectedRoundId, runningRound, rounds])

  const latestRound = activeRound

  const [roundState, setRoundState] = useState(null)
  const [updates, setUpdates] = useState([])
  const [incidents, setIncidents] = useState([])
  const [events, setEvents] = useState([])
  const [socketState, setSocketState] = useState('CONNECTING')
  const [lastEventAt, setLastEventAt] = useState(null)
  const [refreshTick, setRefreshTick] = useState(0)
  const [finalizing, setFinalizing] = useState(false)
  const [finalizeError, setFinalizeError] = useState('')
  const [finalizeMessage, setFinalizeMessage] = useState('')

  const eventRef = useRef(null)

  const roundId = latestRound?.id || latestRound?.round_id || null

  useEffect(() => {
    if (!roundId || !token) {
      setRoundState(null)
      setUpdates([])
      setIncidents([])
      setEvents([])
      setSocketState('IDLE')
      return undefined
    }

    let cancelled = false
    let socket = null
    let pollTimer = null
    let reconnectTimer = null

    function normalizeList(value) {
      if (Array.isArray(value)) return value
      if (Array.isArray(value?.value)) return value.value
      if (Array.isArray(value?.events)) return value.events
      return []
    }

    async function loadSnapshot() {
      try {
        const [summary, updateResponse, incidentResponse, eventResponse] =
          await Promise.all([
            apiFetch(
              `/api/v1/security/rounds/${roundId}`,
              token,
            ),
            apiFetch(
              `/api/v1/security/rounds/${roundId}/updates`,
              token,
            ),
            apiFetch(
              `/api/v1/security/rounds/${roundId}/incidents`,
              token,
            ),
            apiFetch(
              `/api/v1/events?round_id=${roundId}`,
              token,
            ),
          ])

        if (cancelled) return

        setRoundState(summary)
        setUpdates(normalizeList(updateResponse))
        setIncidents(normalizeList(incidentResponse))

        const nextEvents = normalizeList(eventResponse)
          .slice()
          .sort(
            (a, b) =>
              new Date(a?.timestamp || 0) -
              new Date(b?.timestamp || 0),
          )

        setEvents(nextEvents)

        if (nextEvents.length) {
          setLastEventAt(
            nextEvents[nextEvents.length - 1]?.timestamp || null,
          )
        }
      } catch {
        if (!cancelled) {
          setSocketState((current) =>
            current === 'CONNECTED' ? current : 'POLLING',
          )
        }
      }
    }

    function mergeEvent(incoming) {
      if (!incoming) return

      const event = incoming.event || incoming.data || incoming

      if (!event.event_id && !event.id && !event.event_type) return

      setEvents((current) => {
        const key =
          event.event_id ||
          event.id ||
          `${event.event_type}-${event.timestamp}-${event.client_id || ''}`

        const exists = current.some(
          (item) =>
            (item.event_id || item.id) === key,
        )

        if (exists) return current

        return [...current, event]
          .sort(
            (a, b) =>
              new Date(a?.timestamp || 0) -
              new Date(b?.timestamp || 0),
          )
          .slice(-80)
      })

      setLastEventAt(event.timestamp || new Date().toISOString())
    }

    async function connectSocket() {
      if (cancelled) return

      try {
        const protocol =
          window.location.protocol === 'https:'
            ? 'wss'
            : 'ws'

        const host =
          window.location.hostname || '127.0.0.1'

        socket = new WebSocket(
          `${protocol}://${host}:8000/ws/events/${roundId}`,
        )

        socket.onopen = () => {
          if (cancelled) return
          setSocketState('CONNECTED')
        }

        socket.onmessage = (message) => {
          if (cancelled) return

          try {
            const payload = JSON.parse(message.data)
            mergeEvent(payload)
          } catch {
            // Ignore malformed websocket frames.
          }
        }

        socket.onerror = () => {
          if (!cancelled) {
            setSocketState('POLLING')
          }
        }

        socket.onclose = () => {
          if (cancelled) return

          setSocketState('POLLING')

          reconnectTimer = window.setTimeout(
            connectSocket,
            3000,
          )
        }
      } catch {
        setSocketState('POLLING')
      }
    }

    loadSnapshot()
    connectSocket()

    pollTimer = window.setInterval(
      loadSnapshot,
      5000,
    )

    return () => {
      cancelled = true

      if (socket) {
        try {
          socket.close()
        } catch {
          // Ignore close errors.
        }
      }

      if (pollTimer) {
        window.clearInterval(pollTimer)
      }

      if (reconnectTimer) {
        window.clearTimeout(reconnectTimer)
      }
    }
  }, [roundId, token, refreshTick])

  async function finalizeRound() {
    if (!roundId || finalizing) return

    const currentStatus = String(
      summary?.status ||
        latestRound?.status ||
        '',
    ).toUpperCase()

    const requiredUpdates = Number(
      summary?.participating_clients ??
        latestRound?.participating_clients ??
        latestRound?.target_clients ??
        0,
    )

    const receivedUpdates = updates.length

    if (currentStatus !== 'RUNNING') {
      setFinalizeError(
        `Round is ${currentStatus || 'NOT RUNNING'} and cannot be finalized.`,
      )
      setFinalizeMessage('')
      return
    }

    if (
      requiredUpdates <= 0 ||
      receivedUpdates < requiredUpdates
    ) {
      setFinalizeError(
        `Waiting for hospital submissions: ${receivedUpdates}/${requiredUpdates} updates received.`,
      )
      setFinalizeMessage('')
      return
    }

    setFinalizing(true)
    setFinalizeError('')
    setFinalizeMessage('')

    try {
      await apiFetch(
        `/api/v1/federations/${FEDERATION_ID}/rounds/${roundId}/finalize`,
        token,
        {
          method: 'POST',
        },
      )

      setFinalizeMessage(
        `ROUND R-${summary?.round_number || latestRound?.round_number || '--'} FINALIZED`,
      )

      setRefreshTick((value) => value + 1)
    } catch (error) {
      setFinalizeError(
        error.message || 'Unable to finalize round',
      )
    } finally {
      setFinalizing(false)
    }
  }

  const summary = roundState || latestRound || {}

  const status = String(
    summary?.status || latestRound?.status || 'UNKNOWN',
  ).toUpperCase()

  const participating = Number(
    summary?.participating_clients ??
      latestRound?.participating_clients ??
      latestRound?.target_clients ??
      0,
  )

  const accepted =
    Number(summary?.accepted_updates ?? 0)

  const quarantined =
    Number(summary?.quarantined_updates ?? 0)

  const totalUpdates =
    Number(summary?.total_updates ?? updates.length ?? 0)

  const incidentCount =
    Number(summary?.incident_count ?? incidents.length ?? 0)

  const eventTypes = useMemo(() => {
    const result = {}

    events.forEach((event) => {
      const client = event?.client_id || 'ROUND'
      result[client] = event
    })

    return result
  }, [events])

  const clientStates = useMemo(() => {
    const byClient = {}

    events.forEach((event) => {
      const clientId = event?.client_id

      if (!clientId) return

      byClient[clientId] = {
        clientId,
        eventType: String(
          event?.event_type || '',
        ).toUpperCase(),
        timestamp: event?.timestamp,
        message: event?.message || '',
      }
    })

    updates.forEach((update) => {
      const clientId =
        update?.hospital_code ||
        update?.hospital_id

      if (!clientId) return

      byClient[clientId] = {
        ...(byClient[clientId] || {}),
        clientId,
        update,
      }
    })

    return Object.values(byClient)
  }, [events, updates])

  const selectedClients = useMemo(() => {
    const eventClients = clientStates
      .map((item) => item.clientId)
      .filter(Boolean)

    const updateClients = updates
      .map(
        (item) =>
          item?.hospital_code ||
          item?.hospital_id,
      )
      .filter(Boolean)

    const telemetryClients = [
      ...eventClients,
      ...updateClients,
    ].filter(
      (client, index, list) =>
        list.indexOf(client) === index,
    )

    if (telemetryClients.length) {
      return telemetryClients
    }

    /*
     * A HOSPITAL round remains RUNNING while the federation waits
     * for real hospital submissions. During that waiting period
     * there may be no events or ModelUpdate rows yet.
     *
     * Use the known hospital registry as the participant display
     * source, limited to the number configured for this round.
     */
    if (
      status === 'RUNNING' &&
      participating > 0 &&
      hospitals.length > 0
    ) {
      return hospitals
        .map(
          (hospital) =>
            hospital?.code ||
            hospital?.id,
        )
        .filter(Boolean)
        .slice(0, participating)
    }

    return []
  }, [
    clientStates,
    updates,
    hospitals,
    participating,
    status,
  ])

  const hospitalLookup = useMemo(() => {
    const map = {}

    hospitals.forEach((hospital) => {
      if (hospital?.id) {
        map[hospital.id] = hospital
      }

      if (hospital?.code) {
        map[hospital.code] = hospital
      }
    })

    return map
  }, [hospitals])

  const stageDefinitions = [
    {
      key: 'L0',
      label: 'VERIFY',
      event: 'INTEGRITY_CHECKED',
      icon: ShieldCheck,
    },
    {
      key: 'L1',
      label: 'INSPECT',
      event: 'FINGERPRINT_GENERATED',
      icon: Search,
    },
    {
      key: 'L2',
      label: 'CORRELATE',
      event: 'ANOMALY_DETECTED',
      icon: GitBranch,
    },
    {
      key: 'L3',
      label: 'INFLUENCE',
      event: 'INFLUENCE_TEST_COMPLETED',
      icon: BarChart3,
    },
    {
      key: 'L4',
      label: 'SIMULATE',
      event: 'COUNTERFACTUAL_TEST_COMPLETED',
      icon: Radar,
    },
    {
      key: 'L5',
      label: 'ATTRIBUTE',
      event: 'ATTRIBUTION_UPDATED',
      icon: Layers3,
    },
  ]

  const completedStages = new Set()

  if (status === 'COMPLETED') {
    stageDefinitions.forEach((item) => completedStages.add(item.key))
  } else {
    events.forEach((event) => {
      const type = String(
        event?.event_type || '',
      ).toUpperCase()

      const stage = stageDefinitions.find(
        (item) => item.event === type,
      )

      if (stage) {
        completedStages.add(stage.key)
      }
    })
  }

  let activeStage = 'L0'

  if (status === 'COMPLETED') {
    activeStage = 'AGG'
  } else {
    for (const stage of stageDefinitions) {
      if (!completedStages.has(stage.key)) {
        activeStage = stage.key
        break
      }
      activeStage = stage.key
    }

    if (
      events.some(
        (event) =>
          String(event?.event_type || '').toUpperCase() ===
          'AGGREGATION_COMPLETED',
      )
    ) {
      activeStage = 'AGG'
    }
  }

  const eventLabel = (event) => {
    const type = String(
      event?.event_type || 'EVENT',
    )
      .replaceAll('_', ' ')

    return type
  }

  const eventTone = (event) => {
    const type = String(
      event?.event_type || '',
    ).toUpperCase()

    if (
      type.includes('QUARANTINE') ||
      type.includes('ANOMALY') ||
      type.includes('INCIDENT')
    ) {
      return 'danger'
    }

    if (
      type.includes('TRUST') ||
      type.includes('ATTRIBUTION')
    ) {
      return 'warning'
    }

    return 'normal'
  }

  const formatTime = (value) => {
    if (!value) return '--:--:--'

    const date = new Date(value)

    if (Number.isNaN(date.getTime())) {
      return '--:--:--'
    }

    return date.toLocaleTimeString([], {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const clientState = (client) => {
    const update = updates.find(
      (item) =>
        item?.hospital_code === client ||
        item?.hospital_id === client,
    )

    const clientEvents = events.filter(
      (event) => event?.client_id === client,
    )

    const last = clientEvents[
      clientEvents.length - 1
    ]

    if (update?.detection_status === 'QUARANTINED') {
      return {
        label: 'QUARANTINED',
        className: 'quarantined',
      }
    }

    if (update?.detection_status === 'ACCEPTED') {
      return {
        label: 'ACCEPTED',
        className: 'accepted',
      }
    }

    if (last) {
      const type = String(
        last?.event_type || '',
      ).toUpperCase()

      if (type === 'CLIENT_UPDATE_RECEIVED') {
        return {
          label: 'RECEIVED',
          className: 'received',
        }
      }

      if (type === 'INTEGRITY_CHECKED') {
        return {
          label: 'L0 VERIFY',
          className: 'verify',
        }
      }

      if (type === 'FINGERPRINT_GENERATED') {
        return {
          label: 'L1 INSPECT',
          className: 'inspect',
        }
      }

      if (type === 'ANOMALY_DETECTED') {
        return {
          label: 'L2 CORRELATE',
          className: 'correlate',
        }
      }

      if (type.includes('INFLUENCE')) {
        return {
          label: 'L3 INFLUENCE',
          className: 'influence',
        }
      }

      if (type.includes('COUNTERFACTUAL')) {
        return {
          label: 'L4 SIMULATE',
          className: 'simulate',
        }
      }

      if (type.includes('ATTRIBUTION')) {
        return {
          label: 'L5 ATTRIBUTE',
          className: 'attribute',
        }
      }

      if (type.includes('TRUST')) {
        return {
          label: 'TRUST',
          className: 'trust',
        }
      }
    }

    return {
      label: status === 'RUNNING' ? 'TRAINING' : 'IDLE',
      className: status === 'RUNNING' ? 'training' : 'idle',
    }
  }

  if (!latestRound) {
    return (
      <div className="live-round-page">
        <div className="live-empty-state">
          <Activity size={34} strokeWidth={1.2} />
          <div>
            <div className="eyebrow">
              SECURITY / LIVE EXECUTION
            </div>
            <h1>No federation round</h1>
            <p>
              Create a round from Round Configuration to
              begin live execution telemetry.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="live-round-page">
      <header className="live-round-hero">
        <div>
          <div className="eyebrow">
            SECURITY / LIVE EXECUTION
          </div>

          <div className="live-title-row">
            <h1>
              Live Round
              <span>
                R-
                {summary?.round_number ||
                  latestRound?.round_number ||
                  latestRound?.id?.slice?.(0, 8) ||
                  '--'}
              </span>
            </h1>

            <div
              className={`live-state live-state-${status.toLowerCase()}`}
            >
              <i />
              {status}
            </div>
          </div>

          <p>
            Operational view of federated execution and the
            security control plane.
          </p>
        </div>

        <div className="live-header-controls">
          <div className="live-round-selector-box">
            <label>ROUND TELEMETRY SELECTOR</label>
            <select
              value={activeRound?.id || ''}
              onChange={(e) => setSelectedRoundId(e.target.value)}
            >
              {rounds.map((r) => (
                <option key={r.id} value={r.id}>
                  R-{r.round_number} &bull; {r.status} &bull; {r.configuration?.execution_mode || 'SIMULATION'} ({r.participating_clients || 0} nodes)
                </option>
              ))}
            </select>
          </div>

          <div className="live-connection">
            <span>EVENT CHANNEL</span>
          <strong>
            <i />
            {socketState}
          </strong>
          <small>
            {lastEventAt
              ? `LAST EVENT ${formatTime(lastEventAt)}`
              : 'WAITING FOR EVENTS'}
          </small>

          {status === 'RUNNING' && (
            <button
              type="button"
              className="history-start-button"
              disabled={
                finalizing ||
                participating <= 0 ||
                updates.length < participating
              }
              onClick={finalizeRound}
              title={
                updates.length < participating
                  ? `Waiting for hospital submissions: ${updates.length}/${participating}`
                  : 'Finalize this hospital round'
              }
            >
              {finalizing
                ? 'FINALIZING...'
                : updates.length < participating
                  ? `WAITING ${updates.length}/${participating}`
                  : 'FINALIZE ROUND'}
            </button>
          )}

          {finalizeError && (
            <small className="round-action-feedback error">
              {finalizeError}
            </small>
          )}

          {finalizeMessage && (
            <small className="round-action-feedback success">
              {finalizeMessage}
            </small>
          )}
        </div>
        </div>
      </header>

      <section className="live-round-metrics">
        <div className="live-metric">
          <span>ROUND</span>
          <strong>
            R-
            {summary?.round_number ||
              latestRound?.round_number ||
              '--'}
          </strong>
          <small>{status}</small>
        </div>

        <div className="live-metric">
          <span>PARTICIPANTS</span>
          <strong>{participating}</strong>
          <small>CONFIGURED NODES</small>
        </div>

        <div className="live-metric">
          <span>UPDATES</span>
          <strong>{totalUpdates}</strong>
          <small>
            {accepted} ACCEPTED / {quarantined} QUARANTINED
          </small>
        </div>

        <div className="live-metric">
          <span>INCIDENTS</span>
          <strong>{incidentCount}</strong>
          <small>SECURITY SIGNALS</small>
        </div>
      </section>

      <section className="live-topology-panel panel">
        <div className="live-panel-header">
          <div>
            <div className="panel-kicker">
              FEDERATION TELEMETRY
            </div>
            <h2>Participant update flow</h2>
          </div>

          <span className="live-panel-badge">
            {selectedClients.length} ACTIVE CHANNELS
          </span>
        </div>

        <div className="live-topology">
          <div className="live-client-column">
            {selectedClients.length ? (
              selectedClients.map((client) => {
                const state = clientState(client)
                const hospital =
                  hospitalLookup[client]

                return (
                  <div
                    className={`live-client-node ${state.className}`}
                    key={client}
                  >
                    <div className="live-node-icon">
                      <Hospital
                        size={17}
                        strokeWidth={1.4}
                      />
                    </div>

                    <div className="live-node-copy">
                      <strong>
                        {hospital?.code || client}
                      </strong>

                      <span>
                        {hospital?.name ||
                          'Federation participant'}
                      </span>
                    </div>

                    <div className="live-node-state">
                      <i />
                      {state.label}
                    </div>
                  </div>
                )
              })
            ) : (
              <div className="live-no-clients">
                <Users
                  size={20}
                  strokeWidth={1.2}
                />
                <span>
                  Waiting for participant telemetry
                </span>
              </div>
            )}
          </div>

          <div className="live-flow-spine">
            <div className="live-flow-line" />
            <div className="live-flow-node">
              <Upload
                size={16}
                strokeWidth={1.3}
              />
              <span>UPDATE INTAKE</span>
            </div>
            <div className="live-flow-line" />
          </div>

          <div className="live-security-core">
            <div className="live-core-ring">
              <Shield
                size={27}
                strokeWidth={1.2}
              />
            </div>

            <strong>FED SENTINEL</strong>
            <span>SECURITY CONTROL PLANE</span>

            <div className="live-core-status">
              <i />
              {activeStage === 'AGG'
                ? 'SECURE AGGREGATION'
                : `${activeStage} ACTIVE`}
            </div>
          </div>
        </div>
      </section>

      <section className="live-security-panel panel">
        <div className="live-panel-header">
          <div>
            <div className="panel-kicker">
              SECURITY PIPELINE
            </div>
            <h2>VERIFY ? INSPECT ? CORRELATE ? ANALYZE</h2>
          </div>

          <span className="live-principle">
            RISK != VERDICT
          </span>
        </div>

        <div className="live-stage-track">
          {stageDefinitions.map(
            (stage, index) => {
              const Icon = stage.icon
              const completed =
                completedStages.has(stage.key)
              const active =
                activeStage === stage.key

              return (
                <div
                  className={`live-stage ${
                    completed ? 'completed' : ''
                  } ${active ? 'active' : ''}`}
                  key={stage.key}
                >
                  <div className="live-stage-marker">
                    <Icon
                      size={15}
                      strokeWidth={1.4}
                    />
                  </div>

                  <strong>{stage.key}</strong>
                  <span>{stage.label}</span>

                  {index <
                    stageDefinitions.length - 1 && (
                    <div className="live-stage-connector" />
                  )}
                </div>
              )
            },
          )}

          <div
            className={`live-stage final ${
              activeStage === 'AGG'
                ? 'active'
                : ''
            }`}
          >
            <div className="live-stage-marker">
              <GitBranch
                size={15}
                strokeWidth={1.4}
              />
            </div>
            <strong>SAFE</strong>
            <span>AGGREGATE</span>
          </div>
        </div>
      </section>

      <div className="live-lower-grid">
        <section className="live-events-panel panel">
          <div className="live-panel-header">
            <div>
              <div className="panel-kicker">
                EVENT STREAM
              </div>
              <h2>Operational timeline</h2>
            </div>

            <span className="live-panel-badge">
              {events.length} EVENTS
            </span>
          </div>

          <div className="live-event-list">
            {events.length ? (
              events
                .slice()
                .reverse()
                .slice(0, 14)
                .map((event, index) => (
                  <div
                    className={`live-event-row ${eventTone(
                      event,
                    )}`}
                    key={
                      event?.event_id ||
                      event?.id ||
                      `${event?.timestamp}-${index}`
                    }
                  >
                    <time>
                      {formatTime(event?.timestamp)}
                    </time>

                    <div className="live-event-dot">
                      <i />
                    </div>

                    <div className="live-event-copy">
                      <strong>
                        {eventLabel(event)}
                      </strong>

                      <span>
                        {event?.client_id
                          ? `${event.client_id}  /  `
                          : ''}
                        {event?.message ||
                          'Security event recorded.'}
                      </span>
                    </div>
                  </div>
                ))
            ) : (
              <div className="live-event-empty">
                <Activity
                  size={19}
                  strokeWidth={1.2}
                />
                Waiting for round events...
              </div>
            )}
          </div>
        </section>

        <section className="live-update-panel panel">
          <div className="live-panel-header">
            <div>
              <div className="panel-kicker">
                UPDATE TELEMETRY
              </div>
              <h2>Security state</h2>
            </div>
          </div>

          <div className="live-update-list">
            {updates.length ? (
              updates.map((update) => (
                <div
                  className="live-update-row"
                  key={update.id}
                >
                  <div>
                    <strong>
                      {update.hospital_code ||
                        update.hospital_id}
                    </strong>
                    <span>
                      {update.artifact_type ||
                        'MODEL UPDATE'}
                    </span>
                  </div>

                  <div className="live-update-state">
                    <span>
                      L0 {update.l0_status || '--'}
                    </span>
                    <span
                      className={
                        String(
                          update.detection_status || '',
                        ).toUpperCase() ===
                        'QUARANTINED'
                          ? 'danger'
                          : ''
                      }
                    >
                      {update.detection_status ||
                        'PENDING'}
                    </span>
                    <small>
                      TRUST{' '}
                      {update.trust_status ||
                        '--'}
                    </small>
                  </div>
                </div>
              ))
            ) : (
              <div className="live-event-empty">
                <ShieldCheck
                  size={19}
                  strokeWidth={1.2}
                />
                No persisted updates yet.
              </div>
            )}
          </div>
        </section>
      </div>

      {incidents.length > 0 && (
        <section className="live-incident-strip panel">
          <div className="live-incident-icon">
            <AlertTriangle
              size={18}
              strokeWidth={1.3}
            />
          </div>

          <div>
            <div className="panel-kicker">
              ACTIVE SECURITY INCIDENT
            </div>
            <strong>
              {incidents[0]?.title ||
                incidents[0]?.threat_type ||
                'SECURITY INCIDENT'}
            </strong>
            <span>
              {incidents[0]?.recommended_action
                ? `RECOMMENDED ACTION: ${incidents[0].recommended_action}`
                : 'Incident evidence available for investigation.'}
            </span>
          </div>

          <div className="live-incident-meta">
            <span>
              {incidents[0]?.severity || 'INFO'}
            </span>
            <small>
              {incidents[0]?.status || 'OPEN'}
            </small>
          </div>
        </section>
      )}
    </div>
  )
}


function Placeholder({ title, section }) {
  return (
    <div className="placeholder-page">
      <div className="eyebrow">{section}</div>

      <h1>{title}</h1>

      <p>
        This control-plane module is being connected to the live backend.
      </p>

      <div className="placeholder-box">
        <span>&#9671;</span>
        <strong>MODULE READY</strong>
        <small>Real API integration comes next.</small>
      </div>
    </div>
  )
}


function NavIcon({ name }) {
  const props = {
    size: 13,
    strokeWidth: 1.5,
    'aria-hidden': true,
  }

  const icons = {
    command: Gauge,
    overview: Network,
    hospitals: Hospital,
    synthetic: Database,
    rounds: Workflow,
    live: Activity,
    intake: Upload,
    verify: ShieldCheck,
    inspect: Search,
    correlate: GitBranch,
    quarantine: ShieldAlert,
    influence: BarChart3,
    simulate: Radar,
    attribute: Layers3,
    trust: Shield,
    incidents: AlertTriangle,
    aggregation: GitBranch,
    model: Globe2,
    audit: FileClock,
    replay: History,
    reports: FileText,
    settings: Settings,
    federation: Users,
    terminal: Terminal,
    sliders: SlidersHorizontal,
    archive: Archive,
  }

  const IconComponent = icons[name] || Activity

  return <IconComponent {...props} />
}

function HospitalPortalShell({ token, onLogout }) {
  const hospitalId =
    localStorage.getItem('fedsentinel_hospital_id') || 'HOSPITAL'

  return (
    <div className="app-shell hospital-portal-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-lockup">
            <span className="brand-mark">FS</span>
            <div>
              <strong>FED SENTINEL</strong>
              <span>HOSPITAL PORTAL</span>
            </div>
          </div>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-label">COMMAND</div>
          <button className="nav-item active">
            <span>Hospital Command</span>
          </button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-label">HOSPITAL</div>
          <button className="nav-item">
            <span>My Hospital</span>
          </button>
          <button className="nav-item">
            <span>Federation</span>
          </button>
          <button className="nav-item">
            <span>Team & Access</span>
          </button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-label">DATA</div>
          <button className="nav-item">
            <span>Datasets</span>
          </button>
          <button className="nav-item">
            <span>Data Quality</span>
          </button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-label">FEDERATED LEARNING</div>
          <button className="nav-item">
            <span>Current Round</span>
          </button>
          <button className="nav-item">
            <span>Local Training</span>
          </button>
          <button className="nav-item">
            <span>Model Updates</span>
          </button>
          <button className="nav-item">
            <span>Global Model</span>
          </button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-label">SECURITY</div>
          <button className="nav-item">
            <span>Security Status</span>
          </button>
          <button className="nav-item">
            <span>Incidents</span>
          </button>
          <button className="nav-item">
            <span>Trust</span>
          </button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-label">REPORTS</div>
          <button className="nav-item">
            <span>Training Reports</span>
          </button>
          <button className="nav-item">
            <span>Participation Reports</span>
          </button>
          <button className="nav-item">
            <span>Security Reports</span>
          </button>
          <button className="nav-item">
            <span>Model Reports</span>
          </button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-label">SYSTEM</div>
          <button className="nav-item">
            <span>Audit Activity</span>
          </button>
          <button className="nav-item">
            <span>Settings</span>
          </button>
        </div>

        <div className="sidebar-bottom">
          <div className="privacy-note">
            <strong>PRIVACY BOUNDARY</strong>
            <span>
              Raw hospital and patient data remains inside the hospital.
            </span>
          </div>

          <button className="logout-button" onClick={onLogout}>
            EXIT HOSPITAL PORTAL
          </button>
        </div>
      </aside>

      <main className="main-content">
        <div className="page-header">
          <div>
            <div className="eyebrow">FED SENTINEL / HOSPITAL</div>
            <h1>Hospital Command</h1>
            <p>
              Secure local control plane for {hospitalId}.
            </p>
          </div>
        </div>

        <section className="content-card">
          <div className="card-header">
            <div>
              <div className="eyebrow">HOSPITAL PORTAL</div>
              <h2>Hospital Control Centre</h2>
            </div>
            <span className="status-badge">AUTHENTICATED</span>
          </div>

          <div className="empty-state">
            <strong>Hospital workflow ready</strong>
            <p>
              The portal shell is connected to the authenticated hospital
              session. Dataset management, local training, federation,
              model-update monitoring, security, and reporting modules will
              use the existing hospital APIs.
            </p>
          </div>
        </section>

        <section className="content-card">
          <div className="card-header">
            <div>
              <div className="eyebrow">DATA BOUNDARY</div>
              <h2>Privacy Architecture</h2>
            </div>
          </div>

          <div className="security-grid">
            <div className="security-item">
              <strong>LOCAL ONLY</strong>
              <span>Patient records and raw hospital datasets</span>
            </div>

            <div className="security-item">
              <strong>SHARED</strong>
              <span>Model updates and required security metadata</span>
            </div>

            <div className="security-item">
              <strong>PROTECTED</strong>
              <span>Hospital identity and federation participation</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

function App() {
  const [token, setToken] = useState(
    () => localStorage.getItem('fedsentinel_token') || '',
  )

  const [route, setRoute] = useState(
    () => window.location.pathname || '/admin/login',
  )

  const isHospitalRoute = route.startsWith('/hospital')
  const portal = isHospitalRoute ? 'hospital' : 'admin'

  useEffect(() => {
    function handleRouteChange() {
      setRoute(window.location.pathname || '/admin/login')
    }

    window.addEventListener('popstate', handleRouteChange)

    return () => {
      window.removeEventListener('popstate', handleRouteChange)
    }
  }, [])

  const [active, setActive] = useState('command')
  const [loading, setLoading] = useState(Boolean(token))
  const [error, setError] = useState('')

  const [data, setData] = useState({
    hospitals: [],
    rounds: [],
    incidents: [],
    securityRound: null,
    trustRecords: [],
  })

  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }

    const role = localStorage.getItem('fedsentinel_role') || ''
    const storedPortal = localStorage.getItem('fedsentinel_portal') || ''

    const adminRoles = ['SUPER_ADMIN', 'ADMIN']
    const hospitalRoles = ['HOSPITAL_ADMIN', 'HOSPITAL_OPERATOR']

    const roleBelongsToCurrentPortal = isHospitalRoute
      ? hospitalRoles.includes(role)
      : adminRoles.includes(role)

    const portalMatchesCurrentRoute = storedPortal
      ? storedPortal === portal
      : true

    if (!roleBelongsToCurrentPortal || !portalMatchesCurrentRoute) {
      localStorage.removeItem('fedsentinel_token')
      localStorage.removeItem('fedsentinel_portal')
      localStorage.removeItem('fedsentinel_role')
      localStorage.removeItem('fedsentinel_hospital_id')

      setToken('')
      setLoading(false)

      return
    }

    let cancelled = false

    async function load() {
      try {
        setError('')

        if (isHospitalRoute) {
          setLoading(false)
          return
        }

        const [hospitals, rounds] = await Promise.all([
          apiFetch('/api/v1/hospitals', token),
          apiFetch(
            `/api/v1/federations/${FEDERATION_ID}/rounds`,
            token,
          ),
        ])

        if (cancelled) return

        const hospitalList = Array.isArray(hospitals)
          ? hospitals
          : hospitals.value || []

        const roundList = Array.isArray(rounds)
          ? rounds
          : rounds.value || []

        const latestRound = roundList[0]

        let incidents = []

        if (latestRound?.id) {
          try {
            const incidentResponse = await apiFetch(
              `/api/v1/security/rounds/${latestRound.id}/incidents`,
              token,
            )

            incidents = Array.isArray(incidentResponse)
              ? incidentResponse
              : incidentResponse.value || []
          } catch {
            incidents = []
          }
        }

        let securityRound = null

        if (latestRound?.id) {
          try {
            securityRound = await apiFetch(
              `/api/v1/security/rounds/${latestRound.id}`,
              token,
            )
          } catch {
            // Security summary is supplemental.
            // The main dashboard still works if unavailable.
          }
        }

        let trustRecords = []

        if (latestRound?.id) {
          try {
            const trustResponse = await apiFetch(
              `/api/v1/security/rounds/${latestRound.id}/trust`,
              token,
            )

            trustRecords = Array.isArray(trustResponse)
              ? trustResponse
              : trustResponse.value || []
          } catch {
            // Trust records are supplemental.
            trustRecords = []
          }
        }

        if (cancelled) return

        setData({
          hospitals: hospitalList,
          rounds: roundList,
          incidents: incidents,
          securityRound,
          trustRecords,
        })
      } catch (err) {
        if (!cancelled) {
          setError(err.message)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    setLoading(true)
    load()

    const refresh = window.setInterval(load, 5000)

    return () => {
      cancelled = true
      window.clearInterval(refresh)
    }
  }, [token, refreshKey, isHospitalRoute])

  function logout() {
    localStorage.removeItem('fedsentinel_token')
    localStorage.removeItem('fedsentinel_portal')
    localStorage.removeItem('fedsentinel_role')
    localStorage.removeItem('fedsentinel_hospital_id')

    setToken('')

    goTo(isHospitalRoute ? '/hospital/login' : '/admin/login')

    setData({
      hospitals: [],
      rounds: [],
      incidents: [],
      securityRound: null,
      trustRecords: [],
    })
  }

  if (!token) {
    return (
      <Login
        onLogin={setToken}
        portal={isHospitalRoute ? 'hospital' : 'admin'}
      />
    )
  }

  if (isHospitalRoute) {
    return <HospitalPortal token={token} onLogout={logout} />
  }

  const activeItem = navGroups
    .flatMap((group) => group.items)
    .find((item) => item.id === active)

  return (
    <div className="app-shell">
      <Sidebar
        active={active}
        onNavigate={setActive}
        onLogout={logout}
      />

      <main className="main-content">
        {loading && (
          <div className="loading-strip">
            <span className="pulse" />
            SYNCHRONIZING SECURITY TELEMETRY
          </div>
        )}

        {error && (
          <div className="api-error">
            <strong>API CONNECTION ERROR</strong>
            <span>{error}</span>
          </div>
        )}

        {active === 'command' ? (
          <CommandCenter data={data} />
        ) : active === 'overview' ? (
          <FederationOverview data={data} />
        ) : active === 'hospitals' ? (
          <HospitalsPage
            data={data}
            token={token}
            onDataRefresh={() => setRefreshKey((value) => value + 1)}
          />
        ) : active === 'synthetic' ? (
          <SyntheticDataPage data={data} />
        ) : active === 'round-config' ? (
          <RoundConfigurationPage
            data={data}
            token={token}
            onDataRefresh={() => setRefreshKey((value) => value + 1)}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'live-round' ? (
          <LiveRoundPage
            data={data}
            token={token}
          />
        ) : active === 'intake' ? (
          <UpdateIntakePage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'l0' ? (
          <L0VerifyPage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'l1' ? (
          <L1InspectPage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'l2' ? (
          <L2CorrelatePage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'quarantine' ? (
          <QuarantinePage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
            onDataRefresh={() => setRefreshKey((value) => value + 1)}
          />
        ) : active === 'l3' ? (
          <L3InfluencePage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'l4' ? (
          <L4SimulatePage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'l5' ? (
          <L5AttributePage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'trust' ? (
          <TrustEnginePage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'incidents' ? (
          <IncidentsPage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
            onDataRefresh={() => setRefreshKey((value) => value + 1)}
          />
        ) : active === 'aggregation' ? (
          <SafeAggregationPage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'model' ? (
          <GlobalModelPage
            data={data}
            token={token}
          />
        ) : active === 'audit' ? (
          <AuditTrailPage
            data={data}
            token={token}
          />
        ) : active === 'replay' ? (
          <RoundReplayPage
            data={data}
            token={token}
            onNavigate={(pageId) => setActive(pageId)}
          />
        ) : active === 'reports' ? (
          <ReportsPage
            data={data}
            token={token}
          />
        ) : (
          <Placeholder
            title={activeItem?.label || 'Module'}
            section="FED SENTINEL / CONTROL PLANE"
          />
        )}
      </main>
    </div>
  )
}

export default App
















