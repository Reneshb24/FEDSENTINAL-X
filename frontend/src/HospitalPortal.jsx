import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Building2,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Database,
  Download,
  FileClock,
  FileText,
  Gauge,
  GitBranch,
  Globe2,
  Hospital,
  Info,
  Layers3,
  Lock,
  Network,
  RefreshCw,
  Save,
  Search,
  Settings,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Upload,
  Users,
  Workflow,
  XCircle,
  Link2,

  X,
} from 'lucide-react'

const rawHospitalApi = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://127.0.0.1:8000'
const HOSPITAL_API = rawHospitalApi.replace(/\/+$/, '')
const HOSPITAL_FEDERATION_ID =
  (import.meta.env && import.meta.env.VITE_FEDERATION_ID) || '413ef0b3-a947-4a02-a652-d963ef14b8da'

async function hospitalFetch(path, token, options = {}) {
  const response = await fetch(`${HOSPITAL_API}${path}`, {
    ...options,
    headers: {
      ...(options.body && !(options.body instanceof FormData)
        ? { 'Content-Type': 'application/json' }
        : {}),
      ...(options.headers || {}),
      ...(token
        ? { Authorization: `Bearer ${token}` }
        : {}),
    },
  })

  if (response.status === 401) {
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

function hospitalArray(value) {
  if (Array.isArray(value)) return value
  if (Array.isArray(value?.value)) return value.value
  if (Array.isArray(value?.items)) return value.items
  if (Array.isArray(value?.results)) return value.results
  return []
}

function formatDate(value) {
  if (!value) return '—'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return String(value)

  return date.toLocaleString()
}

function formatBytes(bytes) {
  if (bytes === null || bytes === undefined) return '—'

  const value = Number(bytes)

  if (!Number.isFinite(value)) return '—'
  if (value < 1024) return `${value} B`
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`
  if (value < 1024 * 1024 * 1024) {
    return `${(value / (1024 * 1024)).toFixed(1)} MB`
  }

  return `${(value / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

function statusClass(value) {
  const text = String(value || '').toUpperCase()

  if (
    text.includes('TRUST') ||
    text.includes('ACTIVE') ||
    text.includes('ACCEPT') ||
    text.includes('COMPLET') ||
    text.includes('VALID')
  ) {
    return 'hp-status hp-status-good'
  }

  if (
    text.includes('PENDING') ||
    text.includes('RUNNING') ||
    text.includes('REVIEW') ||
    text.includes('ANALYZ')
  ) {
    return 'hp-status hp-status-warn'
  }

  if (
    text.includes('QUARANT') ||
    text.includes('REJECT') ||
    text.includes('FAIL') ||
    text.includes('ERROR') ||
    text.includes('SUSPEND')
  ) {
    return 'hp-status hp-status-danger'
  }

  return 'hp-status'
}

function downloadText(filename, content, type = 'text/plain') {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')

  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()

  URL.revokeObjectURL(url)
}

function csvEscape(value) {
  const text = value === null || value === undefined ? '' : String(value)
  return `"${text.replaceAll('"', '""')}"`
}

function toCsv(rows) {
  if (!rows.length) return ''

  const columns = Array.from(
    rows.reduce((set, row) => {
      Object.keys(row).forEach((key) => set.add(key))
      return set
    }, new Set()),
  )

  return [
    columns.map(csvEscape).join(','),
    ...rows.map((row) =>
      columns.map((column) => csvEscape(row[column])).join(','),
    ),
  ].join('\n')
}

function PortalStat({ icon: Icon, label, value, detail }) {
  return (
    <div className="hp-stat">
      <div className="hp-stat-icon">
        <Icon size={18} />
      </div>

      <div className="hp-stat-label">{label}</div>

      <div className="hp-stat-value">{value}</div>

      <div className="hp-stat-detail">{detail}</div>
    </div>
  )
}

function SectionTitle({ eyebrow, title, description, action }) {
  return (
    <div className="hp-section-title">
      <div>
        <div className="hp-eyebrow">{eyebrow}</div>
        <h2>{title}</h2>
        {description && <p>{description}</p>}
      </div>

      {action}
    </div>
  )
}

function InfoRow({ label, value, mono = false }) {
  return (
    <div className="hp-info-row">
      <span>{label}</span>
      <strong className={mono ? 'hp-mono' : ''}>{value ?? '—'}</strong>
    </div>
  )
}

function EmptyModule({ icon: Icon = Info, title, description }) {
  return (
    <div className="hp-empty">
      <div className="hp-empty-icon">
        <Icon size={25} />
      </div>

      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  )
}

function HospitalCommand({
  hospital,
  dashboard,
  status,
  rounds,
  onNavigate,
  onRefresh,
  refreshing,
}) {
  const latestRound = rounds[0] || null

  const trustScore =
    dashboard?.trust_score === null ||
    dashboard?.trust_score === undefined
      ? null
      : Number(dashboard.trust_score)

  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">FED SENTINEL / HOSPITAL</div>

          <h1>Hospital Command</h1>

          <p>
            Secure local control plane for{' '}
            <strong>{hospital?.name || 'your hospital'}</strong>.
          </p>
        </div>

        <button
          className="hp-button hp-button-secondary"
          onClick={onRefresh}
          disabled={refreshing}
        >
          <RefreshCw
            size={15}
            className={refreshing ? 'hp-spin' : ''}
          />
          {refreshing ? 'SYNCING' : 'REFRESH'}
        </button>
      </div>

      <div className="hp-hero">
        <div className="hp-hero-main">
          <div className="hp-hero-icon">
            <Hospital size={30} />
          </div>

          <div>
            <div className="hp-eyebrow">CONNECTED HOSPITAL</div>

            <h2>{hospital?.name || 'Hospital Workspace'}</h2>

            <p>
              {hospital?.code || 'HOSPITAL'} ·{' '}
              {hospital?.location || 'Private hospital workspace'}
            </p>
          </div>
        </div>

        <div className="hp-hero-statuses">
          <span className={statusClass(status?.status)}>
            {status?.status || 'UNKNOWN'}
          </span>

          <span
            className={statusClass(
              dashboard?.federation_member
                ? dashboard?.membership_status || 'MEMBER'
                : 'NOT A MEMBER',
            )}
          >
            {dashboard?.federation_member
              ? dashboard?.membership_status || 'FEDERATION MEMBER'
              : 'NOT A MEMBER'}
          </span>
        </div>
      </div>

      <div className="hp-stat-grid">
        <PortalStat
          icon={Database}
          label="DATASETS"
          value={dashboard?.total_datasets ?? 0}
          detail={`${dashboard?.active_datasets ?? 0} active`}
        />

        <PortalStat
          icon={Upload}
          label="MODEL UPDATES"
          value={dashboard?.total_updates ?? 0}
          detail={`${dashboard?.accepted_updates ?? 0} accepted`}
        />

        <PortalStat
          icon={ShieldAlert}
          label="QUARANTINED"
          value={dashboard?.quarantined_updates ?? 0}
          detail="updates requiring review"
        />

        <PortalStat
          icon={AlertTriangle}
          label="OPEN INCIDENTS"
          value={dashboard?.open_incidents ?? 0}
          detail="hospital-visible incidents"
        />
      </div>

      <div className="hp-grid-2">
        <section className="hp-card">
          <SectionTitle
            eyebrow="FEDERATION"
            title="Participation"
            description="Your hospital's current federation state."
          />

          <div className="hp-info-list">
            <InfoRow
              label="Federation member"
              value={
                dashboard?.federation_member
                  ? 'YES'
                  : 'NO'
              }
            />

            <InfoRow
              label="Membership"
              value={
                dashboard?.membership_status ||
                status?.membership_status ||
                'NOT ENROLLED'
              }
            />

            <InfoRow
              label="Eligibility"
              value={
                status?.is_eligible
                  ? 'ELIGIBLE'
                  : 'NOT ELIGIBLE'
              }
            />

            <InfoRow
              label="Hospital status"
              value={status?.status || 'UNKNOWN'}
            />
          </div>

          <button
            className="hp-link-button"
            onClick={() => onNavigate('federation')}
          >
            Open federation workspace
            <ChevronRight size={15} />
          </button>
        </section>

        <section className="hp-card">
          <SectionTitle
            eyebrow="TRUST"
            title="Hospital trust"
            description="Current trust information exposed to the hospital."
          />

          <div className="hp-trust-number">
            {trustScore === null
              ? '—'
              : trustScore.toFixed(1)}
          </div>

          <div className="hp-trust-label">
            {dashboard?.trust_status ||
              'Trust evaluation pending'}
          </div>

          <div className="hp-progress">
            <span
              style={{
                width:
                  trustScore === null
                    ? '0%'
                    : `${Math.max(
                        0,
                        Math.min(100, trustScore),
                      )}%`,
              }}
            />
          </div>
        </section>
      </div>

      <div className="hp-grid-2">
        <section className="hp-card">
          <SectionTitle
            eyebrow="CURRENT ROUND"
            title={
              latestRound
                ? `Round ${latestRound.round_number ?? '—'}`
                : 'No round detected'
            }
            description="Federation round information visible to this session."
          />

          {latestRound ? (
            <div className="hp-info-list">
              <InfoRow
                label="Round ID"
                value={latestRound.id}
                mono
              />

              <InfoRow
                label="Status"
                value={latestRound.status}
              />

              <InfoRow
                label="Participating clients"
                value={
                  latestRound.participating_clients ??
                  latestRound.configured_clients ??
                  '—'
                }
              />

              <InfoRow
                label="Accepted updates"
                value={latestRound.accepted_updates ?? 0}
              />

              <InfoRow
                label="Quarantined updates"
                value={
                  latestRound.quarantined_updates ?? 0
                }
              />
            </div>
          ) : (
            <EmptyModule
              icon={GitBranch}
              title="No federation round available"
              description="There is currently no round visible to this hospital session."
            />
          )}

          <button
            className="hp-link-button"
            onClick={() => onNavigate('round')}
          >
            Open current round
            <ChevronRight size={15} />
          </button>
        </section>

        <section className="hp-card">
          <SectionTitle
            eyebrow="PRIVACY BOUNDARY"
            title="What leaves the hospital?"
            description="FedSentinel separates local clinical data from federated model evidence."
          />

          <div className="hp-boundary">
            <div className="hp-boundary-row local">
              <Lock size={17} />
              <div>
                <strong>LOCAL ONLY</strong>
                <span>Patient records</span>
              </div>
            </div>

            <div className="hp-boundary-row local">
              <Database size={17} />
              <div>
                <strong>LOCAL ONLY</strong>
                <span>Raw hospital datasets</span>
              </div>
            </div>

            <div className="hp-boundary-row shared">
              <Upload size={17} />
              <div>
                <strong>SHARED</strong>
                <span>Model updates</span>
              </div>
            </div>

            <div className="hp-boundary-row shared">
              <Shield size={17} />
              <div>
                <strong>SHARED</strong>
                <span>Security metadata</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <section className="hp-card">
        <SectionTitle
          eyebrow="FEDERATED LEARNING"
          title="Hospital contribution pipeline"
          description="The complete hospital-side learning lifecycle."
        />

        <div className="hp-pipeline">
          {[
            ['01', 'DATASET', 'Prepare verified local data'],
            ['02', 'ROUND', 'Wait for an eligible federation round'],
            ['03', 'TRAIN', 'Train locally from the verified model'],
            ['04', 'UPDATE', 'Generate a model delta artifact'],
            ['05', 'SECURITY', 'FedSentinel analyzes the update'],
            ['06', 'AGGREGATE', 'Only safe updates contribute'],
          ].map(([number, title, description]) => (
            <div className="hp-pipeline-step" key={number}>
              <span>{number}</span>
              <strong>{title}</strong>
              <small>{description}</small>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}

function MyHospitalPage({
  hospital,
  dashboard,
  status,
  onNavigate,
}) {
  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">HOSPITAL / IDENTITY</div>
          <h1>My Hospital</h1>
          <p>
            Hospital identity, eligibility, security posture and local
            operating state.
          </p>
        </div>
      </div>

      <div className="hp-grid-2">
        <section className="hp-card">
          <SectionTitle
            eyebrow="IDENTITY"
            title={hospital?.name || 'Hospital'}
          />

          <div className="hp-info-list">
            <InfoRow label="Hospital code" value={hospital?.code} />
            <InfoRow label="Hospital ID" value={hospital?.id} mono />
            <InfoRow label="Location" value={hospital?.location} />
            <InfoRow
              label="Contact email"
              value={hospital?.contact_email}
            />
            <InfoRow
              label="Contact phone"
              value={hospital?.contact_phone}
            />
            <InfoRow
              label="Created"
              value={formatDate(hospital?.created_at)}
            />
          </div>
        </section>

        <section className="hp-card">
          <SectionTitle
            eyebrow="POSTURE"
            title="Operating status"
          />

          <div className="hp-status-stack">
            <div>
              <span>Hospital</span>
              <strong className={statusClass(status?.status)}>
                {status?.status || 'UNKNOWN'}
              </strong>
            </div>

            <div>
              <span>Security</span>
              <strong className={statusClass(status?.security_status)}>
                {status?.security_status || 'UNKNOWN'}
              </strong>
            </div>

            <div>
              <span>Federation eligibility</span>
              <strong className={statusClass(
                status?.is_eligible
                  ? 'ELIGIBLE'
                  : 'NOT ELIGIBLE',
              )}>
                {status?.is_eligible
                  ? 'ELIGIBLE'
                  : 'NOT ELIGIBLE'}
              </strong>
            </div>
          </div>
        </section>
      </div>

      <section className="hp-card">
        <SectionTitle
          eyebrow="ACCESS MODEL"
          title="Hospital data boundary"
          description="The hospital portal is tenant-scoped by the authenticated hospital identity."
        />

        <div className="hp-grid-3">
          <div className="hp-feature">
            <Lock size={20} />
            <strong>Clinical data stays local</strong>
            <span>
              Patient records and raw datasets are not exposed through
              the federation control plane.
            </span>
          </div>

          <div className="hp-feature">
            <ShieldCheck size={20} />
            <strong>Security is centralized</strong>
            <span>
              Submitted model updates are evaluated by the FedSentinel
              security pipeline.
            </span>
          </div>

          <div className="hp-feature">
            <Network size={20} />
            <strong>Participation is controlled</strong>
            <span>
              Federation eligibility and membership determine whether
              the hospital can participate.
            </span>
          </div>
        </div>

        <button
          className="hp-link-button"
          onClick={() => onNavigate('team')}
        >
          Review team and access
          <ChevronRight size={15} />
        </button>
      </section>
    </>
  )
}

function FederationPage({
  rounds,
  dashboard,
  status,
  onRefresh,
}) {
  const latestRound = rounds[0] || null

  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">HOSPITAL / FEDERATION</div>
          <h1>Federation</h1>
          <p>
            View your hospital's membership and current federation
            participation state.
          </p>
        </div>

        <button
          className="hp-button hp-button-secondary"
          onClick={onRefresh}
        >
          <RefreshCw size={15} />
          REFRESH
        </button>
      </div>

      <div className="hp-grid-3">
        <PortalStat
          icon={Network}
          label="MEMBERSHIP"
          value={
            dashboard?.federation_member
              ? 'ACTIVE'
              : 'NONE'
          }
          detail={
            dashboard?.membership_status ||
            'Not enrolled'
          }
        />

        <PortalStat
          icon={ShieldCheck}
          label="ELIGIBILITY"
          value={
            status?.is_eligible ? 'YES' : 'NO'
          }
          detail={
            status?.security_status || 'Unknown'
          }
        />

        <PortalStat
          icon={GitBranch}
          label="CURRENT ROUND"
          value={
            latestRound?.round_number ?? '—'
          }
          detail={
            latestRound?.status || 'No round'
          }
        />
      </div>

      <section className="hp-card">
        <SectionTitle
          eyebrow="CURRENT FEDERATION ROUND"
          title={
            latestRound
              ? `Round ${latestRound.round_number ?? '—'}`
              : 'No active round'
          }
        />

        {latestRound ? (
          <div className="hp-round-detail">
            <div className="hp-info-list">
              <InfoRow
                label="Round ID"
                value={latestRound.id}
                mono
              />
              <InfoRow
                label="Status"
                value={latestRound.status}
              />
              <InfoRow
                label="Participants"
                value={
                  latestRound.participating_clients ??
                  '—'
                }
              />
              <InfoRow
                label="Accepted updates"
                value={
                  latestRound.accepted_updates ?? 0
                }
              />
              <InfoRow
                label="Quarantined updates"
                value={
                  latestRound.quarantined_updates ?? 0
                }
              />
              <InfoRow
                label="Started"
                value={formatDate(latestRound.started_at)}
              />
            </div>

            <div className="hp-round-state">
              <GitBranch size={30} />
              <strong>
                {latestRound.status || 'UNKNOWN'}
              </strong>
              <span>
                The hospital can participate only when backend
                eligibility and round conditions permit it.
              </span>
            </div>
          </div>
        ) : (
          <EmptyModule
            icon={Network}
            title="No round available"
            description="No federation round is currently visible to this hospital."
          />
        )}
      </section>

      <section className="hp-card">
        <SectionTitle
          eyebrow="IMPORTANT"
          title="Federation participation"
        />

        <div className="hp-notice hp-notice-info">
          <Info size={18} />
          <div>
            <strong>Hospital-side federation control</strong>
            <p>
              The current backend exposes federation membership and
              round visibility, but does not expose a hospital-side
              “request to join federation” endpoint. This portal
              therefore does not fake a join-request submission.
            </p>
          </div>
        </div>
      </section>
    </>
  )
}

function TeamAccessPage() {
  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">HOSPITAL / ACCESS</div>
          <h1>Team & Access</h1>
          <p>
            Hospital account and access boundary.
          </p>
        </div>
      </div>

      <section className="hp-card">
        <SectionTitle
          eyebrow="CURRENT ACCOUNT"
          title="Hospital administrator"
        />

        <div className="hp-notice hp-notice-info">
          <Users size={19} />

          <div>
            <strong>Authenticated hospital administrator</strong>
            <p>
              Your current session is authenticated as a hospital
              administrator and is scoped to its hospital identity.
              The existing backend does not expose a hospital-side
              user-management API, so no fake user creation or role
              changes are presented here.
            </p>
          </div>
        </div>
      </section>

      <section className="hp-grid-3">
        <div className="hp-feature">
          <Lock size={20} />
          <strong>Hospital scoped</strong>
          <span>
            Hospital resources are resolved from the authenticated
            hospital identity.
          </span>
        </div>

        <div className="hp-feature">
          <ShieldCheck size={20} />
          <strong>Role protected</strong>
          <span>
            Hospital access is enforced by the backend authorization
            layer.
          </span>
        </div>

        <div className="hp-feature">
          <Activity size={20} />
          <strong>Auditable</strong>
          <span>
            Supported hospital operations are recorded by backend
            services where applicable.
          </span>
        </div>
      </section>
    </>
  )
}

function DatasetsPage({
  token,
  datasets,
  selectedDataset,
  setSelectedDataset,
  onReload,
}) {
  const [showCreate, setShowCreate] = useState(false)
  const [editing, setEditing] = useState(null)
  const [search, setSearch] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [createForm, setCreateForm] = useState({
    name: '',
    dataset_type: 'IMAGE_CLASSIFICATION',
    sample_count: 0,
    num_classes: 10,
  })
  const [editForm, setEditForm] = useState({
    name: '',
    dataset_type: '',
    sample_count: 0,
    num_classes: 10,
  })
  const [versionName, setVersionName] = useState('v1')
  const [versionFile, setVersionFile] = useState(null)
  const [versions, setVersions] = useState([])
  const [loadingVersions, setLoadingVersions] = useState(false)
  const [ingestMode, setIngestMode] = useState('upload')
  const [recordLink, setRecordLink] = useState('')
  const [recordFormat, setRecordFormat] = useState('AUTO')

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()

    if (!term) return datasets

    return datasets.filter((dataset) =>
      [
        dataset.name,
        dataset.dataset_type,
        dataset.id,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
        .includes(term),
    )
  }, [datasets, search])

  async function createDataset(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setMessage('')

    try {
      await hospitalFetch(
        '/api/v1/hospital/datasets',
        token,
        {
          method: 'POST',
          body: JSON.stringify({
            name: createForm.name.trim(),
            dataset_type: createForm.dataset_type,
            sample_count: Number(createForm.sample_count),
            num_classes: Number(createForm.num_classes),
          }),
        },
      )

      setMessage('Dataset created successfully.')
      setCreateForm({
        name: '',
        dataset_type: 'IMAGE_CLASSIFICATION',
        sample_count: 0,
        num_classes: 10,
      })
      setShowCreate(false)
      await onReload()
    } catch (err) {
      if (err.message === 'SESSION_EXPIRED') {
        throw err
      }

      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function updateDataset(event) {
    event.preventDefault()

    if (!editing) return

    setBusy(true)
    setError('')
    setMessage('')

    try {
      await hospitalFetch(
        `/api/v1/hospital/datasets/${editing.id}`,
        token,
        {
          method: 'PATCH',
          body: JSON.stringify({
            name: editForm.name.trim(),
            dataset_type: editForm.dataset_type,
            sample_count: Number(editForm.sample_count),
            num_classes: Number(editForm.num_classes),
          }),
        },
      )

      setMessage('Dataset updated successfully.')
      setEditing(null)
      await onReload()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function toggleDataset(dataset) {
    setBusy(true)
    setError('')
    setMessage('')

    try {
      await hospitalFetch(
        `/api/v1/hospital/datasets/${dataset.id}/${
          dataset.is_active ? 'deactivate' : 'activate'
        }`,
        token,
        { method: 'POST' },
      )

      setMessage(
        dataset.is_active
          ? 'Dataset deactivated.'
          : 'Dataset activated.',
      )

      await onReload()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function loadVersions(dataset) {
    setSelectedDataset(dataset)
    setLoadingVersions(true)
    setError('')

    try {
      const response = await hospitalFetch(
        `/api/v1/hospital/datasets/${dataset.id}/versions`,
        token,
      )

      setVersions(hospitalArray(response))
    } catch (err) {
      setError(err.message)
      setVersions([])
    } finally {
      setLoadingVersions(false)
    }
  }

  async function uploadVersion(event) {
    event.preventDefault()

    if (!selectedDataset || !versionFile) {
      setError('Select a dataset and a file first.')
      return
    }

    setBusy(true)
    setError('')
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', versionFile)

      const response = await hospitalFetch(
        `/api/v1/hospital/datasets/${selectedDataset.id}/versions/upload?version=${encodeURIComponent(
          versionName.trim(),
        )}`,
        token,
        {
          method: 'POST',
          body: formData,
        },
      )

      setMessage(
        response?.message ||
          'Dataset version uploaded and validated.',
      )

      setVersionFile(null)
      setVersionName('v1')

      const refreshed = await hospitalFetch(
        `/api/v1/hospital/datasets/${selectedDataset.id}/versions`,
        token,
      )

      setVersions(hospitalArray(refreshed))
      await onReload()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function linkVersion(event) {
    event.preventDefault()
    if (!selectedDataset || !recordLink.trim()) {
      setError('Select a dataset and provide a record link / path.')
      return
    }

    setBusy(true)
    setError('')
    setMessage('')

    try {
      const response = await hospitalFetch(
        `/api/v1/hospital/datasets/${selectedDataset.id}/versions/link`,
        token,
        {
          method: 'POST',
          body: JSON.stringify({
            version: versionName.trim(),
            record_link: recordLink.trim(),
            format: recordFormat,
          }),
        },
      )

      setMessage(
        response?.message ||
          'Dataset records successfully processed and ingested within hospital boundary.',
      )
      setRecordLink('')
      setVersionName('v2')

      const refreshed = await hospitalFetch(
        `/api/v1/hospital/datasets/${selectedDataset.id}/versions`,
        token,
      )
      setVersions(hospitalArray(refreshed))
      await onReload()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  function beginEdit(dataset) {
    setEditing(dataset)

    setEditForm({
      name: dataset.name || '',
      dataset_type:
        dataset.dataset_type || 'IMAGE_CLASSIFICATION',
      sample_count: dataset.sample_count ?? 0,
      num_classes: dataset.num_classes ?? 10,
    })
  }

  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">DATA / LOCAL STORAGE</div>
          <h1>Datasets</h1>
          <p>
            Manage hospital-local datasets, versions, validation and
            activation state.
          </p>
        </div>

        <button
          className="hp-button hp-button-primary"
          onClick={() => setShowCreate(true)}
        >
          <Database size={15} />
          CREATE DATASET
        </button>
      </div>

      {message && (
        <div className="hp-notice hp-notice-success">
          <CheckCircle2 size={18} />
          <span>{message}</span>
          <button onClick={() => setMessage('')}>
            <X size={15} />
          </button>
        </div>
      )}

      {error && (
        <div className="hp-notice hp-notice-danger">
          <AlertTriangle size={18} />
          <span>{error}</span>
          <button onClick={() => setError('')}>
            <X size={15} />
          </button>
        </div>
      )}

      <section className="hp-card">
        <div className="hp-toolbar">
          <div className="hp-search">
            <Search size={16} />
            <input
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Search datasets..."
            />
          </div>

          <div className="hp-toolbar-meta">
            {filtered.length} dataset
            {filtered.length === 1 ? '' : 's'}
          </div>
        </div>

        {filtered.length === 0 ? (
          <EmptyModule
            icon={Database}
            title="No datasets found"
            description="Create a dataset or adjust your search."
          />
        ) : (
          <div className="hp-table-wrap">
            <table className="hp-table">
              <thead>
                <tr>
                  <th>DATASET</th>
                  <th>TYPE</th>
                  <th>SAMPLES</th>
                  <th>CLASSES</th>
                  <th>STATE</th>
                  <th>ACTIONS</th>
                </tr>
              </thead>

              <tbody>
                {filtered.map((dataset) => (
                  <tr key={dataset.id}>
                    <td>
                      <strong>{dataset.name}</strong>
                      <small className="hp-mono">
                        {dataset.id}
                      </small>
                    </td>

                    <td>{dataset.dataset_type || '—'}</td>

                    <td>{dataset.sample_count ?? 0}</td>

                    <td>{dataset.num_classes ?? 0}</td>

                    <td>
                      <span
                        className={statusClass(
                          dataset.is_active
                            ? 'ACTIVE'
                            : 'INACTIVE',
                        )}
                      >
                        {dataset.is_active
                          ? 'ACTIVE'
                          : 'INACTIVE'}
                      </span>
                    </td>

                    <td>
                      <div className="hp-table-actions">
                        <button
                          className="hp-small-button"
                          onClick={() =>
                            loadVersions(dataset)
                          }
                        >
                          VERSIONS
                        </button>

                        <button
                          className="hp-small-button"
                          onClick={() =>
                            beginEdit(dataset)
                          }
                        >
                          EDIT
                        </button>

                        <button
                          className="hp-small-button"
                          onClick={() =>
                            toggleDataset(dataset)
                          }
                          disabled={busy}
                        >
                          {dataset.is_active
                            ? 'DEACTIVATE'
                            : 'ACTIVATE'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedDataset && (
        <section className="hp-card">
          <SectionTitle
            eyebrow="DATASET VERSION"
            title={selectedDataset.name}
            description={`Version management for ${selectedDataset.id}`}
            action={
              <button
                className="hp-small-button"
                onClick={() => setSelectedDataset(null)}
              >
                CLOSE
              </button>
            }
          />

          <div className="hp-grid-2">
            <div>
              <h3 className="hp-subtitle">Existing versions</h3>

              {loadingVersions ? (
                <div className="hp-loading-small">
                  <RefreshCw
                    size={17}
                    className="hp-spin"
                  />
                  Loading versions...
                </div>
              ) : versions.length === 0 ? (
                <EmptyModule
                  icon={Layers3}
                  title="No versions"
                  description="Upload the first version for this dataset."
                />
              ) : (
                <div className="hp-version-list">
                  {versions.map((version) => (
                    <div
                      className="hp-version"
                      key={version.id}
                    >
                      <div>
                        <strong>
                          {version.version}
                        </strong>
                        <span>
                          {version.sample_count ?? 0}{' '}
                          samples
                        </span>
                      </div>

                      <div>
                        <small>
                          {formatDate(
                            version.created_at,
                          )}
                        </small>

                        <small className="hp-mono">
                          {version.fingerprint ||
                            'No fingerprint'}
                        </small>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="hp-form" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ display: 'flex', gap: 8, borderBottom: '1px solid var(--hp-border)', paddingBottom: 10 }}>
                <button
                  type="button"
                  className={ingestMode === 'upload' ? 'hp-button hp-button-primary' : 'hp-small-button'}
                  onClick={() => setIngestMode('upload')}
                  style={{ display: 'flex', alignItems: 'center', gap: 6 }}
                >
                  <Upload size={14} />
                  UPLOAD FILE (.NPZ)
                </button>
                <button
                  type="button"
                  className={ingestMode === 'link' ? 'hp-button hp-button-primary' : 'hp-small-button'}
                  onClick={() => setIngestMode('link')}
                  style={{ display: 'flex', alignItems: 'center', gap: 6 }}
                >
                  <Link2 size={14} />
                  LINK RECORD URL / PATH
                </button>
              </div>

              {ingestMode === 'upload' ? (
                <form className="hp-form" onSubmit={uploadVersion}>
                  <h3 className="hp-subtitle">Upload Local Dataset (.npz)</h3>
                  <label>
                    VERSION
                    <input
                      value={versionName}
                      onChange={(event) => setVersionName(event.target.value)}
                      pattern="[A-Za-z0-9._-]+"
                      required
                    />
                  </label>
                  <label>
                    DATASET FILE
                    <input
                      type="file"
                      onChange={(event) => setVersionFile(event.target.files?.[0] || null)}
                      required
                    />
                  </label>
                  <div className="hp-file-boundary">
                    <Lock size={16} />
                    <span>Uploaded artifacts remain strictly within the hospital dataset boundary.</span>
                  </div>
                  <button className="hp-button hp-button-primary" disabled={busy || !versionFile}>
                    <Upload size={15} />
                    {busy ? 'UPLOADING...' : 'UPLOAD & VALIDATE'}
                  </button>
                </form>
              ) : (
                <form className="hp-form" onSubmit={linkVersion}>
                  <h3 className="hp-subtitle">Ingest & Register from Record Link / Path</h3>
                  <label>
                    VERSION
                    <input
                      value={versionName}
                      onChange={(event) => setVersionName(event.target.value)}
                      pattern="[A-Za-z0-9._-]+"
                      placeholder="e.g. v2-ehr"
                      required
                    />
                  </label>
                  <label>
                    RECORD LINK / PATH / URL
                    <input
                      value={recordLink}
                      onChange={(e) => setRecordLink(e.target.value)}
                      placeholder="e.g. data/mnist/hospital_h21.npz or https://... or demo://synthetic"
                      required
                    />
                  </label>
                  <label>
                    DATA FORMAT
                    <select value={recordFormat} onChange={(e) => setRecordFormat(e.target.value)}>
                      <option value="AUTO">AUTO-DETECT (NPZ / CSV)</option>
                      <option value="NPZ">NPZ TENSOR ARCHIVE</option>
                      <option value="CSV">CSV TABULAR PIXELS</option>
                    </select>
                  </label>
                  <div className="hp-file-boundary">
                    <Lock size={16} />
                    <span>External records are retrieved into the hospital local boundary and hashed. Patient records never leave enclave.</span>
                  </div>
                  <button className="hp-button hp-button-primary" disabled={busy || !recordLink.trim()}>
                    <Database size={15} />
                    {busy ? 'PROCESSING RECORDS...' : 'PROCESS & REGISTER RECORDS'}
                  </button>
                </form>
              )}
            </div>
          </div>
        </section>
      )}

      {showCreate && (
        <div className="hp-modal-backdrop">
          <form
            className="hp-modal"
            onSubmit={createDataset}
          >
            <div className="hp-modal-head">
              <div>
                <div className="hp-eyebrow">DATA</div>
                <h2>Create dataset</h2>
              </div>

              <button
                type="button"
                className="hp-icon-button"
                onClick={() => setShowCreate(false)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="hp-form">
              <label>
                DATASET NAME
                <input
                  value={createForm.name}
                  onChange={(event) =>
                    setCreateForm({
                      ...createForm,
                      name: event.target.value,
                    })
                  }
                  placeholder="e.g. H21 Chest X-Ray"
                  required
                />
              </label>

              <label>
                DATASET TYPE
                <select
                  value={createForm.dataset_type}
                  onChange={(event) =>
                    setCreateForm({
                      ...createForm,
                      dataset_type:
                        event.target.value,
                    })
                  }
                >
                  <option value="IMAGE_CLASSIFICATION">
                    IMAGE_CLASSIFICATION
                  </option>
                  <option value="TABULAR">
                    TABULAR
                  </option>
                  <option value="TEXT">
                    TEXT
                  </option>
                  <option value="OTHER">
                    OTHER
                  </option>
                </select>
              </label>

              <div className="hp-form-grid">
                <label>
                  SAMPLE COUNT
                  <input
                    type="number"
                    min="0"
                    value={createForm.sample_count}
                    onChange={(event) =>
                      setCreateForm({
                        ...createForm,
                        sample_count:
                          event.target.value,
                      })
                    }
                  />
                </label>

                <label>
                  NUMBER OF CLASSES
                  <input
                    type="number"
                    min="1"
                    value={createForm.num_classes}
                    onChange={(event) =>
                      setCreateForm({
                        ...createForm,
                        num_classes:
                          event.target.value,
                      })
                    }
                  />
                </label>
              </div>
            </div>

            <div className="hp-modal-actions">
              <button
                type="button"
                className="hp-button hp-button-secondary"
                onClick={() => setShowCreate(false)}
              >
                CANCEL
              </button>

              <button
                className="hp-button hp-button-primary"
                disabled={busy}
              >
                <Save size={15} />
                {busy ? 'CREATING...' : 'CREATE DATASET'}
              </button>
            </div>
          </form>
        </div>
      )}

      {editing && (
        <div className="hp-modal-backdrop">
          <form
            className="hp-modal"
            onSubmit={updateDataset}
          >
            <div className="hp-modal-head">
              <div>
                <div className="hp-eyebrow">
                  DATASET / EDIT
                </div>
                <h2>Update dataset</h2>
              </div>

              <button
                type="button"
                className="hp-icon-button"
                onClick={() => setEditing(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="hp-form">
              <label>
                DATASET NAME
                <input
                  value={editForm.name}
                  onChange={(event) =>
                    setEditForm({
                      ...editForm,
                      name: event.target.value,
                    })
                  }
                  required
                />
              </label>

              <label>
                DATASET TYPE
                <input
                  value={editForm.dataset_type}
                  onChange={(event) =>
                    setEditForm({
                      ...editForm,
                      dataset_type:
                        event.target.value,
                    })
                  }
                  required
                />
              </label>

              <div className="hp-form-grid">
                <label>
                  SAMPLE COUNT
                  <input
                    type="number"
                    min="0"
                    value={editForm.sample_count}
                    onChange={(event) =>
                      setEditForm({
                        ...editForm,
                        sample_count:
                          event.target.value,
                      })
                    }
                  />
                </label>

                <label>
                  NUMBER OF CLASSES
                  <input
                    type="number"
                    min="1"
                    value={editForm.num_classes}
                    onChange={(event) =>
                      setEditForm({
                        ...editForm,
                        num_classes:
                          event.target.value,
                      })
                    }
                  />
                </label>
              </div>
            </div>

            <div className="hp-modal-actions">
              <button
                type="button"
                className="hp-button hp-button-secondary"
                onClick={() => setEditing(null)}
              >
                CANCEL
              </button>

              <button
                className="hp-button hp-button-primary"
                disabled={busy}
              >
                <Save size={15} />
                {busy ? 'SAVING...' : 'SAVE CHANGES'}
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  )
}

function DataQualityPage({ datasets }) {
  const active = datasets.filter(
    (dataset) => dataset.is_active,
  ).length

  const totalSamples = datasets.reduce(
    (sum, dataset) =>
      sum + Number(dataset.sample_count || 0),
    0,
  )

  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">DATA / QUALITY</div>
          <h1>Data Quality</h1>
          <p>
            Local dataset readiness indicators based on the metadata
            currently exposed by the backend.
          </p>
        </div>
      </div>

      <div className="hp-stat-grid">
        <PortalStat
          icon={Database}
          label="TOTAL DATASETS"
          value={datasets.length}
          detail="registered datasets"
        />

        <PortalStat
          icon={CheckCircle2}
          label="ACTIVE"
          value={active}
          detail="eligible for local workflows"
        />

        <PortalStat
          icon={BarChart3}
          label="TOTAL SAMPLES"
          value={totalSamples.toLocaleString()}
          detail="reported dataset samples"
        />

        <PortalStat
          icon={ShieldCheck}
          label="RAW DATA"
          value="LOCAL"
          detail="hospital boundary"
        />
      </div>

      <section className="hp-card">
        <SectionTitle
          eyebrow="QUALITY REGISTER"
          title="Dataset readiness"
        />

        <div className="hp-quality-list">
          {datasets.map((dataset) => (
            <div
              className="hp-quality-row"
              key={dataset.id}
            >
              <div>
                <strong>{dataset.name}</strong>
                <span>
                  {dataset.dataset_type || 'UNKNOWN'}
                </span>
              </div>

              <div>
                <span>Samples</span>
                <strong>
                  {dataset.sample_count ?? 0}
                </strong>
              </div>

              <div>
                <span>Classes</span>
                <strong>
                  {dataset.num_classes ?? 0}
                </strong>
              </div>

              <span
                className={statusClass(
                  dataset.is_active
                    ? 'VALIDATED ACTIVE'
                    : 'INACTIVE',
                )}
              >
                {dataset.is_active
                  ? 'READY'
                  : 'INACTIVE'}
              </span>
            </div>
          ))}
        </div>

        {!datasets.length && (
          <EmptyModule
            icon={BarChart3}
            title="No dataset metadata"
            description="Create and upload a dataset to begin local data preparation."
          />
        )}
      </section>
    </>
  )
}

function CurrentRoundPage({
  rounds,
  updates,
  onNavigate,
}) {
  const latestRound = rounds[0] || null

  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">
            FEDERATED LEARNING / ROUND
          </div>
          <h1>Current Round</h1>
          <p>
            Monitor the federation round before starting local
            training.
          </p>
        </div>
      </div>

      {!latestRound ? (
        <section className="hp-card">
          <EmptyModule
            icon={GitBranch}
            title="No current round"
            description="No federation round is currently available to this hospital."
          />
        </section>
      ) : (
        <>
          <div className="hp-grid-3">
            <PortalStat
              icon={GitBranch}
              label="ROUND"
              value={
                latestRound.round_number ?? '—'
              }
              detail={latestRound.status || 'UNKNOWN'}
            />

            <PortalStat
              icon={Users}
              label="PARTICIPANTS"
              value={
                latestRound.participating_clients ??
                '—'
              }
              detail="participating clients"
            />

            <PortalStat
              icon={Upload}
              label="YOUR UPDATES"
              value={updates.length}
              detail="visible model updates"
            />
          </div>

          <section className="hp-card">
            <SectionTitle
              eyebrow="ROUND STATE"
              title={`Federation Round ${
                latestRound.round_number ?? '—'
              }`}
            />

            <div className="hp-round-detail">
              <div className="hp-info-list">
                <InfoRow
                  label="Round ID"
                  value={latestRound.id}
                  mono
                />
                <InfoRow
                  label="Status"
                  value={latestRound.status}
                />
                <InfoRow
                  label="Started"
                  value={formatDate(
                    latestRound.started_at,
                  )}
                />
                <InfoRow
                  label="Accepted updates"
                  value={
                    latestRound.accepted_updates ?? 0
                  }
                />
                <InfoRow
                  label="Quarantined updates"
                  value={
                    latestRound.quarantined_updates ??
                    0
                  }
                />
              </div>

              <div className="hp-round-state">
                <Activity size={30} />
                <strong>
                  {latestRound.status || 'UNKNOWN'}
                </strong>
                <span>
                  Use Local Training when the round and dataset are
                  ready.
                </span>

                <button
                  className="hp-button hp-button-primary"
                  onClick={() =>
                    onNavigate('training')
                  }
                >
                  OPEN LOCAL TRAINING
                </button>
              </div>
            </div>
          </section>
        </>
      )}
    </>
  )
}

function LocalTrainingPage({
  token,
  datasets,
  rounds,
  onTrainingComplete,
  onNavigate,
}) {
  const [datasetId, setDatasetId] = useState('')
  const [version, setVersion] = useState('')
  const [versions, setVersions] = useState([])
  const [loadingVersions, setLoadingVersions] = useState(false)
  const [training, setTraining] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const latestRound = rounds[0] || null

  useEffect(() => {
    if (!datasetId) {
      setVersions([])
      setVersion('')
      return
    }

    let cancelled = false

    async function load() {
      setLoadingVersions(true)
      setError('')

      try {
        const response = await hospitalFetch(
          `/api/v1/hospital/datasets/${datasetId}/versions`,
          token,
        )

        if (cancelled) return

        const items = hospitalArray(response)
        setVersions(items)

        if (items[0]?.version) {
          setVersion(items[0].version)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message)
          setVersions([])
        }
      } finally {
        if (!cancelled) {
          setLoadingVersions(false)
        }
      }
    }

    load()

    return () => {
      cancelled = true
    }
  }, [datasetId, token])

  async function runTraining(event) {
    event.preventDefault()

    setError('')
    setResult(null)

    if (!latestRound?.id) {
      setError('No federation round is currently available.')
      return
    }

    if (!datasetId) {
      setError('Select a dataset.')
      return
    }

    if (!version) {
      setError('Select a verified dataset version.')
      return
    }

    setTraining(true)

    try {
      const response = await hospitalFetch(
        '/api/v1/hospital/training',
        token,
        {
          method: 'POST',
          body: JSON.stringify({
            round_id: latestRound.id,
            federation_id:
              HOSPITAL_FEDERATION_ID,
            dataset_id: datasetId,
            dataset_version: version,
          }),
        },
      )

      setResult(response)
      onTrainingComplete?.(response)
    } catch (err) {
      if (err.message === 'SESSION_EXPIRED') {
        throw err
      }

      setError(err.message)
    } finally {
      setTraining(false)
    }
  }

  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">
            FEDERATED LEARNING / LOCAL
          </div>
          <h1>Local Training</h1>
          <p>
            Train locally and submit a model update without sending
            raw hospital data to the federation.
          </p>
        </div>
      </div>

      <section className="hp-card hp-training-banner">
        <div className="hp-training-icon">
          <Workflow size={25} />
        </div>

        <div>
          <div className="hp-eyebrow">
            PRIVACY-PRESERVING TRAINING
          </div>

          <h2>Prepare ? Train ? Submit ? Track</h2>

          <p>
            The backend loads the latest server-verified global model,
            trains against your selected local dataset, creates the
            model update artifact and records its security lifecycle.
          </p>
        </div>
      </section>

      {error && (
        <div className="hp-notice hp-notice-danger">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="hp-grid-2">
        <form
          className="hp-card hp-form"
          onSubmit={runTraining}
        >
          <SectionTitle
            eyebrow="TRAINING INPUT"
            title="Select local data"
          />

          <label>
            FEDERATION ROUND
            <select
              value={latestRound?.id || ''}
              disabled
            >
              <option value="">
                {latestRound
                  ? `Round ${
                      latestRound.round_number ??
                      '—'
                    } · ${
                      latestRound.status || 'UNKNOWN'
                    }`
                  : 'No round available'}
              </option>
            </select>
          </label>

          <label>
            DATASET
            <select
              value={datasetId}
              onChange={(event) =>
                setDatasetId(event.target.value)
              }
              required
            >
              <option value="">
                Select active dataset
              </option>

              {datasets
                .filter((dataset) => dataset.is_active)
                .map((dataset) => (
                  <option
                    key={dataset.id}
                    value={dataset.id}
                  >
                    {dataset.name}
                  </option>
                ))}
            </select>
          </label>

          <label>
            DATASET VERSION
            <select
              value={version}
              onChange={(event) =>
                setVersion(event.target.value)
              }
              disabled={
                !datasetId ||
                loadingVersions ||
                versions.length === 0
              }
              required
            >
              <option value="">
                {loadingVersions
                  ? 'Loading versions...'
                  : 'Select version'}
              </option>

              {versions.map((item) => (
                <option
                  key={item.id}
                  value={item.version}
                >
                  {item.version} ·{' '}
                  {item.sample_count ?? 0} samples
                </option>
              ))}
            </select>
          </label>

          <div className="hp-file-boundary">
            <Lock size={17} />
            <span>
              Raw hospital data stays local. The training API submits
              the resulting model update, not the raw dataset.
            </span>
          </div>

          <button
            className="hp-button hp-button-primary hp-button-large"
            disabled={
              training ||
              !latestRound?.id ||
              !datasetId ||
              !version
            }
          >
            <Workflow size={16} />
            {training
              ? 'TRAINING LOCALLY...'
              : 'START LOCAL TRAINING'}
          </button>
        </form>

        <section className="hp-card">
          <SectionTitle
            eyebrow="SECURITY PIPELINE"
            title="What happens next?"
          />

          <div className="hp-step-list">
            {[
              [
                'LOCAL TRAIN',
                'PyTorch training runs against the hospital dataset.',
              ],
              [
                'ARTIFACT',
                'A model delta is persisted as a SafeTensors artifact.',
              ],
              [
                'INTEGRITY',
                'The artifact receives a cryptographic fingerprint.',
              ],
              [
                'SECURITY',
                'FedSentinel evaluates the submitted update.',
              ],
              [
                'DECISION',
                'The update may be accepted, reviewed or quarantined.',
              ],
            ].map(([title, text], index) => (
              <div
                className="hp-step"
                key={title}
              >
                <span>{String(index + 1).padStart(2, '0')}</span>

                <div>
                  <strong>{title}</strong>
                  <p>{text}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      {result && (
        <section className="hp-card hp-training-result">
          <SectionTitle
            eyebrow="TRAINING COMPLETE"
            title="Model update generated"
          />

          <div className="hp-grid-3">
            <InfoRow
              label="Update ID"
              value={result.update_id}
              mono
            />

            <InfoRow
              label="Examples"
              value={result.num_examples}
            />

            <InfoRow
              label="Epochs"
              value={result.epochs_completed}
            />

            <InfoRow
              label="Training loss"
              value={
                result.training_loss === undefined
                  ? '—'
                  : Number(
                      result.training_loss,
                    ).toFixed(6)
              }
            />

            <InfoRow
              label="Artifact type"
              value={result.artifact_type}
            />

            <InfoRow
              label="Artifact size"
              value={formatBytes(
                result.artifact_size,
              )}
            />
          </div>

          <div className="hp-artifact">
            <div>
              <span>ARTIFACT HASH</span>
              <strong className="hp-mono">
                {result.artifact_hash || '—'}
              </strong>
            </div>

            <div>
              <span>SECURITY STATUS</span>
              <strong className={statusClass(
                result.security_status,
              )}>
                {result.security_status || 'PENDING'}
              </strong>
            </div>

            <div>
              <span>ACTION</span>
              <strong>
                {result.action || '—'}
              </strong>
            </div>
          </div>

          <div className="hp-notice hp-notice-info">
            <CheckCircle2 size={18} />
            <div>
              <strong>
                Update submitted to the FedSentinel pipeline.
              </strong>
              <p>
                {result.message ||
                  'The update is now subject to the configured security workflow.'}
              </p>
            </div>
          </div>

          <button
            className="hp-link-button"
            onClick={() => onNavigate('updates')}
          >
            View model updates
            <ChevronRight size={15} />
          </button>
        </section>
      )}
    </>
  )
}

function ModelUpdatesPage({
  updates,
  loading,
  onRefresh,
}) {
  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">
            FEDERATED LEARNING / UPDATES
          </div>
          <h1>Model Updates</h1>
          <p>
            Hospital-visible model update and security lifecycle
            information.
          </p>
        </div>

        <button
          className="hp-button hp-button-secondary"
          onClick={onRefresh}
        >
          <RefreshCw size={15} />
          REFRESH
        </button>
      </div>

      <section className="hp-card">
        <SectionTitle
          eyebrow="UPDATE REGISTER"
          title="Hospital-visible updates"
        />

        {loading ? (
          <div className="hp-loading-small">
            <RefreshCw
              size={17}
              className="hp-spin"
            />
            Synchronizing update telemetry...
          </div>
        ) : updates.length === 0 ? (
          <EmptyModule
            icon={Upload}
            title="No visible model updates"
            description="Submitted updates may appear here when the backend exposes them to the hospital role."
          />
        ) : (
          <div className="hp-table-wrap">
            <table className="hp-table">
              <thead>
                <tr>
                  <th>UPDATE</th>
                  <th>ROUND</th>
                  <th>STATUS</th>
                  <th>ACTION</th>
                  <th>SUBMITTED</th>
                </tr>
              </thead>

              <tbody>
                {updates.map((update) => (
                  <tr key={update.id || update.update_id}>
                    <td>
                      <strong className="hp-mono">
                        {update.id ||
                          update.update_id ||
                          '—'}
                      </strong>
                    </td>

                    <td>
                      {update.round_id || '—'}
                    </td>

                    <td>
                      <span
                        className={statusClass(
                          update.security_status ||
                            update.status,
                        )}
                      >
                        {update.security_status ||
                          update.status ||
                          'PENDING'}
                      </span>
                    </td>

                    <td>
                      {update.action || '—'}
                    </td>

                    <td>
                      {formatDate(
                        update.submitted_at ||
                          update.created_at,
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="hp-card">
        <div className="hp-notice hp-notice-info">
          <Info size={18} />
          <div>
            <strong>Security decisions remain distinct.</strong>
            <p>
              An update being quarantined means the update requires
              security handling. It does not by itself mean that the
              hospital has been declared malicious.
            </p>
          </div>
        </div>
      </section>
    </>
  )
}

function GlobalModelPage({ rounds }) {
  const latestRound = rounds[0] || null

  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">
            FEDERATED LEARNING / MODEL
          </div>
          <h1>Global Model</h1>
          <p>
            Verified global-model context available through the
            current federation state.
          </p>
        </div>
      </div>

      <section className="hp-card">
        <SectionTitle
          eyebrow="VERIFIED MODEL CONTEXT"
          title="Global model"
        />

        <div className="hp-notice hp-notice-info">
          <Globe2 size={19} />
          <div>
            <strong>
              Model publication is controlled by the federation
              security pipeline.
            </strong>
            <p>
              The current hospital API does not expose a dedicated
              hospital global-model download endpoint. The portal
              therefore does not invent a model file or download URL.
              The latest round context is shown below.
            </p>
          </div>
        </div>

        <div className="hp-info-list hp-model-context">
          <InfoRow
            label="Latest round"
            value={
              latestRound?.round_number ?? '—'
            }
          />

          <InfoRow
            label="Round status"
            value={
              latestRound?.status || '—'
            }
          />

          <InfoRow
            label="Accepted updates"
            value={
              latestRound?.accepted_updates ?? 0
            }
          />

          <InfoRow
            label="Quarantined updates"
            value={
              latestRound?.quarantined_updates ?? 0
            }
          />
        </div>
      </section>
    </>
  )
}

function SecurityPage({
  dashboard,
  status,
  securityRound,
}) {
  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">
            SECURITY / POSTURE
          </div>
          <h1>Security Status</h1>
          <p>
            Hospital-visible security posture and federation
            eligibility.
          </p>
        </div>
      </div>

      <div className="hp-grid-3">
        <PortalStat
          icon={ShieldCheck}
          label="SECURITY"
          value={status?.security_status || 'UNKNOWN'}
          detail="hospital posture"
        />

        <PortalStat
          icon={Shield}
          label="ELIGIBILITY"
          value={
            status?.is_eligible
              ? 'ELIGIBLE'
              : 'NOT ELIGIBLE'
          }
          detail="federation eligibility"
        />

        <PortalStat
          icon={AlertTriangle}
          label="INCIDENTS"
          value={dashboard?.open_incidents ?? 0}
          detail="open incidents"
        />
      </div>

      <section className="hp-card">
        <SectionTitle
          eyebrow="SECURITY BOUNDARY"
          title="Hospital security posture"
        />

        <div className="hp-security-matrix">
          <div>
            <ShieldCheck size={21} />
            <strong>Hospital status</strong>
            <span>
              {status?.status || 'UNKNOWN'}
            </span>
          </div>

          <div>
            <ShieldAlert size={21} />
            <strong>Security status</strong>
            <span>
              {status?.security_status || 'UNKNOWN'}
            </span>
          </div>

          <div>
            <Network size={21} />
            <strong>Federation</strong>
            <span>
              {status?.federation_member
                ? status?.membership_status ||
                  'MEMBER'
                : 'NOT A MEMBER'}
            </span>
          </div>

          <div>
            <CheckCircle2 size={21} />
            <strong>Eligibility</strong>
            <span>
              {status?.is_eligible
                ? 'ELIGIBLE'
                : 'NOT ELIGIBLE'}
            </span>
          </div>
        </div>
      </section>

      {securityRound && (
        <section className="hp-card">
          <SectionTitle
            eyebrow="SECURITY ROUND"
            title="Latest security context"
          />

          <pre className="hp-json">
            {JSON.stringify(
              securityRound,
              null,
              2,
            )}
          </pre>
        </section>
      )}
    </>
  )
}

function IncidentsPage({ incidents }) {
  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">
            SECURITY / INCIDENTS
          </div>
          <h1>Incidents</h1>
          <p>
            Security incidents visible to this hospital session.
          </p>
        </div>
      </div>

      <section className="hp-card">
        {incidents.length === 0 ? (
          <EmptyModule
            icon={ShieldCheck}
            title="No hospital-visible incidents"
            description="No incident records are currently visible to this hospital session."
          />
        ) : (
          <div className="hp-incident-list">
            {incidents.map((incident) => (
              <div
                className="hp-incident"
                key={incident.id}
              >
                <div className="hp-incident-icon">
                  <AlertTriangle size={19} />
                </div>

                <div>
                  <strong>
                    {incident.title ||
                      incident.threat ||
                      incident.reason ||
                      'Security incident'}
                  </strong>

                  <span>
                    {incident.description ||
                      incident.message ||
                      'Security event recorded by FedSentinel.'}
                  </span>

                  <small>
                    {incident.id || 'Incident'} ·{' '}
                    {formatDate(
                      incident.created_at ||
                        incident.detected_at,
                    )}
                  </small>
                </div>

                <span
                  className={statusClass(
                    incident.severity ||
                      incident.status,
                  )}
                >
                  {incident.severity ||
                    incident.status ||
                    'OPEN'}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="hp-card">
        <div className="hp-notice hp-notice-info">
          <Info size={18} />
          <div>
            <strong>Incident interpretation</strong>
            <p>
              Security incidents describe model/security evidence and
              actions. They should not be interpreted as a blanket
              declaration that the hospital itself is malicious.
            </p>
          </div>
        </div>
      </section>
    </>
  )
}

function TrustPage({ dashboard, trustRecords }) {
  const trustScore =
    dashboard?.trust_score === null ||
    dashboard?.trust_score === undefined
      ? null
      : Number(dashboard.trust_score)

  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">
            SECURITY / TRUST
          </div>
          <h1>Trust</h1>
          <p>
            Hospital-visible trust information and security decision
            context.
          </p>
        </div>
      </div>

      <section className="hp-card">
        <SectionTitle
          eyebrow="CURRENT TRUST"
          title="Hospital trust state"
        />

        <div className="hp-trust-large">
          <div className="hp-trust-number">
            {trustScore === null
              ? '—'
              : trustScore.toFixed(1)}
          </div>

          <div>
            <strong>
              {dashboard?.trust_status ||
                'Trust evaluation pending'}
            </strong>

            <p>
              The displayed value is sourced from the backend hospital
              dashboard. The hospital UI does not manufacture a trust
              score.
            </p>
          </div>
        </div>
      </section>

      <section className="hp-card">
        <SectionTitle
          eyebrow="TRUST RECORDS"
          title="Available trust evidence"
        />

        {trustRecords.length === 0 ? (
          <EmptyModule
            icon={Gauge}
            title="No detailed trust records"
            description="Detailed trust records are not currently exposed to this hospital session."
          />
        ) : (
          <div className="hp-table-wrap">
            <table className="hp-table">
              <thead>
                <tr>
                  <th>HOSPITAL</th>
                  <th>STATUS</th>
                  <th>RISK</th>
                  <th>TRUST</th>
                  <th>ROUND</th>
                </tr>
              </thead>

              <tbody>
                {trustRecords.map((record) => (
                  <tr key={record.id}>
                    <td>
                      {record.hospital_id || '—'}
                    </td>

                    <td>
                      {record.status ||
                        record.trust_status ||
                        '—'}
                    </td>

                    <td>
                      {record.risk_score ??
                        record.risk ??
                        '—'}
                    </td>

                    <td>
                      {record.trust_score ??
                        record.score ??
                        '—'}
                    </td>

                    <td>
                      {record.round_id || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  )
}

function ReportsPage({
  hospital,
  dashboard,
  datasets,
  rounds,
  updates,
}) {
  function downloadTrainingReport() {
    const rows = [
      {
        hospital: hospital?.code || '',
        hospital_name: hospital?.name || '',
        total_datasets:
          dashboard?.total_datasets ?? 0,
        active_datasets:
          dashboard?.active_datasets ?? 0,
        total_updates:
          dashboard?.total_updates ?? 0,
        accepted_updates:
          dashboard?.accepted_updates ?? 0,
        quarantined_updates:
          dashboard?.quarantined_updates ?? 0,
        open_incidents:
          dashboard?.open_incidents ?? 0,
        trust_score:
          dashboard?.trust_score ?? '',
      },
    ]

    downloadText(
      `fedsentinel-${hospital?.code || 'hospital'}-training-report.csv`,
      toCsv(rows),
      'text/csv;charset=utf-8',
    )
  }

  function downloadDatasetReport() {
    const rows = datasets.map((dataset) => ({
      id: dataset.id,
      name: dataset.name,
      dataset_type: dataset.dataset_type,
      sample_count: dataset.sample_count,
      num_classes: dataset.num_classes,
      is_active: dataset.is_active,
      created_at: dataset.created_at,
    }))

    downloadText(
      `fedsentinel-${hospital?.code || 'hospital'}-datasets.csv`,
      toCsv(rows),
      'text/csv;charset=utf-8',
    )
  }

  function downloadRoundReport() {
    const rows = rounds.map((round) => ({
      id: round.id,
      round_number: round.round_number,
      status: round.status,
      participating_clients:
        round.participating_clients,
      accepted_updates:
        round.accepted_updates,
      quarantined_updates:
        round.quarantined_updates,
      started_at: round.started_at,
    }))

    downloadText(
      `fedsentinel-${hospital?.code || 'hospital'}-participation.csv`,
      toCsv(rows),
      'text/csv;charset=utf-8',
    )
  }

  function downloadUpdateReport() {
    const rows = updates.map((update) => ({
      id: update.id || update.update_id,
      round_id: update.round_id,
      status:
        update.security_status ||
        update.status,
      action: update.action,
      submitted_at:
        update.submitted_at ||
        update.created_at,
    }))

    downloadText(
      `fedsentinel-${hospital?.code || 'hospital'}-updates.csv`,
      toCsv(rows),
      'text/csv;charset=utf-8',
    )
  }

  const reports = [
    {
      icon: Workflow,
      title: 'Training Report',
      description:
        'Current hospital training and update counters.',
      action: downloadTrainingReport,
    },
    {
      icon: Database,
      title: 'Dataset Report',
      description:
        'CSV export of current hospital dataset metadata.',
      action: downloadDatasetReport,
    },
    {
      icon: GitBranch,
      title: 'Participation Report',
      description:
        'CSV export of visible federation rounds.',
      action: downloadRoundReport,
    },
    {
      icon: Shield,
      title: 'Model Update Report',
      description:
        'CSV export of visible model update metadata.',
      action: downloadUpdateReport,
    },
  ]

  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">
            REPORTS / EXPORTS
          </div>
          <h1>Reports & Exports</h1>
          <p>
            Generate local CSV reports from data already visible to
            this authenticated hospital session.
          </p>
        </div>
      </div>

      <div className="hp-grid-2">
        {reports.map((report) => {
          const Icon = report.icon

          return (
            <section
              className="hp-card hp-report-card"
              key={report.title}
            >
              <div className="hp-report-icon">
                <Icon size={23} />
              </div>

              <h2>{report.title}</h2>

              <p>{report.description}</p>

              <button
                className="hp-button hp-button-secondary"
                onClick={report.action}
              >
                <Download size={15} />
                DOWNLOAD CSV
              </button>
            </section>
          )
        })}
      </div>

      <section className="hp-card">
        <div className="hp-notice hp-notice-info">
          <Info size={18} />
          <div>
            <strong>Export boundary</strong>
            <p>
              These browser-generated reports contain only metadata
              already returned by the hospital APIs. They do not
              export patient records or raw hospital datasets.
            </p>
          </div>
        </div>
      </section>
    </>
  )
}

function AuditPage({ rounds, updates }) {
  const events = [
    ...rounds.map((round) => ({
      type: 'ROUND',
      title: `Round ${round.round_number ?? '—'} · ${
        round.status || 'UNKNOWN'
      }`,
      detail: round.id,
      time: round.started_at,
    })),
    ...updates.map((update) => ({
      type: 'UPDATE',
      title: 'Model update',
      detail:
        update.id ||
        update.update_id ||
        'Update',
      time:
        update.submitted_at ||
        update.created_at,
    })),
  ].sort(
    (a, b) =>
      new Date(b.time || 0) -
      new Date(a.time || 0),
  )

  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">
            SYSTEM / AUDIT
          </div>
          <h1>Audit Activity</h1>
          <p>
            Hospital-visible activity assembled from available
            federation and update telemetry.
          </p>
        </div>
      </div>

      <section className="hp-card">
        {events.length === 0 ? (
          <EmptyModule
            icon={FileClock}
            title="No visible activity"
            description="No federation or update activity is currently available to this session."
          />
        ) : (
          <div className="hp-timeline">
            {events.map((event, index) => (
              <div
                className="hp-timeline-item"
                key={`${event.type}-${event.detail}-${index}`}
              >
                <div className="hp-timeline-dot" />

                <div>
                  <span>{event.type}</span>
                  <strong>{event.title}</strong>
                  <small className="hp-mono">
                    {event.detail}
                  </small>
                  <small>
                    {formatDate(event.time)}
                  </small>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  )
}

function SettingsPage({ hospital, onLogout }) {
  return (
    <>
      <div className="hp-page-head">
        <div>
          <div className="hp-eyebrow">
            SYSTEM / SETTINGS
          </div>
          <h1>Settings</h1>
          <p>
            Hospital portal configuration and privacy controls.
          </p>
        </div>
      </div>

      <section className="hp-card">
        <SectionTitle
          eyebrow="SESSION"
          title="Hospital session"
        />

        <div className="hp-info-list">
          <InfoRow
            label="Hospital"
            value={hospital?.name}
          />

          <InfoRow
            label="Hospital code"
            value={hospital?.code}
          />

          <InfoRow
            label="Hospital ID"
            value={hospital?.id}
            mono
          />
        </div>

        <button
          className="hp-button hp-button-danger"
          onClick={onLogout}
        >
          EXIT HOSPITAL PORTAL
        </button>
      </section>

      <section className="hp-card">
        <SectionTitle
          eyebrow="PRIVACY"
          title="Data boundary"
        />

        <div className="hp-grid-3">
          <div className="hp-feature">
            <Lock size={20} />
            <strong>Patient records</strong>
            <span>LOCAL ONLY</span>
          </div>

          <div className="hp-feature">
            <Database size={20} />
            <strong>Raw datasets</strong>
            <span>LOCAL ONLY</span>
          </div>

          <div className="hp-feature">
            <Upload size={20} />
            <strong>Model updates</strong>
            <span>SHARED WITH FEDERATION</span>
          </div>
        </div>
      </section>
    </>
  )
}

export default function HospitalPortal({
  token,
  onLogout,
}) {
  const [active, setActive] = useState('command')
  const [hospital, setHospital] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [status, setStatus] = useState(null)
  const [datasets, setDatasets] = useState([])
  const [rounds, setRounds] = useState([])
  const [updates, setUpdates] = useState([])
  const [incidents, setIncidents] = useState([])
  const [trustRecords, setTrustRecords] = useState([])
  const [securityRound, setSecurityRound] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')

  async function loadPortal(showRefresh = false) {
    if (showRefresh) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }

    setError('')

    try {
      const [
        hospitalResponse,
        dashboardResponse,
        statusResponse,
        datasetsResponse,
      ] = await Promise.all([
        hospitalFetch(
          '/api/v1/hospital/me',
          token,
        ),
        hospitalFetch(
          '/api/v1/hospital/dashboard',
          token,
        ),
        hospitalFetch(
          '/api/v1/hospital/status',
          token,
        ),
        hospitalFetch(
          '/api/v1/hospital/datasets',
          token,
        ),
      ])

      setHospital(
        hospitalResponse?.value ||
          hospitalResponse,
      )

      setDashboard(
        dashboardResponse?.value ||
          dashboardResponse,
      )

      setStatus(
        statusResponse?.value ||
          statusResponse,
      )

      setDatasets(
        hospitalArray(datasetsResponse),
      )

      let roundList = []
      try {
        const roundsRes = await hospitalFetch(
          `/api/v1/federations/${HOSPITAL_FEDERATION_ID}/rounds`,
          token,
        )
        roundList = hospitalArray(roundsRes)
      } catch (err) {
        console.warn('Failed to load federation rounds in hospital portal', err)
      }

      setRounds(roundList)

      const latestRound = roundList[0]

      let nextUpdates = []
      let nextIncidents = []
      let nextTrust = []
      let nextSecurity = null

      if (latestRound?.id) {
        try {
          const response =
            await hospitalFetch(
              `/api/v1/security/rounds/${latestRound.id}/updates`,
              token,
            )

          nextUpdates =
            hospitalArray(response)
        } catch {
          nextUpdates = []
        }

        try {
          const response =
            await hospitalFetch(
              `/api/v1/security/rounds/${latestRound.id}/incidents`,
              token,
            )

          nextIncidents =
            hospitalArray(response)
        } catch {
          nextIncidents = []
        }

        try {
          const response =
            await hospitalFetch(
              `/api/v1/security/rounds/${latestRound.id}/trust`,
              token,
            )

          nextTrust =
            hospitalArray(response)
        } catch {
          nextTrust = []
        }

        try {
          nextSecurity =
            await hospitalFetch(
              `/api/v1/security/rounds/${latestRound.id}`,
              token,
            )
        } catch {
          nextSecurity = null
        }
      }

      setUpdates(nextUpdates)
      setIncidents(nextIncidents)
      setTrustRecords(nextTrust)
      setSecurityRound(nextSecurity)

      const identity =
        hospitalResponse?.value ||
        hospitalResponse

      if (identity?.id) {
        localStorage.setItem(
          'fedsentinel_hospital_id',
          identity.id,
        )
      }
    } catch (err) {
      if (err.message === 'SESSION_EXPIRED') {
        onLogout()
        return
      }

      setError(
        err.message ||
          'Unable to load the hospital portal.',
      )
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadPortal()

    const interval = window.setInterval(
      () => loadPortal(true),
      10000,
    )

    return () => window.clearInterval(interval)
  }, [token])

  const navigation = [
    {
      label: 'COMMAND',
      items: [
        ['command', 'Hospital Command', Activity],
      ],
    },
    {
      label: 'HOSPITAL',
      items: [
        ['hospital', 'My Hospital', Hospital],
        ['federation', 'Federation', Network],
        ['team', 'Team & Access', Users],
      ],
    },
    {
      label: 'DATA',
      items: [
        ['datasets', 'Datasets', Database],
        ['quality', 'Data Quality', BarChart3],
      ],
    },
    {
      label: 'FEDERATED LEARNING',
      items: [
        ['round', 'Current Round', GitBranch],
        ['training', 'Local Training', Workflow],
        ['updates', 'Model Updates', Upload],
        ['global-model', 'Global Model', Globe2],
      ],
    },
    {
      label: 'SECURITY',
      items: [
        ['security', 'Security Status', ShieldCheck],
        ['incidents', 'Incidents', ShieldAlert],
        ['trust', 'Trust', Gauge],
      ],
    },
    {
      label: 'REPORTS',
      items: [
        ['reports', 'Reports & Exports', FileText],
      ],
    },
    {
      label: 'SYSTEM',
      items: [
        ['audit', 'Audit Activity', FileClock],
        ['settings', 'Settings', Settings],
      ],
    },
  ]

  const activeLabel =
    navigation
      .flatMap((group) => group.items)
      .find(([id]) => id === active)?.[1] ||
    'Hospital Command'

  function handleTrainingComplete() {
    loadPortal(true)
  }

  let page = null

  if (loading && !hospital) {
    page = (
      <div className="hp-loading-page">
        <RefreshCw
          size={28}
          className="hp-spin"
        />
        <strong>
          Synchronizing hospital control plane...
        </strong>
        <span>
          Loading authenticated hospital state from FedSentinel.
        </span>
      </div>
    )
  } else if (active === 'command') {
    page = (
      <HospitalCommand
        hospital={hospital}
        dashboard={dashboard}
        status={status}
        rounds={rounds}
        onNavigate={setActive}
        onRefresh={() => loadPortal(true)}
        refreshing={refreshing}
      />
    )
  } else if (active === 'hospital') {
    page = (
      <MyHospitalPage
        hospital={hospital}
        dashboard={dashboard}
        status={status}
        onNavigate={setActive}
      />
    )
  } else if (active === 'federation') {
    page = (
      <FederationPage
        rounds={rounds}
        dashboard={dashboard}
        status={status}
        onRefresh={() => loadPortal(true)}
      />
    )
  } else if (active === 'team') {
    page = <TeamAccessPage />
  } else if (active === 'datasets') {
    page = (
      <DatasetsPage
        token={token}
        datasets={datasets}
        selectedDataset={null}
        setSelectedDataset={() => {}}
        onReload={() => loadPortal(true)}
      />
    )
  } else if (active === 'quality') {
    page = <DataQualityPage datasets={datasets} />
  } else if (active === 'round') {
    page = (
      <CurrentRoundPage
        rounds={rounds}
        updates={updates}
        onNavigate={setActive}
      />
    )
  } else if (active === 'training') {
    page = (
      <LocalTrainingPage
        token={token}
        datasets={datasets}
        rounds={rounds}
        onTrainingComplete={handleTrainingComplete}
        onNavigate={setActive}
      />
    )
  } else if (active === 'updates') {
    page = (
      <ModelUpdatesPage
        updates={updates}
        loading={loading}
        onRefresh={() => loadPortal(true)}
      />
    )
  } else if (active === 'global-model') {
    page = <GlobalModelPage rounds={rounds} />
  } else if (active === 'security') {
    page = (
      <SecurityPage
        dashboard={dashboard}
        status={status}
        securityRound={securityRound}
      />
    )
  } else if (active === 'incidents') {
    page = <IncidentsPage incidents={incidents} />
  } else if (active === 'trust') {
    page = (
      <TrustPage
        dashboard={dashboard}
        trustRecords={trustRecords}
      />
    )
  } else if (active === 'reports') {
    page = (
      <ReportsPage
        hospital={hospital}
        dashboard={dashboard}
        datasets={datasets}
        rounds={rounds}
        updates={updates}
      />
    )
  } else if (active === 'audit') {
    page = (
      <AuditPage
        rounds={rounds}
        updates={updates}
      />
    )
  } else if (active === 'settings') {
    page = (
      <SettingsPage
        hospital={hospital}
        onLogout={onLogout}
      />
    )
  }

  return (
    <>
      <style>{`
        .hospital-full-portal {
          --hp-bg: #05080b;
          --hp-panel: #0a0f14;
          --hp-panel-2: #0d141b;
          --hp-border: rgba(148,163,184,.15);
          --hp-border-strong: rgba(148,163,184,.25);
          --hp-text: #e8eef5;
          --hp-muted: #82909f;
          --hp-dim: #536170;
          --hp-accent: #58d6ff;
          --hp-green: #65e6a2;
          --hp-yellow: #f0c86b;
          --hp-red: #ff6f7d;
          min-height: 100vh;
          background:
            radial-gradient(circle at 80% 0%, rgba(40,115,150,.10), transparent 32%),
            #05080b;
          color: var(--hp-text);
          display: flex;
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .hospital-full-portal *,
        .hospital-full-portal *::before,
        .hospital-full-portal *::after {
          box-sizing: border-box;
        }

        .hp-sidebar {
          width: 248px;
          flex: 0 0 248px;
          min-height: 100vh;
          position: sticky;
          top: 0;
          height: 100vh;
          overflow-y: auto;
          border-right: 1px solid var(--hp-border);
          background: rgba(5,9,13,.96);
          display: flex;
          flex-direction: column;
        }

        .hp-brand {
          padding: 22px 20px 18px;
          border-bottom: 1px solid var(--hp-border);
        }

        .hp-brand-lockup {
          display: flex;
          align-items: center;
          gap: 11px;
        }

        .hp-brand-mark {
          width: 34px;
          height: 34px;
          border: 1px solid rgba(88,214,255,.55);
          display: grid;
          place-items: center;
          color: var(--hp-accent);
          font-size: 12px;
          font-weight: 800;
          letter-spacing: .05em;
        }

        .hp-brand strong {
          display: block;
          font-size: 13px;
          letter-spacing: .13em;
        }

        .hp-brand span {
          display: block;
          color: var(--hp-muted);
          font-size: 9px;
          letter-spacing: .16em;
          margin-top: 3px;
        }

        .hp-identity {
          margin: 14px;
          padding: 14px;
          border: 1px solid var(--hp-border);
          background: rgba(255,255,255,.015);
        }

        .hp-identity-code {
          font-size: 13px;
          font-weight: 700;
          margin-top: 6px;
        }

        .hp-identity-name {
          color: var(--hp-muted);
          font-size: 11px;
          margin-top: 4px;
          line-height: 1.4;
        }

        .hp-online {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          margin-top: 11px;
          color: var(--hp-green);
          font-size: 9px;
          letter-spacing: .1em;
          text-transform: uppercase;
        }

        .hp-online::before {
          content: "";
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: currentColor;
          box-shadow: 0 0 10px currentColor;
        }

        .hp-nav {
          padding: 4px 10px 16px;
          flex: 1;
        }

        .hp-nav-group {
          margin-top: 13px;
        }

        .hp-nav-label {
          padding: 0 9px 6px;
          color: var(--hp-dim);
          font-size: 8px;
          letter-spacing: .18em;
          font-weight: 700;
        }

        .hp-nav-item {
          width: 100%;
          border: 0;
          background: transparent;
          color: var(--hp-muted);
          padding: 9px 10px;
          display: flex;
          align-items: center;
          gap: 9px;
          text-align: left;
          cursor: pointer;
          font-size: 11px;
          border-left: 2px solid transparent;
          transition: .15s ease;
        }

        .hp-nav-item:hover {
          background: rgba(255,255,255,.035);
          color: var(--hp-text);
        }

        .hp-nav-item.active {
          background: rgba(88,214,255,.07);
          color: var(--hp-accent);
          border-left-color: var(--hp-accent);
        }

        .hp-sidebar-bottom {
          padding: 14px;
          border-top: 1px solid var(--hp-border);
        }

        .hp-privacy-mini {
          border: 1px solid var(--hp-border);
          padding: 11px;
          margin-bottom: 10px;
        }

        .hp-privacy-mini strong {
          display: block;
          font-size: 8px;
          letter-spacing: .14em;
          color: var(--hp-accent);
        }

        .hp-privacy-mini span {
          display: block;
          font-size: 10px;
          color: var(--hp-muted);
          line-height: 1.5;
          margin-top: 6px;
        }

        .hp-exit {
          width: 100%;
          border: 1px solid var(--hp-border);
          background: transparent;
          color: var(--hp-muted);
          padding: 9px;
          cursor: pointer;
          font-size: 9px;
          letter-spacing: .1em;
        }

        .hp-exit:hover {
          color: var(--hp-red);
          border-color: rgba(255,111,125,.35);
        }

        .hp-main {
          flex: 1;
          min-width: 0;
          padding: 32px 36px 60px;
          overflow-x: hidden;
        }

        .hp-page-head {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 20px;
          margin-bottom: 24px;
        }

        .hp-page-head h1 {
          margin: 5px 0 6px;
          font-size: 30px;
          line-height: 1.1;
          letter-spacing: -.025em;
          color: #f4f8fb;
        }

        .hp-page-head p {
          margin: 0;
          color: var(--hp-muted);
          font-size: 13px;
          line-height: 1.6;
        }

        .hp-eyebrow {
          color: var(--hp-accent);
          font-size: 8px;
          letter-spacing: .18em;
          font-weight: 800;
          text-transform: uppercase;
        }

        .hp-card {
          background: linear-gradient(180deg, rgba(12,18,24,.96), rgba(7,11,15,.96));
          border: 1px solid var(--hp-border);
          padding: 23px;
          margin-top: 18px;
          min-width: 0;
        }

        .hp-section-title {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 20px;
          margin-bottom: 20px;
        }

        .hp-section-title h2 {
          margin: 5px 0 4px;
          font-size: 17px;
          letter-spacing: -.01em;
        }

        .hp-section-title p {
          margin: 0;
          color: var(--hp-muted);
          font-size: 11px;
          line-height: 1.55;
        }

        .hp-hero {
          margin-top: 0;
          padding: 25px;
          border: 1px solid rgba(88,214,255,.16);
          background:
            linear-gradient(120deg, rgba(88,214,255,.065), transparent 55%),
            rgba(10,15,20,.95);
          display: flex;
          justify-content: space-between;
          gap: 20px;
          align-items: center;
        }

        .hp-hero-main {
          display: flex;
          gap: 15px;
          align-items: center;
        }

        .hp-hero-icon {
          width: 54px;
          height: 54px;
          display: grid;
          place-items: center;
          border: 1px solid rgba(88,214,255,.25);
          color: var(--hp-accent);
          background: rgba(88,214,255,.05);
        }

        .hp-hero h2 {
          margin: 5px 0 4px;
          font-size: 22px;
        }

        .hp-hero p {
          margin: 0;
          color: var(--hp-muted);
          font-size: 11px;
        }

        .hp-hero-statuses {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          justify-content: flex-end;
        }

        .hp-status {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border: 1px solid var(--hp-border-strong);
          color: var(--hp-muted);
          padding: 5px 8px;
          font-size: 8px;
          letter-spacing: .1em;
          text-transform: uppercase;
          white-space: nowrap;
        }

        .hp-status-good {
          color: var(--hp-green);
          border-color: rgba(101,230,162,.24);
          background: rgba(101,230,162,.035);
        }

        .hp-status-warn {
          color: var(--hp-yellow);
          border-color: rgba(240,200,107,.24);
          background: rgba(240,200,107,.035);
        }

        .hp-status-danger {
          color: var(--hp-red);
          border-color: rgba(255,111,125,.25);
          background: rgba(255,111,125,.035);
        }

        .hp-stat-grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 14px;
          margin-top: 16px;
        }

        .hp-stat {
          min-height: 132px;
          border: 1px solid var(--hp-border);
          background: rgba(10,15,20,.85);
          padding: 18px;
        }

        .hp-stat-icon {
          color: var(--hp-accent);
          margin-bottom: 13px;
        }

        .hp-stat-label {
          color: var(--hp-dim);
          font-size: 8px;
          letter-spacing: .16em;
          font-weight: 800;
        }

        .hp-stat-value {
          margin-top: 6px;
          font-size: 27px;
          line-height: 1.1;
          font-weight: 750;
        }

        .hp-stat-detail {
          margin-top: 5px;
          color: var(--hp-muted);
          font-size: 10px;
        }

        .hp-grid-2 {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 16px;
        }

        .hp-grid-3 {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 16px;
          margin-top: 16px;
        }

        .hp-info-list {
          display: grid;
          gap: 0;
          border-top: 1px solid var(--hp-border);
        }

        .hp-info-row {
          min-width: 0;
          padding: 10px 0;
          border-bottom: 1px solid var(--hp-border);
          display: flex;
          justify-content: space-between;
          gap: 20px;
          align-items: flex-start;
        }

        .hp-info-row > span {
          color: var(--hp-muted);
          font-size: 10px;
        }

        .hp-info-row > strong {
          max-width: 68%;
          text-align: right;
          font-size: 10px;
          overflow-wrap: anywhere;
        }

        .hp-mono {
          font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
          font-size: 9px !important;
          letter-spacing: 0;
        }

        .hp-link-button {
          margin-top: 16px;
          border: 0;
          background: transparent;
          color: var(--hp-accent);
          display: inline-flex;
          align-items: center;
          gap: 5px;
          cursor: pointer;
          padding: 0;
          font-size: 10px;
          font-weight: 700;
        }

        .hp-trust-number {
          font-size: 54px;
          line-height: 1;
          font-weight: 750;
          margin: 20px 0 8px;
        }

        .hp-trust-label {
          color: var(--hp-muted);
          font-size: 11px;
        }

        .hp-progress {
          height: 4px;
          background: rgba(255,255,255,.06);
          margin-top: 20px;
          overflow: hidden;
        }

        .hp-progress span {
          display: block;
          height: 100%;
          background: var(--hp-accent);
          box-shadow: 0 0 14px rgba(88,214,255,.35);
        }

        .hp-boundary {
          display: grid;
          gap: 9px;
        }

        .hp-boundary-row {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px;
          border: 1px solid var(--hp-border);
        }

        .hp-boundary-row.local {
          color: var(--hp-accent);
          background: rgba(88,214,255,.025);
        }

        .hp-boundary-row.shared {
          color: var(--hp-green);
          background: rgba(101,230,162,.025);
        }

        .hp-boundary-row div {
          display: flex;
          flex-direction: column;
          gap: 3px;
        }

        .hp-boundary-row strong {
          font-size: 8px;
          letter-spacing: .14em;
        }

        .hp-boundary-row span {
          color: var(--hp-muted);
          font-size: 10px;
        }

        .hp-pipeline {
          display: grid;
          grid-template-columns: repeat(6, minmax(0, 1fr));
          gap: 9px;
        }

        .hp-pipeline-step {
          border: 1px solid var(--hp-border);
          padding: 14px;
          min-height: 118px;
          background: rgba(255,255,255,.012);
        }

        .hp-pipeline-step span {
          color: var(--hp-accent);
          font-size: 8px;
          letter-spacing: .12em;
        }

        .hp-pipeline-step strong {
          display: block;
          font-size: 9px;
          margin-top: 10px;
          letter-spacing: .08em;
        }

        .hp-pipeline-step small {
          display: block;
          color: var(--hp-muted);
          font-size: 9px;
          line-height: 1.5;
          margin-top: 6px;
        }

        .hp-feature {
          border: 1px solid var(--hp-border);
          padding: 18px;
          background: rgba(255,255,255,.012);
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          gap: 9px;
        }

        .hp-feature svg {
          color: var(--hp-accent);
        }

        .hp-feature strong {
          font-size: 12px;
        }

        .hp-feature span {
          color: var(--hp-muted);
          font-size: 10px;
          line-height: 1.55;
        }

        .hp-button {
          border: 1px solid var(--hp-border-strong);
          background: transparent;
          color: var(--hp-text);
          min-height: 34px;
          padding: 8px 13px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 7px;
          cursor: pointer;
          font-size: 9px;
          font-weight: 800;
          letter-spacing: .1em;
        }

        .hp-button:hover:not(:disabled) {
          border-color: rgba(88,214,255,.45);
          color: var(--hp-accent);
        }

        .hp-button:disabled {
          opacity: .45;
          cursor: not-allowed;
        }

        .hp-button-primary {
          border-color: rgba(88,214,255,.4);
          background: rgba(88,214,255,.08);
          color: var(--hp-accent);
        }

        .hp-button-secondary {
          background: rgba(255,255,255,.025);
        }

        .hp-button-danger {
          border-color: rgba(255,111,125,.3);
          color: var(--hp-red);
          margin-top: 18px;
        }

        .hp-button-large {
          min-height: 42px;
          width: 100%;
        }

        .hp-toolbar {
          display: flex;
          justify-content: space-between;
          gap: 15px;
          align-items: center;
          margin-bottom: 17px;
        }

        .hp-search {
          display: flex;
          align-items: center;
          gap: 8px;
          border: 1px solid var(--hp-border);
          background: rgba(0,0,0,.15);
          padding: 0 10px;
          width: min(420px, 100%);
        }

        .hp-search svg {
          color: var(--hp-dim);
        }

        .hp-search input {
          flex: 1;
          border: 0;
          outline: 0;
          background: transparent;
          color: var(--hp-text);
          padding: 10px 0;
          font-size: 11px;
        }

        .hp-toolbar-meta {
          color: var(--hp-muted);
          font-size: 9px;
        }

        .hp-table-wrap {
          overflow-x: auto;
        }

        .hp-table {
          width: 100%;
          border-collapse: collapse;
          min-width: 760px;
        }

        .hp-table th {
          text-align: left;
          color: var(--hp-dim);
          font-size: 8px;
          letter-spacing: .13em;
          font-weight: 800;
          padding: 10px 9px;
          border-bottom: 1px solid var(--hp-border-strong);
        }

        .hp-table td {
          padding: 13px 9px;
          border-bottom: 1px solid var(--hp-border);
          font-size: 10px;
          color: var(--hp-muted);
          vertical-align: middle;
        }

        .hp-table td strong {
          display: block;
          color: var(--hp-text);
          font-size: 10px;
        }

        .hp-table td small {
          display: block;
          margin-top: 4px;
          color: var(--hp-dim);
          overflow-wrap: anywhere;
        }

        .hp-table-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 5px;
        }

        .hp-small-button {
          border: 1px solid var(--hp-border);
          background: transparent;
          color: var(--hp-muted);
          padding: 6px 8px;
          cursor: pointer;
          font-size: 8px;
          letter-spacing: .07em;
        }

        .hp-small-button:hover {
          color: var(--hp-accent);
          border-color: rgba(88,214,255,.35);
        }

        .hp-version-list {
          display: grid;
          gap: 7px;
        }

        .hp-version {
          border: 1px solid var(--hp-border);
          padding: 12px;
          display: flex;
          justify-content: space-between;
          gap: 15px;
        }

        .hp-version > div {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .hp-version strong {
          font-size: 11px;
        }

        .hp-version span,
        .hp-version small {
          color: var(--hp-muted);
          font-size: 9px;
        }

        .hp-subtitle {
          font-size: 12px;
          margin: 0 0 13px;
        }

        .hp-form {
          display: grid;
          gap: 14px;
        }

        .hp-form label {
          display: grid;
          gap: 6px;
          color: var(--hp-dim);
          font-size: 8px;
          letter-spacing: .13em;
          font-weight: 800;
        }

        .hp-form input,
        .hp-form select {
          width: 100%;
          border: 1px solid var(--hp-border-strong);
          background: #070c11;
          color: var(--hp-text);
          outline: none;
          padding: 10px 11px;
          font-size: 11px;
          min-height: 38px;
        }

        .hp-form input:focus,
        .hp-form select:focus {
          border-color: rgba(88,214,255,.5);
        }

        .hp-form-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 12px;
        }

        .hp-file-boundary {
          border: 1px dashed rgba(88,214,255,.2);
          background: rgba(88,214,255,.025);
          color: var(--hp-muted);
          padding: 11px;
          display: flex;
          gap: 9px;
          align-items: flex-start;
          font-size: 9px;
          line-height: 1.5;
        }

        .hp-file-boundary svg {
          color: var(--hp-accent);
          flex: 0 0 auto;
        }

        .hp-modal-backdrop {
          position: fixed;
          inset: 0;
          z-index: 100;
          background: rgba(0,0,0,.72);
          backdrop-filter: blur(5px);
          display: grid;
          place-items: center;
          padding: 20px;
        }

        .hp-modal {
          width: min(560px, 100%);
          max-height: calc(100vh - 40px);
          overflow-y: auto;
          border: 1px solid var(--hp-border-strong);
          background: #080d12;
          padding: 22px;
          box-shadow: 0 25px 90px rgba(0,0,0,.55);
        }

        .hp-modal-head {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 20px;
        }

        .hp-modal-head h2 {
          margin: 5px 0 0;
          font-size: 18px;
        }

        .hp-icon-button {
          width: 32px;
          height: 32px;
          display: grid;
          place-items: center;
          background: transparent;
          border: 1px solid var(--hp-border);
          color: var(--hp-muted);
          cursor: pointer;
        }

        .hp-modal-actions {
          display: flex;
          justify-content: flex-end;
          gap: 8px;
          margin-top: 20px;
        }

        .hp-notice {
          margin-top: 16px;
          padding: 13px 15px;
          border: 1px solid var(--hp-border);
          display: flex;
          align-items: flex-start;
          gap: 10px;
          font-size: 10px;
          line-height: 1.55;
        }

        .hp-notice p {
          margin: 4px 0 0;
          color: var(--hp-muted);
        }

        .hp-notice button {
          margin-left: auto;
          border: 0;
          background: transparent;
          color: var(--hp-muted);
          cursor: pointer;
        }

        .hp-notice-info {
          border-color: rgba(88,214,255,.2);
          color: var(--hp-accent);
          background: rgba(88,214,255,.025);
        }

        .hp-notice-success {
          border-color: rgba(101,230,162,.2);
          color: var(--hp-green);
          background: rgba(101,230,162,.025);
        }

        .hp-notice-danger {
          border-color: rgba(255,111,125,.22);
          color: var(--hp-red);
          background: rgba(255,111,125,.025);
        }

        .hp-loading-page {
          min-height: 70vh;
          display: grid;
          place-items: center;
          align-content: center;
          gap: 10px;
          color: var(--hp-accent);
          text-align: center;
        }

        .hp-loading-page strong {
          color: var(--hp-text);
          font-size: 13px;
        }

        .hp-loading-page span {
          color: var(--hp-muted);
          font-size: 10px;
        }

        .hp-loading-small {
          min-height: 100px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 9px;
          color: var(--hp-muted);
          font-size: 10px;
        }

        .hp-spin {
          animation: hpSpin 1s linear infinite;
        }

        @keyframes hpSpin {
          to {
            transform: rotate(360deg);
          }
        }

        .hp-round-detail {
          display: grid;
          grid-template-columns: 1fr .75fr;
          gap: 20px;
        }

        .hp-round-state {
          border: 1px solid rgba(88,214,255,.18);
          background: rgba(88,214,255,.025);
          padding: 20px;
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          gap: 9px;
          color: var(--hp-accent);
        }

        .hp-round-state strong {
          color: var(--hp-text);
          font-size: 18px;
        }

        .hp-round-state span {
          color: var(--hp-muted);
          font-size: 10px;
          line-height: 1.55;
        }

        .hp-step-list {
          display: grid;
          gap: 8px;
        }

        .hp-step {
          display: flex;
          gap: 13px;
          padding: 12px;
          border: 1px solid var(--hp-border);
        }

        .hp-step > span {
          color: var(--hp-accent);
          font-family: monospace;
          font-size: 9px;
        }

        .hp-step strong {
          display: block;
          font-size: 9px;
          letter-spacing: .1em;
        }

        .hp-step p {
          color: var(--hp-muted);
          font-size: 9px;
          margin: 5px 0 0;
          line-height: 1.5;
        }

        .hp-training-banner {
          display: flex;
          gap: 15px;
          align-items: flex-start;
          border-color: rgba(88,214,255,.18);
          background: linear-gradient(120deg, rgba(88,214,255,.055), transparent 60%);
        }

        .hp-training-icon {
          width: 48px;
          height: 48px;
          display: grid;
          place-items: center;
          color: var(--hp-accent);
          border: 1px solid rgba(88,214,255,.25);
          flex: 0 0 auto;
        }

        .hp-training-banner h2 {
          margin: 5px 0 5px;
          font-size: 18px;
        }

        .hp-training-banner p {
          margin: 0;
          color: var(--hp-muted);
          font-size: 10px;
          line-height: 1.6;
        }

        .hp-training-result {
          border-color: rgba(101,230,162,.18);
        }

        .hp-artifact {
          display: grid;
          grid-template-columns: 2fr 1fr 1fr;
          gap: 10px;
          margin-top: 18px;
        }

        .hp-artifact > div {
          border: 1px solid var(--hp-border);
          padding: 12px;
          min-width: 0;
        }

        .hp-artifact span {
          display: block;
          color: var(--hp-dim);
          font-size: 8px;
          letter-spacing: .13em;
        }

        .hp-artifact strong {
          display: block;
          margin-top: 7px;
          font-size: 9px;
          overflow-wrap: anywhere;
        }

        .hp-security-matrix {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 10px;
        }

        .hp-security-matrix > div {
          border: 1px solid var(--hp-border);
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 7px;
        }

        .hp-security-matrix svg {
          color: var(--hp-accent);
        }

        .hp-security-matrix strong {
          font-size: 10px;
        }

        .hp-security-matrix span {
          color: var(--hp-muted);
          font-size: 9px;
        }

        .hp-incident-list {
          display: grid;
          gap: 8px;
        }

        .hp-incident {
          display: grid;
          grid-template-columns: 40px 1fr auto;
          gap: 12px;
          align-items: center;
          padding: 14px;
          border: 1px solid var(--hp-border);
        }

        .hp-incident-icon {
          width: 38px;
          height: 38px;
          display: grid;
          place-items: center;
          color: var(--hp-yellow);
          border: 1px solid rgba(240,200,107,.2);
        }

        .hp-incident strong,
        .hp-incident span,
        .hp-incident small {
          display: block;
        }

        .hp-incident strong {
          font-size: 11px;
        }

        .hp-incident span {
          color: var(--hp-muted);
          font-size: 9px;
          margin-top: 4px;
        }

        .hp-incident small {
          color: var(--hp-dim);
          font-size: 8px;
          margin-top: 5px;
        }

        .hp-trust-large {
          display: flex;
          align-items: center;
          gap: 30px;
          padding: 20px 0;
        }

        .hp-trust-large .hp-trust-number {
          margin: 0;
          min-width: 150px;
        }

        .hp-trust-large strong {
          font-size: 13px;
        }

        .hp-trust-large p {
          color: var(--hp-muted);
          font-size: 10px;
          line-height: 1.55;
          max-width: 560px;
        }

        .hp-model-context {
          margin-top: 20px;
        }

        .hp-report-card {
          min-height: 220px;
          display: flex;
          flex-direction: column;
          align-items: flex-start;
        }

        .hp-report-icon {
          color: var(--hp-accent);
          width: 44px;
          height: 44px;
          display: grid;
          place-items: center;
          border: 1px solid rgba(88,214,255,.2);
          margin-bottom: 17px;
        }

        .hp-report-card h2 {
          font-size: 15px;
          margin: 0;
        }

        .hp-report-card p {
          color: var(--hp-muted);
          font-size: 10px;
          line-height: 1.55;
          margin: 8px 0 18px;
          flex: 1;
        }

        .hp-quality-list {
          display: grid;
        }

        .hp-quality-row {
          display: grid;
          grid-template-columns: 2fr .8fr .8fr .8fr;
          gap: 15px;
          align-items: center;
          padding: 12px 0;
          border-top: 1px solid var(--hp-border);
        }

        .hp-quality-row > div {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .hp-quality-row strong {
          font-size: 10px;
        }

        .hp-quality-row span {
          color: var(--hp-muted);
          font-size: 9px;
        }

        .hp-timeline {
          position: relative;
          display: grid;
          gap: 0;
        }

        .hp-timeline-item {
          position: relative;
          display: grid;
          grid-template-columns: 16px 1fr;
          gap: 13px;
          padding: 0 0 20px;
        }

        .hp-timeline-item::before {
          content: "";
          position: absolute;
          left: 5px;
          top: 13px;
          bottom: 0;
          width: 1px;
          background: var(--hp-border);
        }

        .hp-timeline-item:last-child::before {
          display: none;
        }

        .hp-timeline-dot {
          width: 11px;
          height: 11px;
          border: 1px solid var(--hp-accent);
          background: var(--hp-bg);
          margin-top: 2px;
          z-index: 1;
        }

        .hp-timeline-item > div:last-child {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .hp-timeline-item span {
          color: var(--hp-accent);
          font-size: 8px;
          letter-spacing: .12em;
        }

        .hp-timeline-item strong {
          font-size: 11px;
        }

        .hp-timeline-item small {
          color: var(--hp-muted);
          font-size: 8px;
        }

        .hp-empty {
          min-height: 160px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 20px;
          color: var(--hp-muted);
        }

        .hp-empty-icon {
          width: 46px;
          height: 46px;
          display: grid;
          place-items: center;
          color: var(--hp-accent);
          border: 1px solid var(--hp-border);
          margin-bottom: 13px;
        }

        .hp-empty h3 {
          color: var(--hp-text);
          margin: 0 0 6px;
          font-size: 13px;
        }

        .hp-empty p {
          margin: 0;
          max-width: 500px;
          font-size: 10px;
          line-height: 1.6;
        }

        .hp-json {
          max-height: 340px;
          overflow: auto;
          border: 1px solid var(--hp-border);
          background: #030609;
          color: #9fc4d2;
          padding: 14px;
          font-family: monospace;
          font-size: 9px;
          line-height: 1.5;
        }

        @media (max-width: 1200px) {
          .hp-sidebar {
            width: 220px;
            flex-basis: 220px;
          }

          .hp-main {
            padding: 26px;
          }

          .hp-stat-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }

          .hp-pipeline {
            grid-template-columns: repeat(3, minmax(0, 1fr));
          }

          .hp-security-matrix {
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }
        }

        @media (max-width: 850px) {
          .hospital-full-portal {
            display: block;
          }

          .hp-sidebar {
            position: static;
            width: 100%;
            height: auto;
            min-height: 0;
          }

          .hp-nav {
            display: flex;
            overflow-x: auto;
            gap: 5px;
            padding-bottom: 10px;
          }

          .hp-nav-group {
            min-width: 175px;
          }

          .hp-sidebar-bottom {
            display: none;
          }

          .hp-main {
            padding: 20px;
          }

          .hp-grid-2,
          .hp-grid-3,
          .hp-round-detail {
            grid-template-columns: 1fr;
          }

          .hp-hero,
          .hp-page-head {
            flex-direction: column;
            align-items: stretch;
          }

          .hp-hero-statuses {
            justify-content: flex-start;
          }

          .hp-artifact {
            grid-template-columns: 1fr;
          }

          .hp-quality-row {
            grid-template-columns: 1fr 1fr;
          }

          .hp-incident {
            grid-template-columns: 40px 1fr;
          }

          .hp-incident > .hp-status {
            grid-column: 2;
            justify-self: start;
          }
        }

        @media (max-width: 560px) {
          .hp-stat-grid {
            grid-template-columns: 1fr;
          }

          .hp-pipeline {
            grid-template-columns: 1fr;
          }

          .hp-form-grid {
            grid-template-columns: 1fr;
          }

          .hp-trust-large {
            display: block;
          }

          .hp-trust-large .hp-trust-number {
            margin-bottom: 15px;
          }
        }
      `}</style>

      <div className="hospital-full-portal">
        <aside className="hp-sidebar">
          <div className="hp-brand">
            <div className="hp-brand-lockup">
              <div className="hp-brand-mark">FS</div>

              <div>
                <strong>FED SENTINEL</strong>
                <span>HOSPITAL PORTAL</span>
              </div>
            </div>
          </div>

          <div className="hp-identity">
            <div className="hp-eyebrow">
              CONNECTED HOSPITAL
            </div>

            <div className="hp-identity-code">
              {hospital?.code || 'HOSPITAL'}
            </div>

            <div className="hp-identity-name">
              {hospital?.name ||
                'Hospital Workspace'}
            </div>

            <div className="hp-online">
              authenticated session
            </div>
          </div>

          <nav className="hp-nav">
            {navigation.map((group) => (
              <div
                className="hp-nav-group"
                key={group.label}
              >
                <div className="hp-nav-label">
                  {group.label}
                </div>

                {group.items.map(
                  ([id, label, Icon]) => (
                    <button
                      key={id}
                      className={`hp-nav-item ${
                        active === id
                          ? 'active'
                          : ''
                      }`}
                      onClick={() =>
                        setActive(id)
                      }
                      type="button"
                    >
                      <Icon
                        size={14}
                        strokeWidth={1.8}
                      />
                      <span>{label}</span>
                    </button>
                  ),
                )}
              </div>
            ))}
          </nav>

          <div className="hp-sidebar-bottom">
            <div className="hp-privacy-mini">
              <strong>PRIVACY BOUNDARY</strong>
              <span>
                Raw hospital and patient data remains inside the
                hospital.
              </span>
            </div>

            <button
              className="hp-exit"
              onClick={onLogout}
              type="button"
            >
              EXIT HOSPITAL PORTAL
            </button>
          </div>
        </aside>

        <main className="hp-main">
          {error && (
            <div className="hp-notice hp-notice-danger">
              <AlertTriangle size={18} />
              <div>
                <strong>
                  Hospital API synchronization error
                </strong>
                <p>{error}</p>
              </div>

              <button
                onClick={() => setError('')}
                type="button"
              >
                <X size={15} />
              </button>
            </div>
          )}

          {!loading && hospital && (
            <div
              style={{
                display: 'flex',
                justifyContent: 'flex-end',
                marginBottom: 8,
                color: 'var(--hp-dim)',
                fontSize: 8,
                letterSpacing: '.1em',
              }}
            >
              {activeLabel.toUpperCase()}
            </div>
          )}

          {page}
        </main>
      </div>
    </>
  )
}



