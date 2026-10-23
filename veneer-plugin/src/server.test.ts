import { describe, expect, it } from 'vitest'
import { veneerError } from '@veneer/api'
import { answerProblem, networkProblem, sentence } from './server.js'

describe('networkProblem', () => {
  const base = 'http://localhost:8000'
  it('tells the writer where to allow a local address', () => {
    expect(networkProblem(veneerError('net/blocked', 'x'), base)).toBe(
      'localhost:8000 is a local address. Allow localhost:8000 for BookForge in Settings, Plugins, then try again.'
    )
  })
  it('says a declined connection sent nothing', () => {
    expect(networkProblem(veneerError('plugin/declined', 'x'), base)).toMatch(/nothing was sent/)
  })
  it('names a bad address', () => {
    expect(networkProblem(veneerError('net/invalid', 'x'), 'nope')).toMatch(/isn't a web address/)
  })
})

describe('answerProblem', () => {
  it("reads FastAPI's validation list", () => {
    const text = '{"detail":[{"msg":"Field required"},{"msg":"Bad theme"}]}'
    expect(answerProblem({ status: 422, ok: false, headers: {}, text, truncated: false })).toBe(
      'BookForge: Field required; Bad theme'
    )
  })
  it('falls back to the status', () => {
    expect(answerProblem({ status: 502, ok: false, headers: {}, text: '<html>', truncated: false })).toBe(
      'The BookForge server answered 502.'
    )
  })
})

it('keeps a notice to one line of at most 200 characters', () => {
  const long = sentence(`a\n${'b'.repeat(300)}`)
  expect(long).not.toContain('\n')
  expect(long.length).toBe(200)
})
