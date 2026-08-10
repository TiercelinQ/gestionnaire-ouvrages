# Changelog

All notable changes to this project are documented in this file.
The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

## [1.0.1] - 2026-08-10

### Fixed

- Top bar and status bar stayed in place while scrolling: the shell now fills the window instead of growing with its content, so only the main content area scrolls.
- Table scrollbar now starts below the header row, which no longer sits inside the scrolling container.
- Table columns keep a fixed width instead of resizing as virtualised rows enter and leave the DOM; overflowing cell text is truncated.

## [1.0.0] - 2026-08-09

### Added

- Initial release.
- Account sign-in against the Cloudflare Worker API, with the session token encrypted at rest through Electron `safeStorage`.
- Book list with client-side search, sorting and virtualised scrolling over the full collection.
- Book record: create, edit with optimistic locking, and move to trash.
- Trash with remaining days and restore.
- Per-field history panel for a book.
- Hierarchical classification (category, genre, sub-genre) and four reference lists.
- Dashboard with counters and category/period charts.
- Cover resolution from a configurable root folder, thumbnail and full-screen preview.
- CSV export of the displayed collection.
- Light and dark themes, splash screen, passive API availability indicator.
