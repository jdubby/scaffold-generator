### python-cli (backend)

The command-line layer owns argument parsing and user-facing output — nothing
else. Parse and validate arguments at the edge (argparse or click), then hand
typed values to plain functions that hold the logic, so behavior is testable
without spawning a process. Declare a single console-script entry point in
`pyproject.toml`; once the tool grows past one verb, give each subcommand its
own module behind that entry point.
