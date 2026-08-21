# Feature Specification: SQLite Preferences and Google Drive Backup

**Feature Branch**: `002-preferences-drive-sync`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: Store personal preferences locally with SQLite and persist backups through Google Drive.

## User Scenarios & Testing

### User Story 1 - Persist preferences locally (Priority: P1)

As the user, I want timezone, language, default duration and confirmation preferences to survive restarts.

**Why this priority**: Local persistence provides immediate value without external infrastructure.

**Independent Test**: Write preferences to a temporary SQLite database, reopen it and read the same values.

**Acceptance Scenarios**:

1. **Given** a new local database, **When** a preference is saved, **Then** it is available after reopening the database.
2. **Given** an unknown preference key, **When** it is requested, **Then** the store returns the documented default.

### User Story 2 - Back up and restore through Drive (Priority: P2)

As the user, I want to back up and restore my preferences through my Google Drive.

**Why this priority**: Drive provides personal persistence while avoiding a managed database initially.

**Independent Test**: Mock Drive upload/download and verify a versioned snapshot is created and restored.

**Acceptance Scenarios**:

1. **Given** local preferences, **When** backup runs, **Then** a versioned snapshot is uploaded without exposing credentials.
2. **Given** an authorized snapshot, **When** restore runs, **Then** preferences are restored without corrupting the local database.

### Edge Cases

- Drive unavailable: local reads and writes must continue.
- Snapshot is malformed or from an unsupported schema version.
- Local and remote snapshots have conflicting versions.
- Multiple users must never read each other's preferences.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST persist preferences in a versioned local SQLite schema.
- **FR-002**: The system MUST isolate preferences by user identity.
- **FR-003**: The system MUST support timezone, language, default duration and confirmation preferences.
- **FR-004**: The system MUST export a versioned backup representation.
- **FR-005**: The system MUST support mocked Drive upload and restore operations.
- **FR-006**: The system MUST not overwrite a newer local version silently.
- **FR-007**: The system MUST continue operating locally when Drive is unavailable.

### Key Entities

- **Preference**: User-scoped key, value, type and update timestamp.
- **PreferenceSnapshot**: Versioned export, owner, device identifier and timestamp.
- **SyncStatus**: Last attempted operation, version and error state.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Preferences survive 100% of local restart tests.
- **SC-002**: Restore tests preserve all supported preference keys.
- **SC-003**: No conflict test silently discards a newer version.
- **SC-004**: All Drive tests run without network access or real OAuth tokens.

## Assumptions

- Initial release uses backup and manual restore before bidirectional sync.
- `sqlite-utils` is preferred, but the schema remains compatible with standard SQLite tooling.
- Drive OAuth scopes will be added only when this feature is implemented.