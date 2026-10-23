// BookForge for Veneer: choose and order a project's chapters, fill in the book's details, and
// make an EPUB with a BookForge server. Everything goes through @veneer/api (AD-3): files through
// api.vault, the server through api.net.fetch, the token through api.secrets, and the UI is one
// host-drawn modal surface (AD-4).
import { splitFrontmatter, type FormField, type FormValue, type ItemsView, type PluginApi, type VaultRenamedEvent } from '@veneer/api'
import {
  EMPTY_DETAILS,
  chapterBody,
  folderOf,
  move,
  prefillDetails,
  reconcile,
  renamed,
  stemOf,
  uploadNames,
  type BookDetails,
  type ChapterChoice
} from './chapters.js'
import { ServerProblem, download, jobStatus, sentence, startJob, themes as fetchThemes, type Server, type Theme } from './server.js'

const SURFACE = 'bookforge:book'
const SERVER_SETTING = 'bookforge:server'
const TOKEN_SECRET = 'api-token'
const CHAPTERS_KEY = 'chapters'
const DETAILS_KEY = 'details'

/** How often a job's status is asked, and for how long; tests shorten them. */
export const timing = { pollMs: 1000, maxPolls: 600 }

const DEFAULT_THEMES: Theme[] = [
  { id: 'modern', label: 'Modern' },
  { id: 'classic', label: 'Classic' },
  { id: 'minimal', label: 'Minimal' }
]

type DetailField = keyof BookDetails

const IDLE_NOTE = 'Order the chapters on the left (drag, or Alt+Up and Alt+Down); Enter includes or leaves one out.'

let dispose: (() => void) | null = null

export function onload(api: PluginApi): void {
  let chapters: ChapterChoice[] = []
  let details: BookDetails = { ...EMPTY_DETAILS }
  let themeChoices: Theme[] = DEFAULT_THEMES
  let hasToken = false
  // What the writer is typing in the token field; never stored outside api.secrets.
  let tokenDraft = ''
  let errors: Partial<Record<DetailField, string>> = {}
  let note = IDLE_NOTE
  let busy = false
  let ready = false
  let selected: string | undefined
  let loading: Promise<void> | null = null
  let unloaded = false

  const inProject = (): boolean => api.workspace.current().project?.kind === 'project'

  const isChoice = (value: unknown): value is ChapterChoice =>
    typeof value === 'object' &&
    value !== null &&
    typeof (value as ChapterChoice).path === 'string' &&
    typeof (value as ChapterChoice).include === 'boolean'

  const storedDetails = (value: unknown): BookDetails | null => {
    if (typeof value !== 'object' || value === null) return null
    const out = { ...EMPTY_DETAILS }
    for (const key of Object.keys(out) as DetailField[]) {
      const v = (value as Record<string, unknown>)[key]
      if (typeof v === 'string') out[key] = v
    }
    return out
  }

  /** Reads the project's documents and this plugin's stored choices. */
  const load = (): Promise<void> => {
    loading ??= (async () => {
      try {
        hasToken = (await api.secrets.get(TOKEN_SECRET)) !== null
        if (!inProject()) {
          chapters = []
          return
        }
        const paths = (await api.vault.list()).filter((e) => e.kind === 'file').map((e) => e.path)
        const stored = await api.projectData.read(CHAPTERS_KEY)
        chapters = reconcile(Array.isArray(stored) ? stored.filter(isChoice) : [], paths)
        const saved = storedDetails(await api.projectData.read(DETAILS_KEY))
        if (saved !== null) details = saved
        else {
          const first = chapters.find((c) => c.include)
          const text = first === undefined ? '' : await api.vault.read(first.path).catch(() => '')
          details = prefillDetails(splitFrontmatter(text).yaml, api.workspace.current().project?.name ?? null)
        }
        ready = true
      } finally {
        loading = null
      }
    })()
    return loading
  }

  const chapterList = (): ItemsView => {
    let n = 0
    const included = chapters.filter((c) => c.include).length
    return {
      kind: 'list',
      reorderable: true,
      selectedId: selected,
      items: chapters.map((c) => {
        const folder = folderOf(c.path)
        if (c.include) n += 1
        return {
          id: c.path,
          label: c.include ? `${n}. ${stemOf(c.path)}` : stemOf(c.path),
          detail: c.include ? folder || undefined : folder === '' ? 'Left out' : `${folder} · left out`
        }
      }),
      empty: { text: ready ? 'This project has no documents yet.' : 'Reading the project…' },
      note: chapters.length === 0 ? undefined : `${included} of ${chapters.length} documents in the book.`
    }
  }

  const detailFields = (): FormField[] => {
    const choices = themeChoices.some((t) => t.id === details.theme)
      ? themeChoices
      : [...themeChoices, { id: details.theme, label: details.theme }]
    const text = (id: DetailField, label: string, extra: Partial<FormField> = {}): FormField => ({
      id,
      type: 'text',
      label,
      value: details[id],
      error: errors[id],
      ...extra
    })
    return [
      text('title', 'Title'),
      text('author', 'Author'),
      text('language', 'Language', { hint: 'A language code, such as en or fr.' }),
      { id: 'description', type: 'longtext', label: 'Description', value: details.description },
      text('publisher', 'Publisher'),
      {
        id: 'theme',
        type: 'choice',
        label: 'Theme',
        value: details.theme,
        options: choices.map((t) => ({ value: t.id, label: t.label }))
      },
      {
        id: 'token',
        type: 'text',
        label: 'API token',
        value: tokenDraft,
        placeholder: hasToken ? 'Saved in the keychain' : 'None',
        hint: 'Only if your server needs one. Kept in the system keychain, never in the project.'
      }
    ]
  }

  const render = (): void => {
    if (unloaded) return
    if (!inProject()) {
      api.surfaces.setView(SURFACE, {
        kind: 'list',
        items: [],
        empty: { text: 'Open a project folder to make a book from its documents.' }
      })
      return
    }
    api.surfaces.setView(SURFACE, {
      kind: 'split',
      list: chapterList(),
      detail: { kind: 'form', fields: detailFields(), note, submitLabel: busy ? undefined : 'Make EPUB' }
    })
  }

  const refresh = async (): Promise<void> => {
    await load()
    render()
  }

  const saveChapters = async (next: ChapterChoice[]): Promise<void> => {
    chapters = next
    render()
    if (inProject()) await api.projectData.write(CHAPTERS_KEY, chapters)
  }

  const setNote = (text: string): void => {
    note = text
    render()
  }

  const fail = (message: string): void => {
    setNote(message)
    api.notify({ message, action: { label: 'Show', surface: SURFACE } })
  }

  const server = async (): Promise<Server> => {
    const raw = await api.settings.get(SERVER_SETTING)
    const base = (typeof raw === 'string' ? raw : '').trim().replace(/\/+$/, '')
    if (base === '') throw new ServerProblem('Set the BookForge server address in Settings, BookForge.')
    return { base, token: await api.secrets.get(TOKEN_SECRET) }
  }

  const wait = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms))

  /** The whole job: upload, poll, download, save. Reports by note and notice, never by throwing. */
  const makeEpub = async (): Promise<void> => {
    if (busy) {
      api.surfaces.show(SURFACE)
      return
    }
    if (!inProject()) {
      api.notify({ message: 'Open a project folder to make an EPUB from its documents.' })
      return
    }
    await api.vault.saveNow()
    if (!ready) await load()
    const book = chapters.filter((c) => c.include)
    errors = {}
    if (details.title.trim() === '') errors.title = 'A book needs a title.'
    if (details.author.trim() === '') errors.author = 'A book needs an author.'
    if (book.length === 0) {
      note = 'Include at least one chapter.'
    }
    if (Object.keys(errors).length > 0 || book.length === 0) {
      render()
      api.surfaces.show(SURFACE)
      return
    }
    busy = true
    try {
      const target = await server()
      setNote('Checking the BookForge server…')
      const listed = await fetchThemes(api, target)
      if (listed.length > 0) themeChoices = listed
      setNote(`Sending ${book.length} ${book.length === 1 ? 'chapter' : 'chapters'} to BookForge…`)
      const names = uploadNames(book.map((c) => c.path))
      const files: { name: string; text: string }[] = []
      for (const chapter of book) {
        const text = await api.vault.read(chapter.path)
        files.push({ name: names.get(chapter.path) as string, text: chapterBody(chapter.path, text, names) })
      }
      const jobId = await startJob(api, target, { ...details, title: details.title.trim(), author: details.author.trim() }, files)
      for (let i = 0; i < timing.maxPolls && !unloaded; i++) {
        const status = await jobStatus(api, target, jobId)
        if (status.status === 'failed') {
          throw new ServerProblem(sentence(`BookForge couldn't make the EPUB: ${status.error ?? 'no reason given'}.`))
        }
        if (status.status === 'completed') {
          if (status.downloadUrl === null) throw new ServerProblem('BookForge finished but sent no EPUB.')
          setNote('Downloading the EPUB…')
          const data = await download(api, target, status.downloadUrl)
          const result = await api.export.saveAs({
            suggestedName: `${details.title.trim().replace(/[\\/:*?"<>|]+/g, '-')}.epub`,
            data,
            filters: [{ name: 'EPUB', extensions: ['epub'] }]
          })
          if (result.saved) {
            const message = sentence(`Saved ${result.name ?? 'the EPUB'}.`)
            setNote(message)
            api.notify({ message })
          } else setNote("The EPUB was made but not saved. Make it again to save it.")
          return
        }
        setNote(status.status === 'pending' ? 'BookForge has the job and will start soon…' : 'BookForge is making the EPUB…')
        await wait(timing.pollMs)
      }
      if (!unloaded) throw new ServerProblem('BookForge is taking too long; the job may still finish on the server.')
    } catch (err) {
      if (err instanceof ServerProblem) fail(err.message)
      else fail(sentence(`The EPUB couldn't be made: ${err instanceof Error ? err.message : String(err)}`))
    } finally {
      busy = false
      render()
    }
  }

  api.commands.handle('bookforge:make-epub', () => makeEpub())

  api.commands.handle('bookforge:forget-token', async () => {
    await api.secrets.delete(TOKEN_SECRET)
    hasToken = false
    render()
  })

  api.surfaces.onRefresh(SURFACE, () => refresh())

  // Enter or a click on a chapter includes or leaves it out; the modal stays open.
  api.surfaces.onOpen(SURFACE, (path) => {
    selected = path
    return saveChapters(chapters.map((c) => (c.path === path ? { ...c, include: !c.include } : c)))
  })

  api.surfaces.onReorder(SURFACE, ({ movedId, beforeId }) => {
    selected = movedId
    return saveChapters(move(chapters, movedId, beforeId))
  })

  const applyField = (fieldId: string, value: FormValue): boolean => {
    if (fieldId === 'token') {
      tokenDraft = typeof value === 'string' ? value : ''
      return false
    }
    if (!(fieldId in details) || typeof value !== 'string') return false
    details = { ...details, [fieldId]: value }
    if (value.trim() !== '') delete errors[fieldId as DetailField]
    return true
  }

  api.surfaces.onFormChange(SURFACE, async (fieldId, value) => {
    const changed = applyField(fieldId, value)
    render()
    if (changed && inProject()) await api.projectData.write(DETAILS_KEY, details)
  })

  api.surfaces.onFormSubmit(SURFACE, async (values) => {
    for (const [id, value] of Object.entries(values)) applyField(id, value)
    if (tokenDraft.trim() !== '') {
      await api.secrets.set(TOKEN_SECRET, tokenDraft.trim())
      hasToken = true
    }
    tokenDraft = ''
    if (inProject()) await api.projectData.write(DETAILS_KEY, details)
    await makeEpub()
  })

  const following = api.events.on('vault:renamed', async (event) => {
    const { from, to, kind } = event as VaultRenamedEvent
    if (!ready) return
    await saveChapters(renamed(chapters, from, to, kind))
  })

  const switching = api.events.on('project:switched', () => {
    ready = false
    chapters = []
    details = { ...EMPTY_DETAILS }
    errors = {}
    selected = undefined
    if (!busy) note = IDLE_NOTE
    return refresh()
  })

  dispose = () => {
    unloaded = true
    following.dispose()
    switching.dispose()
  }

  // The first view; showing the surface is what activated the plugin.
  render()
  void refresh()
}

export function onunload(): void {
  dispose?.()
  dispose = null
}
