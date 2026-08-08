# JetBrains profiles

Profiles are optional source templates. JetBrains does not load configuration
from this directory directly.

Each profile mirrors the path it should occupy beneath `.idea/` after
installation. This keeps profile composition explicit and prevents optional
language tooling from becoming a universal repository requirement.

## Profile lifecycle

1. Copy a selected profile into `.idea/`.
2. Open the repository in the appropriate JetBrains IDE.
3. Confirm the relevant plugin and SDK are available.
4. Validate the shared configuration.
5. Commit only portable files.
6. Leave generated and user-local state ignored.
