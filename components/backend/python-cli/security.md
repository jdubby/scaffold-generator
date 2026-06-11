### python-cli security

- Never interpolate user input into a shell: use `subprocess` with argument
  lists, and no `shell=True` with constructed strings.
- Secrets arrive via environment variables or interactive prompts — never as
  command-line arguments, which leak through process lists and shell history.
- Validate file paths taken from arguments before reading or writing; refuse to
  write outside the user-specified destination.
- Pin dependencies to a tested baseline and treat vulnerability alerts as
  high-priority debt.
