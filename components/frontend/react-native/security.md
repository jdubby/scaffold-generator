### react-native security

- Store tokens and credentials in the platform keychain/keystore — never in
  AsyncStorage or any plain-text store.
- Ship no secrets in the JS bundle; assume anything bundled is readable in a
  distributed build.
- Validate and allowlist deep-link and universal-link URLs before acting on
  them; never navigate to attacker-controlled destinations.
- Pin or verify TLS for requests carrying credentials where the threat model
  warrants it.
