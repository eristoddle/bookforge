import { beforeEach, describe, expect, it } from 'vitest'
import type { FormView, ItemsView, NetFile, NetForm, NetResponse, PluginManifest, SplitView } from '@veneer/api'
import { createFakeHost, type FakeHost } from '@veneer/api/testing'
import manifestJson from '../manifest.json'
import * as plugin from './index.js'

const manifest = manifestJson as PluginManifest
const SURFACE = 'bookforge:book'

const FILES = {
  'chapters/one.md': '---\ntitle: The Storm\nauthor: Mara Lin\n---\n# The Storm\n\nOn to [two](two.md#harbor).\n',
  'chapters/two.md': '# The Harbor\n\nBack to [one](one.md). A [note](../notes/idea.md).\n',
  'notes/idea.md': 'An idea.\n'
}

const THEMES = '[{"id":"modern","label":"Modern"},{"id":"sepia","label":"Sepia"}]'
const EPUB = new Uint8Array([0x50, 0x4b, 0x03, 0x04])

function host(netReplies: (string | Partial<NetResponse>)[] = [], files: Record<string, string> = FILES): FakeHost {
  return createFakeHost(manifest, plugin, {
    project: { name: 'Storm Book', kind: 'project' },
    files: { ...files },
    netReplies
  })
}

async function started(fake: FakeHost): Promise<FakeHost> {
  await fake.load()
  await fake.refreshSurface(SURFACE)
  return fake
}

function split(fake: FakeHost): SplitView {
  const view = fake.views.get(SURFACE)
  if (view?.kind !== 'split') throw new Error(`expected a split view, got ${view?.kind}`)
  return view
}
const rows = (fake: FakeHost) => (split(fake).list as ItemsView).items
const form = (fake: FakeHost) => split(fake).detail as FormView
const field = (fake: FakeHost, id: string) => form(fake).fields.find((f) => f.id === id)

const ok = (text: string): Partial<NetResponse> => ({ status: 200, ok: true, text })
const fullJob = (): (string | Partial<NetResponse>)[] => [
  ok(THEMES),
  ok('{"job_id":"j1","status_url":"/api/v1/status/j1"}'),
  ok('{"status":"processing"}'),
  ok('{"status":"completed","download_url":"/api/v1/download/j1"}'),
  { status: 200, ok: true, text: '', data: EPUB }
]

beforeEach(() => {
  plugin.timing.pollMs = 0
  plugin.timing.maxPolls = 600
})

describe('the chapter list', () => {
  it('lists the project documents in path order, all included, reorderable', async () => {
    const fake = await started(host())
    const list = split(fake).list as ItemsView
    expect(list.reorderable).toBe(true)
    expect(list.items.map((r) => [r.id, r.label, r.detail])).toEqual([
      ['chapters/one.md', '1. one', 'chapters'],
      ['chapters/two.md', '2. two', 'chapters'],
      ['notes/idea.md', '3. idea', 'notes']
    ])
  })

  it('leaves a chapter out and back in on open, and keeps the choice in project data', async () => {
    const fake = await started(host())
    await fake.openItem(SURFACE, 'notes/idea.md')
    expect(rows(fake)[2]).toMatchObject({ label: 'idea', detail: 'notes · left out' })
    expect(JSON.parse(fake.projectData.get('chapters') ?? '[]')).toContainEqual({ path: 'notes/idea.md', include: false })
    await fake.openItem(SURFACE, 'notes/idea.md')
    expect(rows(fake)[2]?.label).toBe('3. idea')
  })

  it('reorders, and the order survives a reload', async () => {
    const fake = await started(host())
    await fake.reorder(SURFACE, { movedId: 'chapters/two.md', beforeId: 'chapters/one.md', parentId: null })
    expect(rows(fake).map((r) => r.id)).toEqual(['chapters/two.md', 'chapters/one.md', 'notes/idea.md'])

    const again = host()
    for (const [key, value] of fake.projectData) again.projectData.set(key, value)
    await started(again)
    expect(rows(again).map((r) => r.id)).toEqual(['chapters/two.md', 'chapters/one.md', 'notes/idea.md'])
  })

  it('follows a renamed folder', async () => {
    const fake = await started(host())
    await fake.emit({ type: 'vault:renamed', from: 'chapters', to: 'book', kind: 'folder' } as never)
    expect(rows(fake)[0]?.id).toBe('book/one.md')
  })

  it('asks for a project folder when a loose file is open', async () => {
    const fake = createFakeHost(manifest, plugin, { project: { name: 'x.md', kind: 'loose' }, openPath: 'x.md', text: '# X' })
    await started(fake)
    const view = fake.views.get(SURFACE) as ItemsView
    expect(view.items).toEqual([])
    expect(view.empty?.text).toMatch(/project folder/)
  })
})

describe('the book details', () => {
  it('prefills from the first chapter and the project name', async () => {
    const fake = await started(host())
    expect(field(fake, 'title')?.value).toBe('Storm Book')
    expect(field(fake, 'author')?.value).toBe('Mara Lin')
    expect(field(fake, 'theme')?.options?.map((o) => o.value)).toEqual(['modern', 'classic', 'minimal'])
    expect(form(fake).submitLabel).toBe('Make EPUB')
  })

  it('keeps edits in project data', async () => {
    const fake = await started(host())
    await fake.formChange(SURFACE, 'title', 'The Storm')
    await fake.formChange(SURFACE, 'theme', 'classic')
    expect(JSON.parse(fake.projectData.get('details') ?? '{}')).toMatchObject({ title: 'The Storm', theme: 'classic' })
    expect(field(fake, 'title')?.value).toBe('The Storm')
  })

  it('puts the token in secrets only, then clears the field', async () => {
    const fake = await started(host())
    await fake.formChange(SURFACE, 'token', 'tok-123')
    expect(field(fake, 'token')?.value).toBe('tok-123')
    await fake.formSubmit(SURFACE, { token: 'tok-123' })
    expect(fake.secrets.get('api-token')).toBe('tok-123')
    expect([...fake.projectData.values()].join()).not.toContain('tok-123')
    expect(field(fake, 'token')).toMatchObject({ value: '', placeholder: 'Saved in the keychain' })

    await fake.run('bookforge:forget-token')
    expect(fake.secrets.has('api-token')).toBe(false)
    expect(field(fake, 'token')?.placeholder).toBe('None')
  })

  it('refuses to make a book without an author, without touching the network', async () => {
    const fake = await started(host(fullJob(), { 'one.md': '# One\n' }))
    await fake.run('bookforge:make-epub')
    expect(field(fake, 'author')?.error).toBe('A book needs an author.')
    expect(fake.netRequests).toEqual([])
    expect(fake.shown).toContain(SURFACE)
  })
})

describe('making the EPUB', () => {
  it('uploads the chosen chapters in order, polls, downloads, and saves', async () => {
    const fake = await started(host(fullJob()))
    await fake.openItem(SURFACE, 'notes/idea.md')
    await fake.reorder(SURFACE, { movedId: 'chapters/two.md', beforeId: 'chapters/one.md', parentId: null })
    await fake.run('bookforge:make-epub')

    const [themes, upload, poll1, poll2, get] = fake.netRequests
    expect(themes?.url).toBe('http://localhost:8000/api/v1/themes')
    expect(upload).toMatchObject({ url: 'http://localhost:8000/api/v1/generate/files', method: 'POST' })
    expect(poll1?.url).toBe('http://localhost:8000/api/v1/status/j1')
    expect(poll2?.url).toBe(poll1?.url)
    expect(get).toMatchObject({ url: 'http://localhost:8000/api/v1/download/j1', as: 'bytes' })

    const parts = (upload?.body as NetForm).form
    const value = (name: string) => parts.find((p) => p.name === name && 'value' in p)
    expect(value('title')).toEqual({ name: 'title', value: 'Storm Book' })
    expect(value('author')).toEqual({ name: 'author', value: 'Mara Lin' })
    expect(value('keep_order')).toEqual({ name: 'keep_order', value: 'true' })
    const files = parts.filter((p): p is { name: string; file: NetFile } => 'file' in p).map((p) => p.file)
    expect(files.map((f) => f.name)).toEqual(['01_two.md', '02_one.md'])
    const decode = (f: NetFile | undefined) => new TextDecoder().decode(f?.data)
    // two links back to one, and to a note that isn't in the book (its text only)
    expect(decode(files[0])).toBe('# The Harbor\n\nBack to [one](02_one.md). A note.\n')
    // one's frontmatter is gone and its link points at two's upload name
    expect(decode(files[1])).toBe('# The Storm\n\nOn to [two](01_two.md#harbor).\n')

    expect(fake.exported).toHaveLength(1)
    expect(fake.exported[0]).toMatchObject({ suggestedName: 'Storm Book.epub', data: EPUB })
    expect(fake.notices.at(-1)?.message).toMatch(/^Saved /)
    expect(form(fake).note).toMatch(/^Saved /)
    // the server's themes replace the built-in ones
    expect(field(fake, 'theme')?.options?.map((o) => o.value)).toEqual(['modern', 'sepia'])
  })

  it('sends the saved token as a bearer header', async () => {
    const fake = await started(host(fullJob()))
    await fake.api.secrets.set('api-token', 'tok-123')
    await fake.run('bookforge:make-epub')
    expect(fake.netRequests.every((r) => r.headers?.['Authorization'] === 'Bearer tok-123')).toBe(true)
  })

  it("shows the server's error when the job fails", async () => {
    const fake = await started(
      host([ok(THEMES), ok('{"job_id":"j1"}'), ok('{"status":"failed","error_message":"No valid chapters found"}')])
    )
    await fake.run('bookforge:make-epub')
    expect(fake.notices.at(-1)).toEqual({
      message: "BookForge couldn't make the EPUB: No valid chapters found.",
      action: { label: 'Show', surface: SURFACE }
    })
    expect(fake.exported).toEqual([])
    expect(form(fake).submitLabel).toBe('Make EPUB')
  })

  it('says plainly when the server is down', async () => {
    const fake = await started(host([]))
    await fake.run('bookforge:make-epub')
    expect(fake.notices.at(-1)?.message).toBe(
      "The BookForge server at localhost:8000 isn't answering. Check that it is running."
    )
  })

  it('explains a refused token before uploading anything', async () => {
    const fake = await started(host([{ status: 401, ok: false, text: '{"detail":"This BookForge server needs an API token."}' }]))
    await fake.run('bookforge:make-epub')
    expect(fake.netRequests).toHaveLength(1)
    expect(fake.notices.at(-1)?.message).toMatch(/needs an API token/)
  })

  it("passes on the server's reason for a refused upload", async () => {
    const fake = await started(host([ok(THEMES), { status: 400, ok: false, text: '{"detail":"Only markdown files are supported: x.txt"}' }]))
    await fake.run('bookforge:make-epub')
    expect(fake.notices.at(-1)?.message).toBe('BookForge: Only markdown files are supported: x.txt')
  })

  it('uses the server address from settings, without a trailing slash', async () => {
    const fake = await started(host(fullJob()))
    fake.setSetting('bookforge:server', 'https://books.example.com/')
    await fake.run('bookforge:make-epub')
    expect(fake.netRequests[0]?.url).toBe('https://books.example.com/api/v1/themes')
  })

  it('gives up after the poll limit', async () => {
    plugin.timing.maxPolls = 2
    const fake = await started(host([ok(THEMES), ok('{"job_id":"j1"}'), ok('{"status":"processing"}')]))
    await fake.run('bookforge:make-epub')
    expect(fake.notices.at(-1)?.message).toMatch(/taking too long/)
  })

  it('refuses a download address on another server', async () => {
    const fake = await started(
      host([ok(THEMES), ok('{"job_id":"j1"}'), ok('{"status":"completed","download_url":"https://evil.example/x"}')])
    )
    await fake.run('bookforge:make-epub')
    expect(fake.netRequests).toHaveLength(3)
    expect(fake.notices.at(-1)?.message).toMatch(/same server/)
  })

  it('leaves nothing registered after unload', async () => {
    const fake = await started(host())
    await fake.unload()
    expect(fake.liveDisposables()).toBe(0)
  })
})
