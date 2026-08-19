Feature: Executable quality gates
  As a developer working in a generated scaffold
  I want each component's quality gate commands written down as runnable commands
  So that the delivery loop's gate step names what to run

  # AC-2
  Scenario: Declared gates are listed in the generated AGENTS.md
    Given a module "fastapi" declaring gates its CI runs
    And a stack spec declaring backend component "fastapi"
    When the user generates the scaffold
    Then the generator exits successfully
    And "AGENTS.md" lists the gate command "ruff check ."
    And "AGENTS.md" lists the gate command "pytest"
    And "AGENTS.md" groups the gate commands under "fastapi"
    And no warnings are printed

  # AC-2
  Scenario: A command declared by two modules is listed once
    Given a module "fastapi" declaring gates its CI runs
    And a module "python-cli" declaring gates its CI runs
    And a stack spec declaring backend component "fastapi"
    And the spec also declares backend component "python-cli"
    When the user generates the scaffold
    Then the generator exits successfully
    And "AGENTS.md" lists the gate command "pytest" exactly once

  # AC-3
  Scenario: A gate the module's own CI never runs is reported
    Given a module "drifty" declaring a gate its CI does not run
    And a stack spec declaring backend component "drifty"
    When the user generates the scaffold
    Then the generator exits successfully
    And a warning names "drifty" and "never runs it"

  # AC-6
  Scenario: A module with no checks.yml fails generation like any missing fragment
    Given a module "bare" declaring no gates
    And a stack spec declaring backend component "bare"
    When the user generates the scaffold
    Then the generator exits with a non-zero code
    And an error names "bare" and "missing fragment file: checks.yml"
    And no output directory is created

  # AC-6
  Scenario: A module declaring an empty gate list generates without warnings
    Given a module "bare-but-explicit" declaring an empty gate list
    And a stack spec declaring backend component "bare-but-explicit"
    When the user generates the scaffold
    Then the generator exits successfully
    And no warnings are printed

  # AC-1
  Scenario: A malformed checks.yml fails generation and names the field
    Given a module "broken" whose checks.yml declares a gate name that is not a slug
    And a stack spec declaring backend component "broken"
    When the user generates the scaffold
    Then the generator exits with a non-zero code
    And an error names "broken" and "gates[0].name"
    And no output directory is created

  # AC-4
  Scenario: The component listing reports gate counts
    Given a module "fastapi" declaring gates its CI runs
    And a module "bare" declaring no gates
    When the user lists components
    Then the listing shows "fastapi" with "2 gates"
    And the listing shows "bare" with "no gates declared"
