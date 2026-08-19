import { useCallback, useEffect, useRef, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { apiFetch, buildQuery, getToken, ApiError } from '../api/client'
import type { DocumentItem } from '../api/types'
import StatusBadge from '../components/StatusBadge'

const ACCEPTED = '.pdf,.docx,.txt'
const MAX_BYTES = 20 * 1024 * 1024

interface UploadState {
  progress: number
  fileName: string
}

function uploadFile(
  file: File,
  onProgress: (percent: number) => void,
): Promise<DocumentItem> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/v1/documents/upload')
    const token = getToken()
    if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        onProgress(Math.round((event.loaded / event.total) * 100))
      }
    }

    xhr.onload = () => {
      if (xhr.status === 401) {
        window.location.assign('/login')
        reject(new ApiError(401, 'Sessão expirada'))
        return
      }
      let body: { detail?: string | { msg?: string }[] } & DocumentItem
      try {
        body = JSON.parse(xhr.responseText)
      } catch {
        reject(new ApiError(xhr.status, 'Resposta inválida do servidor'))
        return
      }
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(body)
        return
      }
      const detail = body?.detail
      const message =
        typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((d) => d?.msg).filter(Boolean).join('; ')
            : `Erro ${xhr.status}`
      reject(new ApiError(xhr.status, message))
    }

    xhr.onerror = () => reject(new ApiError(0, 'Falha de rede no envio'))

    const form = new FormData()
    form.append('file', file)
    xhr.send(form)
  })
}

export default function Upload() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState<UploadState | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [confirmation, setConfirmation] = useState<DocumentItem | null>(null)
  const [recent, setRecent] = useState<DocumentItem[]>([])

  const loadRecent = useCallback(async () => {
    try {
      const data = await apiFetch<DocumentItem[]>(
        `/documents${buildQuery({})}`,
      )
      setRecent(Array.isArray(data) ? data.slice(0, 8) : [])
    } catch {
      // lista recente é secundária; erros não devem bloquear o upload
    }
  }, [])

  useEffect(() => {
    void loadRecent()
  }, [loadRecent])

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null
    setError(null)
    setConfirmation(null)
    if (selected && selected.size > MAX_BYTES) {
      setError('Arquivo excede o limite de 20MB.')
      setFile(null)
      event.target.value = ''
      return
    }
    setFile(selected)
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!file || uploading) return
    setError(null)
    setConfirmation(null)
    setUploading({ progress: 0, fileName: file.name })
    try {
      const created = await uploadFile(file, (progress) =>
        setUploading({ progress, fileName: file.name }),
      )
      setConfirmation(created)
      setFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      void loadRecent()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha no envio do arquivo.')
    } finally {
      setUploading(null)
    }
  }

  return (
    <div className="page">
      <h1>Upload de documento</h1>
      <p className="page-subtitle">
        Envie documentos normativos em PDF, DOCX ou TXT (até 20MB).
      </p>

      <form className="card upload-form" onSubmit={handleSubmit}>
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED}
          onChange={handleFileChange}
          aria-label="Selecionar arquivo"
        />

        {uploading && (
          <div className="progress">
            <div
              className="progress-bar"
              style={{ width: `${uploading.progress}%` }}
            />
            <span className="progress-label">
              Enviando {uploading.fileName}… {uploading.progress}%
            </span>
          </div>
        )}

        {error && (
          <p className="alert alert-error" role="alert">
            {error}
          </p>
        )}

        {confirmation && (
          <p className="alert alert-success" role="status">
            Documento "{confirmation.filename ?? confirmation.name}" enviado com
            sucesso. Status: <StatusBadge status={confirmation.status ?? 'queued'} />
          </p>
        )}

        <button
          type="submit"
          className="btn btn-primary"
          disabled={!file || uploading !== null}
        >
          {uploading ? 'Enviando…' : 'Enviar'}
        </button>
      </form>

      <section className="card">
        <h2>Documentos recentes</h2>
        {recent.length === 0 ? (
          <p className="muted">Nenhum documento enviado ainda.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Tipo</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recent.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.filename ?? doc.name}</td>
                  <td>{doc.doc_type}</td>
                  <td>
                    <StatusBadge status={doc.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}
