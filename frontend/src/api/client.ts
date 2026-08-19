const TOKEN_KEY = 'normaextractor_token'
const API_BASE = '/api/v1'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'ApiError'
  }
}

function handleUnauthorized(): never {
  clearToken()
  window.location.assign('/login')
  throw new ApiError(401, 'Sessão expirada')
}

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json()
    if (typeof body?.detail === 'string') return body.detail
    if (Array.isArray(body?.detail)) {
      return body.detail
        .map((d: { msg?: string }) => d?.msg)
        .filter(Boolean)
        .join('; ')
    }
    if (typeof body?.message === 'string') return body.message
  } catch {
    // corpo não é JSON
  }
  return `Erro ${response.status}`
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken()
  const headers = new Headers(options.headers)
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (response.status === 401) handleUnauthorized()
  if (!response.ok) {
    throw new ApiError(response.status, await extractErrorMessage(response))
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

export function apiJson<T>(
  path: string,
  method: string,
  body: unknown,
): Promise<T> {
  return apiFetch<T>(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export function buildQuery(params: object): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value))
    }
  }
  const qs = search.toString()
  return qs ? `?${qs}` : ''
}
