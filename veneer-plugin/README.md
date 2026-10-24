# BookForge for Veneer

A [Veneer](https://github.com/eristoddle/veneer) plugin that turns a project's markdown documents into an EPUB with a BookForge server (this repository). Built on `@veneer/api` 0.40.0 and nothing else.

## What the writer does

1. Open a project folder in Veneer, then run **Show BookForge** from the palette. A modal opens with the project's documents on the left and the book's details on the right.
2. **Chapters.** Every document is listed and included at first. Enter or a click includes a chapter or leaves it out. Drag a row, or press Alt+Up and Alt+Down, to change the order. The order and the choices are kept in the project at `.veneer/data/bookforge/chapters.json`, so they sync and go into history with the manuscript.
3. **Details.** Title, author, language, description, publisher, and theme. The first time, they are filled from the first chapter's frontmatter (`author`, `language` or `lang`, `description`, `publisher`; the title comes from a `book` key, else the project folder's name). Edits are kept at `.veneer/data/bookforge/details.json`.
4. **Make EPUB** (the form's button, Cmd+Enter, or the palette command **Make an EPUB**). The plugin saves the open document, checks the server, uploads the included chapters in order, and shows progress above the form. When the server finishes, a save dialog asks where the EPUB goes. A notice says when it's saved, or what went wrong.

**API token.** Only needed if the server sets `API_TOKEN`. Type it in the form's API token field; on Make EPUB it goes into the system keychain through `api.secrets` and the field clears. It is never stored in settings or the project. **Forget the BookForge API Token** removes it.

**Server address.** Settings, BookForge, Server address (default `http://localhost:8000`). Veneer refuses addresses on this computer or the local network until the writer allows one for this plugin: Settings, Plugins, BookForge, Local addresses, add `localhost:8000`. The first request to an address also asks once in a notice.

## What the plugin sends

For each included chapter, in book order: the saved text with its frontmatter removed, uploaded as `01_<name>.md`, `02_<name>.md`, and so on, with `keep_order=true`. Relative links to other chapters in the book are pointed at those upload names, and the server turns them into links inside the EPUB. A link to a document that is not in the book keeps only its text. Images are left as they are: the server does not take images yet.

## Develop

```
npm install          # .npmrc allows the git dependency on @veneer/api
npm test             # Vitest on the fake host from @veneer/api/testing
npm run typecheck
npm run build        # bundles main.js (esbuild, one ES module)
```

`@veneer/api` is pinned to the `v0.40.0` tag of https://github.com/eristoddle/veneer-api.

To try it in Veneer: a dev build has **Load plugin from folder** in the palette; point it at this folder after `npm run build`. A packaged Veneer can install from the folder or a zip in Settings, Plugins. Run a server with `python -m bookforge.main` from the repository root.

## Layout

- `manifest.json`: one command pair, one modal surface (`bookforge:book`), one setting (`bookforge:server`).
- `src/index.ts`: state, the split view, handlers, and the make flow.
- `src/chapters.ts`: pure helpers: order, upload names, link rewriting, frontmatter prefill.
- `src/server.ts`: the BookForge REST calls through `api.net.fetch`, and every failure as one plain sentence.

## Releasing

The plugin releases with the server, on one version line. `python release.py <version>` (see `RELEASE_QUICKSTART.md`) bumps `manifest.json` and `package.json` here with the Python package, then tags `v<version>`. On that tag, `.github/workflows/release.yml` does two things:

1. It checks that the manifest's version matches the tag, then typechecks, tests, and builds the plugin. A failure stops the release before anything goes to PyPI.
2. It publishes to PyPI and creates the GitHub release with `manifest.json` and `main.js` attached.

Writers install it in Veneer from Settings, Plugins, Install from GitHub, with `eristoddle/bookforge`. "Check for updates" sees each new tag.

Never change the manifest's `id`; Veneer refuses an update with a different one. When the plugin needs a newer `@veneer/api`, bump the dependency and `apiVersion` together.
