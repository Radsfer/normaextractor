export type DocumentStatus = 'queued' | 'processing' | 'done' | 'error'
export type DocType = 'PDF' | 'DOCX' | 'TXT'

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface DocumentItem {
  id: string
  filename: string
  name?: string
  doc_type: DocType
  status: DocumentStatus
  word_count: number | null
  uploaded_at: string
  created_at?: string
  error_message?: string | null
}

export interface Extraction {
  id?: string
  tipo: string | null
  sujeito: string | null
  acao?: string | null
  action?: string | null
  prazo: string | null
  base_legal: string | null
  penalidade: string | null
}

export interface Metrics {
  coverage: number
  consistency: number
  avg_latency_seconds: number
}

export interface ChatSource {
  chunk_id: string
  document_id: string
  document_name: string
  page: number | null
  text_preview: string
}

export interface DocumentFilters {
  status?: DocumentStatus | ''
  doc_type?: DocType | ''
  date_from?: string
  date_to?: string
}

export interface MetricsFilters {
  document_id?: string
  date_from?: string
  date_to?: string
  doc_type?: DocType | ''
}
