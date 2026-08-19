import type { DocumentStatus } from '../api/types'

const LABELS: Record<DocumentStatus, string> = {
  queued: 'Na fila',
  processing: 'Processando',
  done: 'Concluído',
  error: 'Erro',
}

export default function StatusBadge({ status }: { status: DocumentStatus }) {
  return (
    <span className={`status-badge status-${status}`}>
      <span className="status-dot" aria-hidden="true" />
      {LABELS[status] ?? status}
    </span>
  )
}
