# Drift schema migrations

## v2

- Added explicit `onUpgrade` migration path in `AppDatabase`.
- Consolidated schema bootstrap into `_ensureSchema()` so create/upgrade paths stay aligned.
- Migration step guarantees required indexes exist:
  - `idx_reflections_created_at`
  - `idx_check_ins_created_at`
  - `idx_memories_type`
  - `idx_memories_source`

## v1

- Initial Drift-backed persistence schema for:
  - `reflections`
  - `check_ins`
  - `memories`
