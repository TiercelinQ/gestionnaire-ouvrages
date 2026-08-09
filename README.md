# Gestionnaire Ouvrage - v1.0.0

Windows desktop client for cataloguing and browsing a personal book collection. Desktop front end for the Gestionnaire Ouvrage API (Cloudflare Worker + D1), replacing a Python/PyQt6/SQLite application whose database lived on a synchronised folder.

## Objective

Catalogue, organise and browse a personal book collection with a three-level classification (category → genre → sub-genre) and detailed edition metadata: ISBN, year, collection, binding, dimensions, covers, physical location in the home.

## Features

- Account sign-in; the session token is encrypted at rest with Electron `safeStorage` and never leaves the main process.
- Book list with client-side search, column sorting and virtualised scrolling over the whole collection.
- Full record: create, edit with optimistic locking, move to trash.
- Trash with remaining days and restore. Permanent deletion is a daily server task.
- Per-field history panel for any book.
- Hierarchical classification and four reference lists (illustrations, periods, bindings, locations).
- Dashboard: counters plus category and period charts.
- Cover images resolved from a configurable root folder, with thumbnail and full-screen preview.
- CSV export of the displayed collection.
- Light and dark themes, splash screen, passive API availability indicator.

## Stack

| Layer        | Technology                                                      |
| ------------ | --------------------------------------------------------------- |
| Runtime      | Node.js 24+ · Electron 43                                       |
| Language     | TypeScript strict                                               |
| Renderer     | React 19, function components and hooks only                    |
| Build        | electron-vite                                                   |
| Architecture | Strict MVC - main = models, renderer = views, IPC = controllers |
| Styling      | Centralised CSS: `tokens.css` (variables) + `styles.css`        |
| Icons        | Lucide (`lucide-react`)                                         |
| Charts       | Recharts                                                        |
| Logging      | electron-log                                                    |
| Tests        | Vitest + Testing Library                                        |
| Packaging    | electron-builder (NSIS + portable)                              |

No local database: all data is served by the API. No third-party HTTP client - Node's built-in `fetch`. No virtualisation library - the list is flat with a fixed row height.

## Prerequisites

- Windows 10 or 11.
- Node.js 24 LTS or later.
- An account on the Gestionnaire Ouvrage API. Accounts are created and reset by the administrator from the command line; the application has no sign-up or password-change screen.
- Network access to `https://gestionnaire-ouvrages-api.qtiercelin-apps.workers.dev`.

## Installation

```
npm install
npm run dev          # development
npm run typecheck    # TypeScript verification (main + renderer)
npm run lint         # ESLint
npm test             # Vitest
npm run build        # build without packaging
npm run dist         # Windows packaging (NSIS + portable)
```

If `npm run dev` reports `Error: Electron uninstall`, the Electron binary extraction failed silently - run `npm run postinstall`, which restores it from the local cache.

## Project tree

```
src/
├── shared/                     types, constants, IPC channel names
│   ├── config.ts               API URL, window sizes, toast position, log settings
│   ├── types.ts                API DTOs, IpcResult, WindowApi, type guards
│   └── ipc-channels.ts         the 23 channel names
├── main/
│   ├── index.ts                windows, splash, security, global error handlers
│   ├── logger.ts               electron-log setup
│   ├── models/
│   │   ├── api-client.ts       the only network access point
│   │   ├── token-store.ts      session token, encrypted with safeStorage
│   │   ├── session.model.ts    sign-in, sign-out, session check, version thresholds
│   │   ├── ouvrage.model.ts    books, trash, history
│   │   ├── nomenclature.model.ts   the seven reference lists
│   │   ├── couverture.model.ts     cover path resolution and image reading
│   │   ├── export.model.ts     CSV generation
│   │   ├── preferences.model.ts    preferences.json
│   │   └── errors.ts           named business errors
│   └── controllers/            one IPC handler per channel, input validation
├── preload/index.ts            contextBridge, one named function per channel
└── renderer/
    ├── index.html · splash.html    both carrying the strict CSP
    └── src/
        ├── App.tsx             error boundary, providers, shell, routing
        ├── views/              screens, layout components, modals, drawer
        ├── hooks/              session, toasts, nomenclatures, books, virtualisation
        ├── utils/              search normalisation, formatting
        ├── i18n/               centralised French labels
        └── styles/             tokens.css, styles.css, splash.css
```

## IPC channels

Naming convention `entity:action`. Declared in `src/shared/ipc-channels.ts`; no channel string appears anywhere else.

| Channel               | Controller   | `window.api`                              |
| --------------------- | ------------ | ----------------------------------------- |
| `session:status`      | session      | `sessionStatus()`                         |
| `session:login`       | session      | `sessionLogin(credentials)`               |
| `session:logout`      | session      | `sessionLogout()`                         |
| `app:info`            | session      | `appInfo()`                               |
| `ouvrage:list`        | ouvrage      | `ouvrageList()`                           |
| `ouvrage:get`         | ouvrage      | `ouvrageGet(id)`                          |
| `ouvrage:create`      | ouvrage      | `ouvrageCreate(input)`                    |
| `ouvrage:update`      | ouvrage      | `ouvrageUpdate(id, input)`                |
| `ouvrage:delete`      | ouvrage      | `ouvrageDelete(id, version)`              |
| `ouvrage:restore`     | ouvrage      | `ouvrageRestore(id)`                      |
| `ouvrage:history`     | ouvrage      | `ouvrageHistory(id)`                      |
| `corbeille:list`      | ouvrage      | `corbeilleList()`                         |
| `nomenclature:list`   | nomenclature | `nomenclatureList()`                      |
| `nomenclature:create` | nomenclature | `nomenclatureCreate(resource, input)`     |
| `nomenclature:update` | nomenclature | `nomenclatureUpdate(resource, id, input)` |
| `nomenclature:delete` | nomenclature | `nomenclatureDelete(resource, id)`        |
| `couverture:pick`     | couverture   | `couverturePick()`                        |
| `couverture:read`     | couverture   | `couvertureRead(path)`                    |
| `export:csv`          | export       | `exportCsv(rows)`                         |
| `pref:get`            | preferences  | `getPreferences()`                        |
| `pref:set`            | preferences  | `setPreference(key, value)`               |
| `pref:pickFolder`     | preferences  | `pickCoversFolder()`                      |
| `api:status` (push)   | -            | `onApiStatus(callback)`                   |

## Data model

The application owns no schema: the API does. Locally it stores only two files under `app.getPath("userData")`:

- `preferences.json` - theme, window bounds, covers root folder.
- `session.bin` - the session token and its expiry, encrypted with `safeStorage` (DPAPI on Windows).

## Conventions

- Strict MVC: business logic in `src/main/models/`, validation and dispatch in controllers, rendering only in views. Imports flow one way: renderer → preload → controllers → models.
- No hardcoded visual value in TS/TSX and no inline `style` attribute. Two sanctioned exceptions, both commented: the sliding tab underline writes two CSS variables, and the virtual table's spacer rows carry a computed height.
- `styles.css` consumes only `var(--token)`. Dark mode lives in the single `[data-theme="dark"]` block of `tokens.css`.
- Depth comes from strokes: no `box-shadow`, no gradient, no row striping.
- Errors surface as toasts or under the field named by the server; never `alert()`, `confirm()` or `dialog.showMessageBox`.
- Locked Electron security: `contextIsolation`, `sandbox`, no `nodeIntegration`, strict CSP, navigation and window opening blocked, every IPC payload validated on the main side.
- No `console.log` in shipped code - `electron-log` only, writing to `userData/logs/main.log`. Set `GESTIONNAIREOUVRAGE_DEBUG=1` for debug-level logging.

## Known limitation

`GET /v1/ouvrages` currently returns six fields per book. Location filtering, cover-completion counters, latest additions and the period chart need four more; those screens hide themselves until the API provides them. The requested change is specified in `docs/api/evolution-liste-ouvrages.md`. CSV export covers the columns the list provides - exporting every field would cost one request per book.

## Claude Code

`.claude/settings.json` ships with the project: deny rules on secrets and build outputs, plus a `Stop` hook running ESLint when a TypeScript file has uncommitted changes. Adjust or remove it to taste.

## Licence

Proprietary. Use, modification and redistribution require the author's explicit agreement.
