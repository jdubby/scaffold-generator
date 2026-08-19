Feature: Gate baseline
  As a developer who just generated a scaffold
  I want to run its declared quality gates once, before writing any code
  So that a gate which asserts nothing is caught on day one

  # AC-1
  Scenario: A generated scaffold's own gates are read back and reported
    Given a scaffold generated from the bundled library
    When the user runs the baseline with --dry-run
    Then the generator exits successfully
    And the baseline lists the gate command "pytest"
    And the baseline reports that nothing ran

  # AC-1, AC-2
  Scenario: Each gate is executed and classified
    Given a scaffold declaring a gate "ok" running "python3 --version"
    And a scaffold gate "broken" running "python3 -c \"raise SystemExit(3)\""
    And a scaffold gate "missing" running "scaffold-generator-no-such-tool"
    When the user runs the baseline
    Then the generator exits successfully
    And the gate "ok" is reported as "passed"
    And the gate "broken" is reported as "failed"
    And the gate "missing" is reported as "unavailable"
    And the baseline explains that a passing gate deserves scrutiny

  # AC-3
  Scenario: A gate containing shell syntax is skipped, not executed
    Given a scaffold declaring a gate "chained" running "python3 --version && python3 --version"
    When the user runs the baseline
    Then the generator exits successfully
    And the gate "chained" is reported as "skipped"
    And the skip reason mentions shell syntax

  # AC-4
  Scenario: A dry run executes nothing at all
    Given a scaffold declaring a gate "writer" that would create a file when run
    When the user runs the baseline with --dry-run
    Then the generator exits successfully
    And the baseline reports that nothing ran
    And the gate left no trace in the scaffold

  # AC-4
  Scenario: The same gate does run without --dry-run
    Given a scaffold declaring a gate "writer" that would create a file when run
    When the user runs the baseline
    Then the generator exits successfully
    And the gate left its trace in the scaffold

  # AC-5
  Scenario: A directory that is not a scaffold fails clearly
    Given a directory that is not a generated scaffold
    When the user runs the baseline
    Then the generator exits with a non-zero code
    And an error mentions "AGENTS.md"
