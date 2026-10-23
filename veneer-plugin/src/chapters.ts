// Pure helpers for the chapter list and the upload: no API calls, so they test without a host.
import { splitFrontmatter } from '@veneer/api'

/** One project document in the book's order, and whether it goes into the EPUB. */
export interface ChapterChoice {
  path: string
  include: boolean
}

/** The book's details, as the form edits them and the server takes them. */
export interface BookDetails {
  title: string
  author: string
  language: string
  description: string
  publisher: string
  theme: string
}

export const EMPTY_DETAILS: BookDetails = {
  title: '',
  author: '',
  language: 'en',
  description: '',
  publisher: '',
  theme: 'modern'
}

/**
 * The stored order brought up to date with the project's documents: stored paths that still
 * exist keep their place and choice, new documents follow in path order, included.
 */
export function reconcile(stored: readonly ChapterChoice[], paths: readonly string[]): ChapterChoice[] {
  const present = new Set(paths)
  const kept = stored.filter((c) => present.has(c.path))
  const known = new Set(kept.map((c) => c.path))
  const added = [...paths]
    .filter((p) => !known.has(p))
    .sort()
    .map((path) => ({ path, include: true }))
  return [...kept, ...added]
}

/** Moves `movedId` before `beforeId` (null: to the end), as a reorderable list reports it. */
export function move(chapters: readonly ChapterChoice[], movedId: string, beforeId: string | null): ChapterChoice[] {
  const moved = chapters.find((c) => c.path === movedId)
  if (moved === undefined || movedId === beforeId) return [...chapters]
  const rest = chapters.filter((c) => c.path !== movedId)
  const at = beforeId === null ? rest.length : rest.findIndex((c) => c.path === beforeId)
  rest.splice(at < 0 ? rest.length : at, 0, moved)
  return rest
}

/** Follows a rename or move of a file or folder through the stored order. */
export function renamed(chapters: readonly ChapterChoice[], from: string, to: string, kind: 'file' | 'folder'): ChapterChoice[] {
  return chapters.map((c) => {
    if (kind === 'file') return c.path === from ? { ...c, path: to } : c
    return c.path.startsWith(`${from}/`) ? { ...c, path: `${to}${c.path.slice(from.length)}` } : c
  })
}

/** `chapters/One.md` -> `One`. */
export function stemOf(path: string): string {
  const name = path.slice(path.lastIndexOf('/') + 1)
  return name.replace(/\.(md|markdown)$/i, '')
}

/** `chapters/One.md` -> `chapters`; `One.md` -> ''. */
export function folderOf(path: string): string {
  const slash = path.lastIndexOf('/')
  return slash < 0 ? '' : path.slice(0, slash)
}

/**
 * The file names to upload, in book order: `01_One.md`, `02_Two.md`. The server keeps upload
 * order (`keep_order`), so the number only keeps the names unique and readable.
 */
export function uploadNames(paths: readonly string[]): Map<string, string> {
  const width = Math.max(2, String(paths.length).length)
  const names = new Map<string, string>()
  paths.forEach((path, i) => {
    const safe = stemOf(path).replace(/[^A-Za-z0-9-]+/g, '_').replace(/^_+|_+$/g, '') || 'chapter'
    names.set(path, `${String(i + 1).padStart(width, '0')}_${safe}.md`)
  })
  return names
}

/** Resolves `target` (a link in the document at `from`) to an API path, or null if it leaves the project. */
export function resolveLink(from: string, target: string): string | null {
  const parts = folderOf(from) === '' ? [] : folderOf(from).split('/')
  for (const part of target.split('/')) {
    if (part === '' || part === '.') continue
    if (part === '..') {
      if (parts.length === 0) return null
      parts.pop()
    } else parts.push(part)
  }
  return parts.join('/')
}

const MARKDOWN_TARGET = /\.(md|markdown)$/i
const INLINE_LINK = /(!?)\[([^\]]*)\]\(\s*(<[^>]*>|[^)\s]+)(\s+"[^"]*")?\s*\)/g
const REFERENCE_DEFINITION = /^( {0,3}\[[^\]]+\]:\s*)(<[^>]*>|\S+)(.*)$/gm

/** What a link target becomes, or null to leave it alone. `''` means "drop the link, keep its text". */
function retarget(from: string, raw: string, names: ReadonlyMap<string, string>): string | null {
  const bare = raw.startsWith('<') ? raw.slice(1, -1) : raw
  if (/^[a-z][a-z0-9+.-]*:/i.test(bare) || bare.startsWith('#') || bare.startsWith('/')) return null
  const [pathPart, fragment] = bare.split('#', 2) as [string, string | undefined]
  let decoded: string
  try {
    decoded = decodeURIComponent(pathPart)
  } catch {
    return null
  }
  if (!MARKDOWN_TARGET.test(decoded)) return null
  const resolved = resolveLink(from, decoded)
  const name = resolved === null ? undefined : names.get(resolved)
  if (name === undefined) return ''
  return fragment === undefined ? name : `${name}#${fragment}`
}

/**
 * Points relative links to other chapters at their upload names, so the server can turn them
 * into links inside the EPUB. A link to a document that isn't in the book keeps only its text,
 * since the EPUB has nothing to open. Images and remote links are left alone.
 */
export function rewriteLinks(from: string, body: string, names: ReadonlyMap<string, string>): string {
  const inline = body.replace(INLINE_LINK, (whole, bang: string, text: string, target: string, title?: string) => {
    if (bang === '!') return whole
    const next = retarget(from, target, names)
    if (next === null) return whole
    if (next === '') return text
    return `[${text}](${next}${title ?? ''})`
  })
  return inline.replace(REFERENCE_DEFINITION, (whole, head: string, target: string, tail: string) => {
    const next = retarget(from, target, names)
    return next === null || next === '' ? whole : `${head}${next}${tail}`
  })
}

/** A chapter as uploaded: frontmatter removed (the server would print it), links retargeted. */
export function chapterBody(path: string, text: string, names: ReadonlyMap<string, string>): string {
  return rewriteLinks(path, splitFrontmatter(text).body, names)
}

/**
 * The scalar `key: value` lines of a frontmatter block, enough to prefill the details. Lists,
 * nested maps, and multi-line values are skipped.
 */
export function frontmatterScalars(yaml: string): Record<string, string> {
  const out: Record<string, string> = {}
  for (const line of yaml.split('\n')) {
    const match = /^([A-Za-z_][\w-]*):[ \t]+(.+?)\s*$/.exec(line)
    if (match === null) continue
    let value = match[2] as string
    if (/^["'].*["']$/.test(value)) value = value.slice(1, -1)
    if (value === '' || value === '|' || value === '>') continue
    out[(match[1] as string).toLowerCase()] = value
  }
  return out
}

/**
 * Details filled from the first chapter's frontmatter. A chapter's `title` names the chapter, so
 * the book's title comes from a `book` key, else the project folder's name.
 */
export function prefillDetails(frontmatterYaml: string, projectName: string | null): BookDetails {
  const fm = frontmatterScalars(frontmatterYaml)
  return {
    ...EMPTY_DETAILS,
    title: fm['book'] ?? projectName ?? '',
    author: fm['author'] ?? '',
    language: fm['language'] ?? fm['lang'] ?? EMPTY_DETAILS.language,
    description: fm['description'] ?? '',
    publisher: fm['publisher'] ?? ''
  }
}
