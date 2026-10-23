# Direction: BookForge as a remote API for Veneer

*Planning note, 2026-10-16; status added 2026-10-23.*

- [Veneer](https://github.com/eristoddle/veneer), the desktop writing app, has a BookForge plugin: `veneer-plugin/` in this repository.
- BookForge runs as a **remote API**. The Veneer plugin is a thin client that calls it over the network (through Veneer's `api.net.fetch`).
- BookForge is still simple, with more features to add. The first plugin covers only what the server does today.

## Status (2026-10-23)

Built against `@veneer/api` 0.40.0, following Veneer's `docs/handoff/bookforge-plugin-brief.md`. See `veneer-plugin/README.md` for how it works.

| Brief item | State |
|---|---|
| 1. Choose and order chapters | Built and tested: a reorderable list in a modal; Enter includes a chapter or leaves it out; kept in `api.projectData`. |
| 2. Book details | Built and tested: a form, prefilled from frontmatter, kept in `api.projectData`; themes from `GET /api/v1/themes`. |
| 3. Make the EPUB | Built and tested: `saveNow`, frontmatter stripped, chapter links rewritten, multipart upload in order, token in `api.secrets` and an `Authorization` header. |
| 4. Progress | Built and tested: polls `/status`, shows the state above the form, and raises a notice on success or failure, with the server's own error. |
| 5. Save | Built and tested: downloads bytes, then `api.export.saveAs`. |
| Release from GitHub | **Not done**: see "Releasing" below. |

Verified: 39 Vitest tests on the fake host; 12 pytest tests for the server; and one run in the real Veneer app (a built Electron app driven by Playwright) against a real BookForge server with a token set. That run left a chapter out, reordered, saved the token, made the EPUB, and saved it. The EPUB's chapter order, links, metadata, and lack of frontmatter were checked, with no console errors.

## Server changes made for the plugin

- Frontmatter is stripped before conversion. It used to be printed as a heading.
- The Markdown converter is reset per chapter. Footnotes used to repeat in every later chapter.
- `keep_order` keeps chapters in upload order.
- Links to other uploaded chapters point at their XHTML files.
- `GET /api/v1/themes` lists the themes.
- An optional `API_TOKEN` is checked as a bearer token. `/health` stays open.
- Output file names are safe for any title.
- A chapter with no heading is named after its file, without the order number.

## Deferred server items (from the brief, not needed for the first plugin)

- Images and a cover: a second multipart field or a zip, with image paths rewritten. `_copy_cover_image` is still a stub, so the plugin leaves image links as they are.
- Reading the book's title and author from frontmatter on the server. The plugin prefills them instead.
- `bookforge.yaml` and custom themes: implement them or drop them from the docs.
- Tightening CORS, expiring old jobs and their files, and progress detail in `/status`.

## What the Veneer API lacked (for the API, not worked around)

1. **No secret form field.** The API token is typed into a plain `text` field, so it shows while typed. It goes to `api.secrets` on submit and the field clears. A `secret` (password) field type would fix it.
2. **No checked state on list rows.** "Include in the book" is shown with a numbered label versus a "left out" detail, toggled by opening the row. A row checkbox or toggle would be clearer.
3. **The fake host can't make `net.fetch` reject with `net/blocked` or `plugin/declined`.** `netReplies` only answers, or rejects `offline` when it is empty. The plugin's wording for those codes is tested as a pure function instead.
4. **The fake host keeps `projectData` across `switchProject`.** The real one is per project. This was harmless here, but a plugin test of a project switch could pass falsely.
5. **Installing from GitHub assumes the plugin is at the repository root.** A branch install reads `manifest.json` and `main.js` from the root only (`src/main/plugin-repo.ts`), so a plugin in a subfolder of a larger repository, like this one, can't be installed from a branch. Release assets are not affected.

## Releasing (a decision)

Veneer installs a plugin from a repository's **latest GitHub release**, which must carry `manifest.json` and `main.js`, and "Check for updates" compares tags. This repository's `v*` tags already create releases for the PyPI package, so plugin and server releases would replace each other as "latest". The options:

- **A. One release line.** `release.yml` also builds the plugin and attaches `manifest.json` and `main.js` to every BookForge release, so the plugin's version follows the server's.
- **B. Its own repository** for the plugin (or the community plugin repo). The server and the plugin then release separately.
- **C. No GitHub install for now.** Build with `npm run build` and install from the folder or a zip in Veneer's Settings, Plugins. (A branch install doesn't help here: it reads only the repository root; see gap 5.)

Open questions from 2026-10-16 that are now answered: manuscript files go up as a multipart upload of the saved text; credentials are an optional bearer token kept in `api.secrets`.
