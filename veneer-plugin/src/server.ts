// The BookForge server's REST API, through api.net.fetch only (AD-6). Every failure becomes a
// ServerProblem whose message is one plain sentence for a notice.
import { isVeneerError, type NetFormField, type NetRequest, type NetResponse, type PluginApi } from '@veneer/api'
import type { BookDetails } from './chapters.js'

export interface Server {
  /** The server's address with no trailing slash, e.g. `http://localhost:8000`. */
  base: string
  token: string | null
}

export interface Theme {
  id: string
  label: string
}

export interface JobStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error: string | null
  downloadUrl: string | null
}

/** A failure the writer reads as is. */
export class ServerProblem extends Error {}

/** The longest notice the kernel takes (MAX_NOTICE_MESSAGE). */
const NOTICE_LENGTH = 200

/** One line, short enough for a notice. */
export function sentence(text: string): string {
  const line = text.replace(/\s+/g, ' ').trim()
  return line.length <= NOTICE_LENGTH ? line : `${line.slice(0, NOTICE_LENGTH - 1)}…`
}

function hostOf(base: string): string {
  try {
    return new URL(base).host || base
  } catch {
    return base
  }
}

/** What went wrong reaching the server, in the writer's words. */
export function networkProblem(err: unknown, base: string): string {
  const host = hostOf(base)
  if (!isVeneerError(err)) return sentence(`BookForge couldn't reach ${host}.`)
  switch (err.code) {
    case 'net/blocked':
      return sentence(`${host} is a local address. Allow ${host} for BookForge in Settings, Plugins, then try again.`)
    case 'plugin/declined':
      return sentence(`The connection to ${host} wasn't allowed, so nothing was sent.`)
    case 'offline':
    case 'timeout':
      return sentence(`The BookForge server at ${host} isn't answering. Check that it is running.`)
    case 'net/invalid':
      return sentence(`The BookForge server address isn't a web address. Fix it in Settings, BookForge.`)
    case 'net/too-large':
      return 'The book is too large to send to BookForge.'
    default:
      return sentence(`BookForge couldn't reach ${host}: ${err.message}`)
  }
}

/** The server's own explanation of a refused request: FastAPI's `detail`, a string or a list. */
export function answerProblem(response: NetResponse): string {
  if (response.status === 401) {
    return 'The BookForge server needs an API token, or refused the one saved. Enter it in the book details.'
  }
  let detail = ''
  try {
    const body = JSON.parse(response.text) as { detail?: unknown }
    if (typeof body.detail === 'string') detail = body.detail
    else if (Array.isArray(body.detail)) {
      detail = body.detail
        .map((d: unknown) => (typeof d === 'object' && d !== null && 'msg' in d ? String(d.msg) : ''))
        .filter((m) => m !== '')
        .join('; ')
    }
  } catch {
    // Not JSON: fall back to the status alone.
  }
  return sentence(detail === '' ? `The BookForge server answered ${response.status}.` : `BookForge: ${detail}`)
}

async function send(api: PluginApi, server: Server, request: NetRequest): Promise<NetResponse> {
  const headers: Record<string, string> = { ...request.headers }
  if (server.token !== null) headers['Authorization'] = `Bearer ${server.token}`
  let response: NetResponse
  try {
    response = await api.net.fetch({ ...request, headers })
  } catch (err) {
    throw new ServerProblem(networkProblem(err, server.base))
  }
  if (!response.ok) throw new ServerProblem(answerProblem(response))
  return response
}

function json(response: NetResponse): unknown {
  try {
    return JSON.parse(response.text) as unknown
  } catch {
    throw new ServerProblem("The BookForge server's answer wasn't readable. Is the address right?")
  }
}

/** The server's themes; also the first call of a make, so a down server or a bad token shows before any upload. */
export async function themes(api: PluginApi, server: Server): Promise<Theme[]> {
  const body = json(await send(api, server, { url: `${server.base}/api/v1/themes`, headers: { Accept: 'application/json' } }))
  if (!Array.isArray(body)) return []
  return body.filter(
    (t): t is Theme => typeof t === 'object' && t !== null && typeof t.id === 'string' && typeof t.label === 'string'
  )
}

/** Starts a job from the chapters (upload name and text, in book order) and resolves to its ID. */
export async function startJob(
  api: PluginApi,
  server: Server,
  details: BookDetails,
  chapters: readonly { name: string; text: string }[]
): Promise<string> {
  const encoder = new TextEncoder()
  const form: NetFormField[] = [
    { name: 'title', value: details.title },
    { name: 'author', value: details.author },
    { name: 'theme', value: details.theme },
    { name: 'language', value: details.language },
    { name: 'keep_order', value: 'true' }
  ]
  if (details.description !== '') form.push({ name: 'description', value: details.description })
  if (details.publisher !== '') form.push({ name: 'publisher', value: details.publisher })
  for (const chapter of chapters) {
    form.push({ name: 'files', file: { name: chapter.name, type: 'text/markdown', data: encoder.encode(chapter.text) } })
  }
  const body = json(
    await send(api, server, { url: `${server.base}/api/v1/generate/files`, method: 'POST', body: { form } })
  ) as { job_id?: unknown }
  if (typeof body.job_id !== 'string') throw new ServerProblem("The BookForge server didn't start a job.")
  return body.job_id
}

export async function jobStatus(api: PluginApi, server: Server, jobId: string): Promise<JobStatus> {
  const body = json(
    await send(api, server, { url: `${server.base}/api/v1/status/${encodeURIComponent(jobId)}` })
  ) as { status?: unknown; error_message?: unknown; download_url?: unknown }
  const status = body.status
  if (status !== 'pending' && status !== 'processing' && status !== 'completed' && status !== 'failed') {
    throw new ServerProblem("The BookForge server's job status wasn't readable.")
  }
  return {
    status,
    error: typeof body.error_message === 'string' ? body.error_message : null,
    downloadUrl: typeof body.download_url === 'string' ? body.download_url : null
  }
}

/** The finished EPUB's bytes. `downloadUrl` is the server's path, `/api/v1/download/<id>`. */
export async function download(api: PluginApi, server: Server, downloadUrl: string): Promise<Uint8Array> {
  // Only a path on the same server: the token goes nowhere else.
  if (!downloadUrl.startsWith('/') || downloadUrl.startsWith('//')) {
    throw new ServerProblem("The BookForge server's download address wasn't on the same server.")
  }
  const response = await send(api, server, { url: `${server.base}${downloadUrl}`, as: 'bytes' })
  if (response.data === undefined || response.data.byteLength === 0) {
    throw new ServerProblem('The BookForge server sent an empty EPUB.')
  }
  return response.data
}
