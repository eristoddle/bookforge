import { describe, expect, it } from 'vitest'
import {
  chapterBody,
  frontmatterScalars,
  move,
  prefillDetails,
  reconcile,
  renamed,
  resolveLink,
  rewriteLinks,
  uploadNames
} from './chapters.js'

describe('reconcile', () => {
  it('keeps the stored order and choices, drops gone files, and appends new ones included', () => {
    const stored = [
      { path: 'b.md', include: true },
      { path: 'gone.md', include: true },
      { path: 'a.md', include: false }
    ]
    expect(reconcile(stored, ['a.md', 'b.md', 'd.md', 'c.md'])).toEqual([
      { path: 'b.md', include: true },
      { path: 'a.md', include: false },
      { path: 'c.md', include: true },
      { path: 'd.md', include: true }
    ])
  })
})

describe('move', () => {
  const list = ['a', 'b', 'c'].map((path) => ({ path, include: true }))
  it('moves a row before another, or to the end', () => {
    expect(move(list, 'c', 'a').map((c) => c.path)).toEqual(['c', 'a', 'b'])
    expect(move(list, 'a', null).map((c) => c.path)).toEqual(['b', 'c', 'a'])
  })
  it('ignores an unknown row', () => {
    expect(move(list, 'x', 'a').map((c) => c.path)).toEqual(['a', 'b', 'c'])
  })
})

describe('renamed', () => {
  it('follows a file rename and a folder move', () => {
    const list = [
      { path: 'one.md', include: true },
      { path: 'part/two.md', include: false },
      { path: 'partial.md', include: true }
    ]
    expect(renamed(list, 'one.md', 'One.md', 'file')[0]).toEqual({ path: 'One.md', include: true })
    expect(renamed(list, 'part', 'book/part', 'folder').map((c) => c.path)).toEqual([
      'one.md',
      'book/part/two.md',
      'partial.md'
    ])
  })
})

describe('uploadNames', () => {
  it('numbers the chapters in book order with safe names', () => {
    const names = uploadNames(['ch/The Storm.md', 'Épilogue!.markdown'])
    expect([...names.values()]).toEqual(['01_The_Storm.md', '02_pilogue.md'])
  })
  it('widens the number past 99 chapters', () => {
    const names = uploadNames(Array.from({ length: 120 }, (_, i) => `c${i}.md`))
    expect(names.get('c0.md')).toBe('001_c0.md')
  })
})

describe('links', () => {
  const names = new Map([
    ['chapters/one.md', '01_one.md'],
    ['chapters/two.md', '02_two.md']
  ])

  it('resolves relative paths and refuses ones that leave the project', () => {
    expect(resolveLink('chapters/one.md', '../chapters/./two.md')).toBe('chapters/two.md')
    expect(resolveLink('one.md', '../x.md')).toBeNull()
  })

  it('points chapter links at upload names and keeps the fragment and title', () => {
    expect(rewriteLinks('chapters/one.md', 'See [two](two.md#storm "Two").', names)).toBe(
      'See [two](02_two.md#storm "Two").'
    )
    expect(rewriteLinks('chapters/one.md', 'See [two](<two.md>).', names)).toBe('See [two](02_two.md).')
  })

  it('keeps only the text of a link to a document outside the book', () => {
    expect(rewriteLinks('chapters/one.md', 'A [note](../notes/idea.md) here.', names)).toBe('A note here.')
  })

  it('leaves images, remote links, anchors, and non-markdown targets alone', () => {
    const text = '![map](two.md) [web](https://x.com/a.md) [top](#top) [pdf](two.pdf)'
    expect(rewriteLinks('chapters/one.md', text, names)).toBe(text)
  })

  it('rewrites reference definitions', () => {
    expect(rewriteLinks('chapters/one.md', '[t]: two.md#a "T"\n', names)).toBe('[t]: 02_two.md#a "T"\n')
  })

  it('strips frontmatter from the uploaded body', () => {
    expect(chapterBody('chapters/one.md', '---\ntitle: One\n---\n# One\n[t](two.md)\n', names)).toBe(
      '# One\n[t](02_two.md)\n'
    )
  })
})

describe('details from frontmatter', () => {
  it('reads plain scalars, unquoting them, and skips the rest', () => {
    expect(frontmatterScalars('title: "One"\nauthor: Mara Lin\ntags:\n  - a\nsummary: |\n')).toEqual({
      title: 'One',
      author: 'Mara Lin'
    })
  })

  it('takes the book title from `book`, else the project, never the chapter title', () => {
    expect(prefillDetails('title: Chapter One\nauthor: Mara\nlang: fr\n', 'Storm Book')).toMatchObject({
      title: 'Storm Book',
      author: 'Mara',
      language: 'fr'
    })
    expect(prefillDetails('book: The Storm\n', 'folder').title).toBe('The Storm')
  })
})
