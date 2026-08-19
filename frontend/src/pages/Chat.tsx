import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import type { EventSourceMessage } from '@microsoft/fetch-event-source'
import { apiFetch, buildQuery, getToken, ApiError } from '../api/client'
import type { ChatSource, DocumentItem } from '../api/types'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: ChatSource[]
  error?: string
  streaming?: boolean
}

interface StreamEvent {
  type: 'token' | 'sources' | 'done' | 'error'
  content?: string
  sources?: ChatSource[]
  message?: string
}

let idCounter = 0
function nextId(): string {
  idCounter += 1
  return `msg-${Date.now()}-${idCounter}`
}

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [query, setQuery] = useState('')
  const [selectedDocs, setSelectedDocs] = useState<string[]>([])
  const [busy, setBusy] = useState(false)
  const [clientError, setClientError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    apiFetch<DocumentItem[]>(`/documents${buildQuery({})}`)
      .then((data) => setDocuments(Array.isArray(data) ? data : []))
      .catch(() => {
        /* filtro de documentos é opcional */
      })
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function toggleDocument(id: string) {
    setSelectedDocs((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id],
    )
  }

  async function handleSend(event: FormEvent) {
    event.preventDefault()
    const trimmed = query.trim()
    if (trimmed.length < 5 || trimmed.length > 500) {
      setClientError('A consulta deve ter entre 5 e 500 caracteres.')
      return
    }
    setClientError(null)

    const userMessage: ChatMessage = {
      id: nextId(),
      role: 'user',
      content: trimmed,
    }
    const assistantId = nextId()
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      streaming: true,
    }
    setMessages((current) => [...current, userMessage, assistantMessage])
    setQuery('')
    setBusy(true)

    const controller = new AbortController()
    abortRef.current = controller
    const token = getToken()
    const accumulated = { content: '' }

    function updateAssistant(update: Partial<ChatMessage>) {
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId ? { ...message, ...update } : message,
        ),
      )
    }

    try {
      await fetchEventSource('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          query: trimmed,
          document_ids: selectedDocs.length > 0 ? selectedDocs : undefined,
        }),
        signal: controller.signal,
        openWhenHidden: true,
        onopen: async (response) => {
          if (response.status === 401) {
            window.location.assign('/login')
            throw new ApiError(401, 'Sessão expirada')
          }
          if (!response.ok) {
            let message = `Erro ${response.status}`
            try {
              const body = await response.json()
              if (typeof body?.detail === 'string') message = body.detail
            } catch {
              // mantém mensagem padrão
            }
            throw new ApiError(response.status, message)
          }
        },
        onmessage: (event: EventSourceMessage) => {
          if (!event.data) return
          let parsed: StreamEvent
          try {
            parsed = JSON.parse(event.data) as StreamEvent
          } catch {
            return
          }
          if (parsed.type === 'token' && parsed.content) {
            accumulated.content += parsed.content
            updateAssistant({ content: accumulated.content })
          } else if (parsed.type === 'sources') {
            updateAssistant({ sources: parsed.sources ?? [] })
          } else if (parsed.type === 'done') {
            updateAssistant({ streaming: false })
          } else if (parsed.type === 'error') {
            updateAssistant({
              error: parsed.message ?? 'Erro ao gerar resposta.',
              streaming: false,
            })
          }
        },
        onclose: () => {
          updateAssistant({ streaming: false })
        },
        onerror: (err) => {
          updateAssistant({ streaming: false })
          throw err
        },
      })
    } catch (err) {
      if (controller.signal.aborted) {
        updateAssistant({ streaming: false })
      } else {
        updateAssistant({
          error: err instanceof Error ? err.message : 'Falha de conexão.',
          streaming: false,
        })
      }
    } finally {
      setBusy(false)
      abortRef.current = null
    }
  }

  function handleStop() {
    abortRef.current?.abort()
  }

  return (
    <div className="page chat-page">
      <h1>Chat</h1>
      <p className="page-subtitle">
        Pergunte sobre seus documentos normativos com respostas baseadas nas fontes.
      </p>

      {documents.length > 0 && (
        <details className="card doc-filter">
          <summary>Restringir consulta a documentos ({selectedDocs.length} selecionados)</summary>
          <div className="doc-filter-options">
            {documents.map((doc) => (
              <label key={doc.id} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={selectedDocs.includes(doc.id)}
                  onChange={() => toggleDocument(doc.id)}
                />
                {doc.filename ?? doc.name}
              </label>
            ))}
          </div>
        </details>
      )}

      <div className="chat-thread card">
        {messages.length === 0 ? (
          <p className="muted chat-empty">
            Digite uma pergunta para começar.
          </p>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`chat-message chat-${message.role}`}>
              <div className="chat-bubble">
                {message.content ? (
                  <p>{message.content}</p>
                ) : message.streaming ? (
                  <span className="generating">gerando…</span>
                ) : null}
                {message.error && (
                  <p className="chat-error">{message.error}</p>
                )}
                {message.sources && message.sources.length > 0 && (
                  <details className="chat-sources">
                    <summary>Fontes ({message.sources.length})</summary>
                    <ul>
                      {message.sources.map((source, index) => (
                        <li key={source.chunk_id ?? index}>
                          <strong>{source.document_name}</strong>
                          {source.page != null && <> · pág. {source.page}</>}
                          <p className="muted">{source.text_preview}</p>
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input" onSubmit={handleSend}>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Digite sua pergunta (5 a 500 caracteres)…"
          rows={2}
          maxLength={500}
        />
        <div className="chat-actions">
          {busy ? (
            <button type="button" className="btn btn-danger" onClick={handleStop}>
              Parar
            </button>
          ) : (
            <button
              type="submit"
              className="btn btn-primary"
              disabled={query.trim().length < 5 || query.trim().length > 500}
            >
              Enviar
            </button>
          )}
        </div>
      </form>

      {clientError && (
        <p className="alert alert-error" role="alert">
          {clientError}
        </p>
      )}
    </div>
  )
}
