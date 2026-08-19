import { useCallback, useEffect, useMemo, useState } from 'react'
import { apiFetch, apiJson, buildQuery, ApiError } from '../api/client'
import type {
  DocumentItem,
  DocumentStatus,
  DocType,
  Extraction,
  Metrics,
  MetricsFilters,
} from '../api/types'
import StatusBadge from '../components/StatusBadge'
import Modal from '../components/Modal'

const POLL_INTERVAL = 5000

function formatDate(value: string | undefined | null): string {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString('pt-BR', { hour12: false })
}

export default function Documents() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [statusFilter, setStatusFilter] = useState<DocumentStatus | ''>('')
  const [typeFilter, setTypeFilter] = useState<DocType | ''>('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [metricDoc, setMetricDoc] = useState('')
  const [metricDateFrom, setMetricDateFrom] = useState('')
  const [metricDateTo, setMetricDateTo] = useState('')
  const [metricType, setMetricType] = useState<DocType | ''>('')
  const [detailDoc, setDetailDoc] = useState<DocumentItem | null>(null)
  const [extractions, setExtractions] = useState<Extraction[]>([])
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState<string | null>(null)

  const tableFilters = useMemo(
    () => ({
      status: statusFilter || undefined,
      doc_type: typeFilter || undefined,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
    }),
    [statusFilter, typeFilter, dateFrom, dateTo],
  )

  const metricsFilters: MetricsFilters = useMemo(
    () => ({
      document_id: metricDoc || undefined,
      date_from: metricDateFrom || undefined,
      date_to: metricDateTo || undefined,
      doc_type: metricType || undefined,
    }),
    [metricDoc, metricDateFrom, metricDateTo, metricType],
  )

  const hasActiveJobs = useMemo(
    () =>
      documents.some(
        (doc) => doc.status === 'queued' || doc.status === 'processing',
      ),
    [documents],
  )

  const loadDocuments = useCallback(async () => {
    try {
      const data = await apiFetch<DocumentItem[]>(
        `/documents${buildQuery(tableFilters)}`,
      )
      setDocuments(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error('Falha ao carregar documentos', err)
    }
  }, [tableFilters])

  const loadMetrics = useCallback(async () => {
    try {
      const data = await apiFetch<Metrics>(
        `/metrics${buildQuery(metricsFilters)}`,
      )
      setMetrics(data)
    } catch (err) {
      console.error('Falha ao carregar métricas', err)
    }
  }, [metricsFilters])

  useEffect(() => {
    void loadDocuments()
    void loadMetrics()
  }, [loadDocuments, loadMetrics])

  useEffect(() => {
    if (!hasActiveJobs) return
    const timer = window.setInterval(() => {
      void loadDocuments()
      void loadMetrics()
    }, POLL_INTERVAL)
    return () => window.clearInterval(timer)
  }, [hasActiveJobs, loadDocuments, loadMetrics])

  async function openDetail(doc: DocumentItem) {
    setDetailDoc(doc)
    setExtractions([])
    setDetailError(null)
    setDetailLoading(true)
    try {
      const [meta, extractionsData] = await Promise.all([
        apiFetch<DocumentItem>(`/documents/${doc.id}`),
        apiFetch<Extraction[]>(`/documents/${doc.id}/extractions`),
      ])
      setDetailDoc(meta)
      setExtractions(Array.isArray(extractionsData) ? extractionsData : [])
    } catch (err) {
      setDetailError(
        err instanceof Error ? err.message : 'Falha ao carregar detalhes.',
      )
    } finally {
      setDetailLoading(false)
    }
  }

  async function deleteDocument(doc: DocumentItem) {
    const name = doc.filename ?? doc.name ?? 'documento'
    if (!window.confirm(`Excluir "${name}"? Esta ação não pode ser desfeita.`)) {
      return
    }
    try {
      await apiJson<undefined>(`/documents/${doc.id}`, 'DELETE', undefined)
      await loadDocuments()
      await loadMetrics()
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : 'Falha ao excluir documento.'
      window.alert(message)
    }
  }

  return (
    <div className="page">
      <h1>Documentos</h1>
      <p className="page-subtitle">Acompanhe o processamento e a qualidade das extrações.</p>

      <section className="card">
        <h2>Métricas</h2>
        <div className="filters-row">
          <select value={metricDoc} onChange={(e) => setMetricDoc(e.target.value)}>
            <option value="">Todos os documentos</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.filename ?? doc.name}
              </option>
            ))}
          </select>
          <select value={metricType} onChange={(e) => setMetricType(e.target.value as DocType | '')}>
            <option value="">Todos os tipos</option>
            <option value="PDF">PDF</option>
            <option value="DOCX">DOCX</option>
            <option value="TXT">TXT</option>
          </select>
          <input
            type="date"
            value={metricDateFrom}
            onChange={(e) => setMetricDateFrom(e.target.value)}
            aria-label="Data inicial das métricas"
          />
          <input
            type="date"
            value={metricDateTo}
            onChange={(e) => setMetricDateTo(e.target.value)}
            aria-label="Data final das métricas"
          />
        </div>
        {metrics ? (
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-label">Cobertura</span>
              <span className="metric-value">{metrics.coverage.toFixed(1)}%</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Consistência</span>
              <span className="metric-value">{metrics.consistency.toFixed(1)}%</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Latência média</span>
              <span className="metric-value">
                {metrics.avg_latency_seconds.toFixed(2)}s
              </span>
            </div>
          </div>
        ) : (
          <p className="muted">Sem dados de métricas disponíveis.</p>
        )}
      </section>

      <section className="card">
        <div className="filters-row">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as DocumentStatus | '')}
          >
            <option value="">Todos os status</option>
            <option value="queued">Na fila</option>
            <option value="processing">Processando</option>
            <option value="done">Concluído</option>
            <option value="error">Erro</option>
          </select>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as DocType | '')}
          >
            <option value="">Todos os tipos</option>
            <option value="PDF">PDF</option>
            <option value="DOCX">DOCX</option>
            <option value="TXT">TXT</option>
          </select>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            aria-label="Data inicial"
          />
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            aria-label="Data final"
          />
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Tipo</th>
              <th>Upload</th>
              <th>Palavras</th>
              <th>Status</th>
              <th className="actions-col">Ações</th>
            </tr>
          </thead>
          <tbody>
            {documents.length === 0 ? (
              <tr>
                <td colSpan={6} className="muted">
                  Nenhum documento encontrado.
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.filename ?? doc.name}</td>
                  <td>{doc.doc_type}</td>
                  <td>{formatDate(doc.uploaded_at ?? doc.created_at)}</td>
                  <td>{doc.word_count ?? '—'}</td>
                  <td>
                    <StatusBadge status={doc.status} />
                  </td>
                  <td className="actions-col">
                    <button
                      type="button"
                      className="btn btn-ghost"
                      onClick={() => void openDetail(doc)}
                    >
                      Ver
                    </button>
                    <button
                      type="button"
                      className="btn btn-danger"
                      onClick={() => void deleteDocument(doc)}
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      {detailDoc && (
        <Modal
          title={detailDoc.filename ?? detailDoc.name ?? 'Detalhes do documento'}
          onClose={() => setDetailDoc(null)}
        >
          {detailLoading && <p className="muted">Carregando…</p>}
          {detailError && (
            <p className="alert alert-error">{detailError}</p>
          )}
          {!detailLoading && !detailError && (
            <>
              <dl className="detail-list">
                <dt>Tipo</dt>
                <dd>{detailDoc.doc_type}</dd>
                <dt>Status</dt>
                <dd>
                  <StatusBadge status={detailDoc.status} />
                </dd>
                <dt>Upload</dt>
                <dd>{formatDate(detailDoc.uploaded_at ?? detailDoc.created_at)}</dd>
                <dt>Palavras</dt>
                <dd>{detailDoc.word_count ?? '—'}</dd>
                {detailDoc.error_message && (
                  <>
                    <dt>Erro</dt>
                    <dd>{detailDoc.error_message}</dd>
                  </>
                )}
              </dl>
              <h3>Extrações ({extractions.length})</h3>
              {extractions.length === 0 ? (
                <p className="muted">Nenhuma extração disponível.</p>
              ) : (
                <div className="table-scroll">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Tipo</th>
                        <th>Sujeito</th>
                        <th>Ação</th>
                        <th>Prazo</th>
                        <th>Base legal</th>
                        <th>Penalidade</th>
                      </tr>
                    </thead>
                    <tbody>
                      {extractions.map((item, index) => (
                        <tr key={item.id ?? index}>
                          <td>{item.tipo ?? '—'}</td>
                          <td>{item.sujeito ?? '—'}</td>
                          <td>{item.acao ?? item.action ?? '—'}</td>
                          <td>{item.prazo ?? '—'}</td>
                          <td>{item.base_legal ?? '—'}</td>
                          <td>{item.penalidade ?? '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </Modal>
      )}
    </div>
  )
}
