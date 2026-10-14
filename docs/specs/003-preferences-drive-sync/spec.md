# Feature Specification: SQLite Preferences and Google Drive Backup

**Feature Branch**: `003-preferences-drive-sync`

**Created**: 2026-08-21

**Status**: Draft

**Origin**: Renumbered from `002-preferences-drive-sync`.

**Input**: Store personal preferences locally with SQLite and persist backups through Google Drive.

## User Scenarios & Testing

### User Story 1 - Persist preferences locally (Priority: P1)

As the user, I want timezone, language, default duration and confirmation preferences to survive restarts.

**Independent Test**: Write preferences to a temporary SQLite database, reopen it and read the same values.

### User Story 2 - Back up and restore through Drive (Priority: P2)

As the user, I want to back up and restore preferences through Google Drive.

**Independent Test**: Mock Drive upload/download and verify a versioned snapshot is created and restored.

## Requirements

- Preferences MUST use a versioned local SQLite schema.
- Preferences MUST be isolated by user identity.
- The store MUST support timezone, language, default duration and confirmation settings.
- Backups MUST use a versioned representation.
- Restore MUST reject malformed or unsupported snapshots.
- A newer local version MUST NOT be overwritten silently.
- Local operation MUST continue when Drive is unavailable.
- Drive integration MUST use the MCP/domain boundary selected by `002-calendar-mcp-foundation`, without coupling preference storage to Calendar workflow state.

## Edge Cases

- Drive unavailable.
- Malformed or unsupported snapshot.
- Local/remote version conflict.
- Multiple users accessing the same deployment.

## Success Criteria

- Preferences survive local restart tests.
- Restore preserves all supported keys.
- Conflict tests never silently discard a newer version.
- Drive tests run without network access or real OAuth tokens.

## Dependencies

- `000-mcp-compose`
- `001-langgraph-mcp-routing`
- `002-calendar-mcp-foundation` for identity and integration boundaries
