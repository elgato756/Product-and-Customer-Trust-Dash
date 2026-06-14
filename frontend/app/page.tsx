'use client'

import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'

type StakeholderReview = {
  stakeholder: string
  status: string
  review_focus: string
  trigger: string
  suggested_next_step: string
}

type TrustRequest = {
  id: number
  source: string
  source_url?: string
  source_community?: string
  source_type?: string
  verification_status?: string
  jurisdiction?: string
  customer_region?: string
  customer_segment?: string
  regional_request_profile?: string
  predicted_regional_needs?: string
  regional_routing_notes?: string
  stakeholder_review_matrix?: string
  authority?: string
  compliance_area?: string
  title: string
  raw_content?: string
  category: string
  severity: number
  confidence: number
  summary: string
  escalation_team: string
  should_escalate: boolean
  status: string
  analyst_notes?: string
  created_at: string
}

type AuditEvent = {
  id: number
  incident_id?: number
  action: string
  actor: string
  details?: string
  created_at: string
}

const API_BASE = 'http://localhost:8000'

const FILTERS = [
  'All',
  'High priority',
  'Open',
  'Escalated',
  'Questionnaires',
  'Trust Center',
  'Unsupported Claims',
  'Region Routed',
  'Japan / APAC',
  'EU / EEA',
  'US Financial Services',
]

export default function Home() {
  const [requests, setRequests] = useState<TrustRequest[]>([])
  const [loading, setLoading] = useState(false)
  const [activeFilter, setActiveFilter] = useState('All')
  const [selectedRequest, setSelectedRequest] = useState<TrustRequest | null>(null)
  const [notesDraft, setNotesDraft] = useState('')
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([])

  useEffect(() => {
    fetchRequests()
  }, [])

  useEffect(() => {
    if (selectedRequest) {
      setNotesDraft(selectedRequest.analyst_notes || '')
      fetchAuditEvents(selectedRequest.id)
    } else {
      setAuditEvents([])
    }
  }, [selectedRequest])

  const fetchRequests = async () => {
    const res = await axios.get(`${API_BASE}/customer-requests`)
    setRequests(res.data)

    if (selectedRequest) {
      const refreshed = res.data.find((item: TrustRequest) => item.id === selectedRequest.id)
      if (refreshed) {
        setSelectedRequest(refreshed)
      }
    }
  }

  const fetchAuditEvents = async (requestId: number) => {
    try {
      const res = await axios.get(`${API_BASE}/customer-requests/${requestId}/audit`)
      setAuditEvents(res.data)
    } catch {
      setAuditEvents([])
    }
  }

  const seedDemo = async () => {
    setLoading(true)
    try {
      await axios.post(`${API_BASE}/demo/seed`)
      await fetchRequests()
    } finally {
      setLoading(false)
    }
  }

  const resetDemo = async () => {
    setLoading(true)
    try {
      await axios.post(`${API_BASE}/demo/reset`)
      setSelectedRequest(null)
      await fetchRequests()
    } finally {
      setLoading(false)
    }
  }

  const updateRequest = async (
    id: number,
    status: string,
    analystNotes?: string
  ) => {
    await axios.patch(`${API_BASE}/customer-requests/${id}`, {
      status,
      analyst_notes: analystNotes,
    })
    await fetchRequests()
  }

  const updateStatus = async (id: number, status: string) => {
    await updateRequest(id, status)
  }

  const saveNotes = async () => {
    if (!selectedRequest) return
    await updateRequest(selectedRequest.id, selectedRequest.status, notesDraft)
  }

  const escalate = async (id: number) => {
    await axios.post(`${API_BASE}/customer-requests/${id}/escalate`)
    await fetchRequests()
  }

  const filteredRequests = useMemo(() => {
    return requests.filter((request) => {
      const category = request.category.toLowerCase()
      const sourceType = (request.source_type || '').toLowerCase()
      const verification = (request.verification_status || '').toLowerCase()
      const region = (request.customer_region || request.jurisdiction || '').toLowerCase()

      if (activeFilter === 'All') return true
      if (activeFilter === 'High priority') return request.severity >= 8
      if (activeFilter === 'Open') return request.status === 'open'
      if (activeFilter === 'Escalated') return request.status === 'escalated'
      if (activeFilter === 'Questionnaires') return category.includes('questionnaire') || sourceType.includes('questionnaire')
      if (activeFilter === 'Trust Center') return category.includes('trust_center') || sourceType.includes('trust')
      if (activeFilter === 'Unsupported Claims') return category.includes('unsupported') || verification.includes('unsupported')
      if (activeFilter === 'Region Routed') return Boolean(request.regional_request_profile || request.regional_routing_notes)
      if (activeFilter === 'Japan / APAC') return region.includes('japan') || region.includes('apac')
      if (activeFilter === 'EU / EEA') return region.includes('eu') || region.includes('eea')
      if (activeFilter === 'US Financial Services') return region.includes('financial') || region.includes('bank')

      return true
    })
  }, [requests, activeFilter])

  const priorityClass = (priority: number) => {
    if (priority >= 8) return 'bg-red-100 text-red-800 border-red-200'
    if (priority >= 5) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    return 'bg-green-100 text-green-800 border-green-200'
  }

  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="mb-2 text-sm font-medium text-slate-500">
              Human-in-the-loop GRC prototype
            </p>
            <h1 className="text-3xl font-bold text-slate-900">
              AI Customer Trust & Enterprise Assurance Workflow
            </h1>
            <p className="mt-2 max-w-3xl text-slate-600">
              Triage security questionnaires, Trust Center artifacts, public policy language,
              regional customer request patterns, customer-specific architecture questions, and customer-facing
              security claims while keeping final responses grounded in approved evidence and human review.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              onClick={seedDemo}
              disabled={loading}
              className="rounded-xl bg-slate-900 px-4 py-2 text-white shadow-sm disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Load Demo Requests'}
            </button>

            <button
              onClick={resetDemo}
              disabled={loading}
              className="rounded-xl border bg-white px-4 py-2 text-slate-800 shadow-sm disabled:opacity-50"
            >
              Reset Demo
            </button>
          </div>
        </div>

        <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-5">
          <Metric label="Total Requests" value={requests.length} />
          <Metric label="Open" value={requests.filter(i => i.status === 'open').length} />
          <Metric label="Escalated" value={requests.filter(i => i.status === 'escalated').length} />
          <Metric label="High Priority" value={requests.filter(i => i.severity >= 8).length} />
          <Metric label="Region Routed" value={requests.filter(i => i.regional_request_profile || i.regional_routing_notes).length} />
        </div>

        <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-4">
          <div className="rounded-2xl border bg-white p-4 shadow-sm">
            <p className="text-sm font-semibold text-slate-900">Approved answer bank</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Demonstrates reusable response content for recurring security questions,
              CAIQ-style diligence, and customer-facing trust narratives.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-4 shadow-sm">
            <p className="text-sm font-semibold text-slate-900">Evidence-first claims</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Flags unsupported statements and maps approved responses to SOC 2,
              ISO 27001, privacy language, policies, and control owner review.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-4 shadow-sm">
            <p className="text-sm font-semibold text-slate-900">Stakeholder review matrix</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Shows which requests can use approved content and which need
              Legal, Privacy, Security, Product, Field Security, GTM, or Customer Success review.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-4 shadow-sm">
            <p className="text-sm font-semibold text-slate-900">Regional request intelligence</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Uses historical request patterns to front-load likely regional needs,
              such as Japan/APAC data residency questions, EU privacy artifacts,
              or US financial services evidence requests.
            </p>
          </div>
        </div>

        <div className="mb-6 flex flex-wrap gap-2">
          {FILTERS.map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`rounded-full border px-3 py-2 text-sm ${
                activeFilter === filter
                  ? 'bg-slate-900 text-white'
                  : 'bg-white text-slate-700'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_440px]">
          <section>
            <div className="mb-4 text-sm text-slate-500">
              Showing {filteredRequests.length} of {requests.length} trust requests
            </div>

            <div className="space-y-4">
              {filteredRequests.map((request) => (
                <div
                  key={request.id}
                  onClick={() => setSelectedRequest(request)}
                  className={`cursor-pointer rounded-2xl border bg-white p-5 shadow-sm transition hover:border-slate-400 ${
                    selectedRequest?.id === request.id ? 'border-slate-900' : ''
                  }`}
                >
                  <div className="mb-3 flex items-start justify-between gap-4">
                    <div>
                      <div className="mb-2 flex flex-wrap gap-2">
                        <span className="rounded-full border px-2 py-1 text-xs text-slate-600">
                          {request.source_community || request.source}
                        </span>
                        <span className="rounded-full border px-2 py-1 text-xs text-slate-600">
                          {request.category.replaceAll('_', ' ')}
                        </span>
                        {(request.customer_region || request.jurisdiction) && (
                          <span className="rounded-full border px-2 py-1 text-xs text-slate-600">
                            {request.customer_region || request.jurisdiction}
                          </span>
                        )}
                        {request.verification_status && (
                          <span className="rounded-full border px-2 py-1 text-xs text-slate-600">
                            {request.verification_status.replaceAll('_', ' ')}
                          </span>
                        )}
                      </div>
                      <h2 className="text-lg font-semibold text-slate-900">
                        {request.title}
                      </h2>
                    </div>

                    <span className={`rounded-full border px-3 py-1 text-sm font-medium ${priorityClass(request.severity)}`}>
                      Priority {request.severity}/10
                    </span>
                  </div>

                  <p className="mb-4 text-sm leading-6 text-slate-700">
                    {request.summary}
                  </p>

                  <div className="mb-4 grid grid-cols-1 gap-3 text-sm md:grid-cols-4">
                    <Info label="Confidence" value={`${Math.round(request.confidence * 100)}%`} />
                    <Info label="Region" value={request.customer_region || request.jurisdiction || 'Global'} />
                    <Info label="Review Path" value={request.escalation_team.replaceAll('_', ' ')} />
                    <Info label="Review Required" value={request.should_escalate ? 'Yes' : 'No'} />
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={(event) => {
                        event.stopPropagation()
                        updateStatus(request.id, 'triaged')
                      }}
                      className="rounded-lg border px-3 py-2 text-sm"
                    >
                      Mark Triaged
                    </button>

                    <button
                      onClick={(event) => {
                        event.stopPropagation()
                        escalate(request.id)
                      }}
                      className="rounded-lg bg-slate-900 px-3 py-2 text-sm text-white"
                    >
                      Escalate
                    </button>

                    <button
                      onClick={(event) => {
                        event.stopPropagation()
                        updateStatus(request.id, 'closed')
                      }}
                      className="rounded-lg border px-3 py-2 text-sm"
                    >
                      Close
                    </button>
                  </div>
                </div>
              ))}

              {filteredRequests.length === 0 && (
                <div className="rounded-2xl border bg-white p-8 text-center text-slate-500">
                  No trust requests match this filter. Load demo requests to start the workflow.
                </div>
              )}
            </div>
          </section>

          <aside className="h-fit rounded-2xl border bg-white p-5 shadow-sm lg:sticky lg:top-8">
            {!selectedRequest ? (
              <div className="py-10 text-center text-slate-500">
                Select a trust request to review approved evidence, regional routing context, stakeholder review matrix, escalation path, and analyst notes.
              </div>
            ) : (
              <div>
                <div className="mb-4 flex items-start justify-between gap-3">
                  <div>
                    <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                      Request Detail
                    </p>
                    <h3 className="text-lg font-semibold text-slate-900">
                      {selectedRequest.title}
                    </h3>
                  </div>

                  <button
                    onClick={() => setSelectedRequest(null)}
                    className="rounded-lg border px-2 py-1 text-sm"
                  >
                    Close
                  </button>
                </div>

                <div className="mb-4 grid grid-cols-2 gap-3 text-sm">
                  <Info label="Status" value={selectedRequest.status} />
                  <Info label="Category" value={selectedRequest.category.replaceAll('_', ' ')} />
                  <Info label="Region" value={selectedRequest.customer_region || selectedRequest.jurisdiction || 'Global'} />
                  <Info label="Segment" value={selectedRequest.customer_segment || 'Not specified'} />
                  <Info label="Priority" value={`${selectedRequest.severity}/10`} />
                  <Info label="Confidence" value={`${Math.round(selectedRequest.confidence * 100)}%`} />
                </div>

                <div className="mb-4 rounded-xl bg-slate-50 p-4">
                  <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                    AI-Assisted Triage Summary
                  </p>
                  <p className="text-sm leading-6 text-slate-700">
                    {selectedRequest.summary}
                  </p>
                </div>

                <div className="mb-4 rounded-xl bg-slate-50 p-4">
                  <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                    Request Context
                  </p>
                  <p className="text-sm leading-6 text-slate-700">
                    {selectedRequest.raw_content || 'No request detail available.'}
                  </p>
                </div>

                {(selectedRequest.regional_request_profile || selectedRequest.predicted_regional_needs || selectedRequest.regional_routing_notes) && (
                  <div className="mb-4 rounded-xl bg-slate-50 p-4">
                    <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                      Regional Routing Intelligence
                    </p>
                    {selectedRequest.regional_request_profile && (
                      <p className="mb-2 text-sm font-medium text-slate-800">
                        {selectedRequest.regional_request_profile}
                      </p>
                    )}
                    {selectedRequest.predicted_regional_needs && (
                      <p className="text-sm leading-6 text-slate-700">
                        <span className="font-medium">Likely front-loaded needs: </span>
                        {selectedRequest.predicted_regional_needs}
                      </p>
                    )}
                    {selectedRequest.regional_routing_notes && (
                      <p className="mt-2 text-sm leading-6 text-slate-700">
                        <span className="font-medium">Routing notes: </span>
                        {selectedRequest.regional_routing_notes}
                      </p>
                    )}
                  </div>
                )}

                <div className="mb-4 rounded-xl bg-slate-50 p-4">
                  <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                    Recommended Review Path
                  </p>
                  <p className="text-sm leading-6 text-slate-700">
                    {selectedRequest.escalation_team.replaceAll('_', ' ')}
                  </p>
                </div>

                <StakeholderReviewMatrix request={selectedRequest} />

                <div className="mb-4">
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
                    Analyst Notes
                  </label>
                  <textarea
                    value={notesDraft}
                    onChange={(event) => setNotesDraft(event.target.value)}
                    placeholder="Document approved answer source, regional playbook fit, missing evidence, stakeholder review, customer-facing language, or follow-up actions..."
                    className="h-36 w-full rounded-xl border p-3 text-sm outline-none focus:border-slate-900"
                  />
                </div>

                <div className="mb-4 flex flex-wrap gap-2">
                  <button
                    onClick={saveNotes}
                    className="rounded-lg bg-slate-900 px-3 py-2 text-sm text-white"
                  >
                    Save Notes
                  </button>

                  <button
                    onClick={() => updateRequest(selectedRequest.id, 'triaged', notesDraft)}
                    className="rounded-lg border px-3 py-2 text-sm"
                  >
                    Save & Triaged
                  </button>

                  <button
                    onClick={() => updateRequest(selectedRequest.id, 'closed', notesDraft)}
                    className="rounded-lg border px-3 py-2 text-sm"
                  >
                    Save & Close
                  </button>
                </div>

                <div className="mb-4 rounded-xl bg-slate-50 p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      Audit Trail
                    </p>
                    <button
                      onClick={() => fetchAuditEvents(selectedRequest.id)}
                      className="rounded-lg border bg-white px-2 py-1 text-xs"
                    >
                      Refresh
                    </button>
                  </div>

                  <div className="space-y-3">
                    {auditEvents.length === 0 ? (
                      <p className="text-sm text-slate-500">
                        No audit events recorded yet.
                      </p>
                    ) : (
                      auditEvents.map((event) => (
                        <div key={event.id} className="rounded-lg border bg-white p-3">
                          <div className="mb-1 flex items-center justify-between gap-2">
                            <p className="text-sm font-medium text-slate-800">
                              {event.action.replaceAll('_', ' ')}
                            </p>
                            <p className="text-xs text-slate-500">
                              {new Date(event.created_at).toLocaleString()}
                            </p>
                          </div>

                          <p className="text-xs text-slate-500">
                            Actor: {event.actor}
                          </p>

                          {event.details && (
                            <p className="mt-2 text-sm leading-5 text-slate-700">
                              {event.details}
                            </p>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => escalate(selectedRequest.id)}
                    className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
                  >
                    Escalate for Review
                  </button>

                  {selectedRequest.source_url && (
                    <a
                      href={selectedRequest.source_url}
                      target="_blank"
                      className="rounded-lg border px-3 py-2 text-sm"
                    >
                      View Evidence Source
                    </a>
                  )}
                </div>
              </div>
            )}
          </aside>
        </div>
      </div>
    </main>
  )
}


function getStakeholderMatrix(request: TrustRequest): StakeholderReview[] {
  if (request.stakeholder_review_matrix) {
    try {
      const parsed = JSON.parse(request.stakeholder_review_matrix)
      if (Array.isArray(parsed)) {
        return parsed
      }
    } catch {
      // Fall through to deterministic frontend fallback for older seeded records.
    }
  }

  const text = [
    request.title,
    request.raw_content,
    request.category,
    request.verification_status,
    request.escalation_team,
    request.customer_region,
    request.customer_segment,
    request.regional_routing_notes,
  ].join(' ').toLowerCase()

  const matrix: StakeholderReview[] = [
    {
      stakeholder: 'GRC / Customer Trust',
      status: 'Required',
      review_focus: 'Own intake, triage, evidence mapping, answer-bank reuse, and final response packaging.',
      trigger: 'Every customer trust request requires a named GRC / Customer Trust owner.',
      suggested_next_step: 'Map the request to approved artifacts, document missing evidence, and coordinate stakeholder review before response finalization.',
    },
  ]

  const includesAny = (terms: string[]) => terms.some((term) => text.includes(term))

  if (includesAny(['questionnaire', 'caiq', 'soc 2', 'iso 27001', 'evidence', 'bank', 'financial services', 'regulated enterprise']) || request.escalation_team.includes('field_security')) {
    matrix.push({
      stakeholder: 'Field Security',
      status: 'Required',
      review_focus: 'Validate customer-facing technical response quality, questionnaire coverage, and enterprise assurance narrative.',
      trigger: 'Questionnaire, CAIQ, SOC 2/ISO evidence, regulated customer, or deal-support signal detected.',
      suggested_next_step: 'Confirm which questions can use approved answer-bank content and which require deeper evidence owner review.',
    })
  }

  if (includesAny(['security', 'encryption', 'access control', 'logging', 'vulnerability', 'incident response', 'architecture', 'dedicated storage', 'segregation', 'cloud', 'hosting'])) {
    matrix.push({
      stakeholder: 'Security',
      status: 'Required',
      review_focus: 'Review control evidence, architecture statements, encryption/access-control language, and security claim accuracy.',
      trigger: 'Security architecture, dedicated storage, encryption, logging, vulnerability, or control evidence question detected.',
      suggested_next_step: 'Validate the evidence path and approve any technical language before it is reused externally.',
    })
  }

  if (includesAny(['privacy', 'data handling', 'retention', 'deletion', 'subprocessor', 'cross-border', 'data residency', 'gdpr', 'dpa', 'scc', 'model/data', 'data use'])) {
    matrix.push({
      stakeholder: 'Privacy',
      status: 'Required',
      review_focus: 'Review data handling, retention/deletion, subprocessors, cross-border transfer, and privacy representation accuracy.',
      trigger: 'Privacy, GDPR/DPA/SCC, data residency, retention, deletion, or subprocessor topic detected.',
      suggested_next_step: 'Confirm approved privacy language and identify whether DPA, SCC, or subprocessor artifacts should be attached.',
    })
  }

  if (includesAny(['legal', 'dpa', 'scc', 'privacy policy', 'public policy', 'unsupported claim', 'external claim', 'contract', 'customer-facing claim', 'broad security claim'])) {
    matrix.push({
      stakeholder: 'Legal',
      status: 'Required',
      review_focus: 'Review customer-facing legal posture, public policy language, contractual wording, and unsupported external claims.',
      trigger: 'External claim, DPA/SCC, privacy policy, contractual, or broad public statement detected.',
      suggested_next_step: 'Approve or narrow the language before it is sent externally; block unsupported claims until evidence is confirmed.',
    })
  }

  if (includesAny(['product', 'available', 'configurable', 'dedicated storage', 'data segregation', 'zero data retention', 'product tiers', 'customer-specific', 'feature', 'capability'])) {
    matrix.push({
      stakeholder: 'Product',
      status: 'Conditional',
      review_focus: 'Confirm product capability boundaries, configurable options, product-tier behavior, and customer-specific commitments.',
      trigger: 'Product capability, dedicated storage, zero retention, customer-specific controls, or configurable feature claim detected.',
      suggested_next_step: 'Confirm the accurate product position and update approved customer-facing language if needed.',
    })
  }

  if (includesAny(['japan', 'apac', 'eu', 'eea', 'us financial', 'bank', 'regional', 'localized']) || Boolean(request.customer_region && request.customer_region !== 'Global')) {
    matrix.push({
      stakeholder: 'Regional GTM / Local Team',
      status: 'Conditional',
      review_focus: 'Validate regional customer context, localization needs, and region-specific diligence patterns.',
      trigger: 'Regional playbook attached based on customer region, jurisdiction, or historical request pattern.',
      suggested_next_step: 'Front-load region-specific artifacts and coordinate localized customer communication where appropriate.',
    })
  }

  if (includesAny(['deal', 'sales', 'customer success', 'csm', 'gtm', 'prospect', 'customer call', 'high-priority deal']) || request.escalation_team.includes('customer_success')) {
    matrix.push({
      stakeholder: 'GTM / Customer Success',
      status: 'Informational',
      review_focus: 'Coordinate customer communication, deal context, response timing, and follow-up expectations.',
      trigger: 'Sales, CSM, prospect, customer call, or high-priority deal-support context detected.',
      suggested_next_step: 'Use approved language from the answer bank and route follow-up questions back through the review owner.',
    })
  }

  return matrix
}

function statusClass(status: string) {
  if (status === 'Required') return 'border-red-200 bg-red-50 text-red-700'
  if (status === 'Conditional') return 'border-yellow-200 bg-yellow-50 text-yellow-700'
  return 'border-slate-200 bg-white text-slate-600'
}

function StakeholderReviewMatrix({ request }: { request: TrustRequest }) {
  const matrix = getStakeholderMatrix(request)

  return (
    <div className="mb-4 rounded-xl bg-slate-50 p-4">
      <div className="mb-3">
        <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-500">
          Stakeholder Review Matrix
        </p>
        <p className="text-sm leading-6 text-slate-600">
          Demonstrates review judgment: what can use approved content, what needs partner review,
          and what should not be claimed externally without evidence.
        </p>
      </div>

      <div className="space-y-3">
        {matrix.map((row) => (
          <div key={`${row.stakeholder}-${row.status}`} className="rounded-lg border bg-white p-3">
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-semibold text-slate-900">{row.stakeholder}</p>
              <span className={`rounded-full border px-2 py-1 text-xs font-medium ${statusClass(row.status)}`}>
                {row.status}
              </span>
            </div>
            <p className="text-sm leading-5 text-slate-700">{row.review_focus}</p>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              <span className="font-medium">Trigger: </span>{row.trigger}
            </p>
            <p className="mt-1 text-xs leading-5 text-slate-500">
              <span className="font-medium">Next step: </span>{row.suggested_next_step}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl border bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-bold text-slate-900">{value}</p>
    </div>
  )
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-50 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 break-words font-medium text-slate-800">{value}</p>
    </div>
  )
}
