Feature: Scaffold generation
  As a developer starting a new project
  I want to generate a project scaffold from a YAML stack spec
  So that I have a complete BDD/TDD-ready project structure
  customised for my specific technology stack

  Background:
    Given the component library contains modules for "react-native", "fastapi", and "firebase"

  # AC-1
  Scenario: Valid stack spec generates a complete scaffold
    Given a valid stack spec with name "vocal-app", platform "mobile"
    And the spec declares frontend component "react-native"
    And the spec declares backend component "fastapi"
    And the spec declares database component "firebase"
    When the user runs the scaffold generator with the spec
    Then the output directory is created
    And the scaffold contains "AGENTS.md"
    And the scaffold contains "ARCHITECTURE.md"
    And the scaffold contains "docs/EVALUATOR.md"
    And the scaffold contains "docs/DESIGN.md"
    And the scaffold contains "docs/QUALITY_SCORE.md"
    And the scaffold contains "docs/RELIABILITY.md"
    And the scaffold contains "docs/SECURITY.md"
    And "ARCHITECTURE.md" contains a section for "react-native"
    And "ARCHITECTURE.md" contains a section for "fastapi"
    And "ARCHITECTURE.md" contains a section for "firebase"
    And "docs/RELIABILITY.md" contains a section for "react-native"
    And "docs/RELIABILITY.md" contains a section for "fastapi"
    And "docs/RELIABILITY.md" contains a section for "firebase"
    And "docs/SECURITY.md" contains a section for "react-native"
    And "docs/SECURITY.md" contains a section for "fastapi"
    And "docs/SECURITY.md" contains a section for "firebase"
    And the scaffold contains "ci.yml"
    And "ci.yml" contains a job block for "react-native"
    And "ci.yml" contains a job block for "fastapi"
    And "ci.yml" contains a job block for "firebase"
    And "AGENTS.md" contains a repository map row for "react-native"
    And "AGENTS.md" contains a repository map row for "fastapi"
    And "AGENTS.md" contains a repository map row for "firebase"

  # AC-2
  Scenario: Unknown component produces a placeholder, not a failure
    Given a valid stack spec with name "test-app", platform "mobile"
    And the spec declares database component "supabase"
    When the user runs the scaffold generator with the spec
    Then the generator exits successfully
    And a warning is printed for unknown component "supabase"
    And "ARCHITECTURE.md" contains placeholder text for "supabase"
    And the placeholder references "MODULE_AUTHORING.md"

  # AC-3
  Scenario: Invalid spec produces a clear error and no output
    Given a stack spec file missing the required "name" field
    When the user runs the scaffold generator with the spec
    Then the generator exits with a non-zero code
    And an error is printed to stderr mentioning "name"
    And no output directory is created

  # AC-3
  Scenario: Component name resembling a filesystem path is rejected
    Given a valid stack spec with name "test-app", platform "mobile"
    And the spec declares backend component "../../etc/passwd"
    When the user runs the scaffold generator with the spec
    Then the generator exits with a non-zero code
    And an error is printed to stderr mentioning "backend"
    And no output directory is created

  # AC-4
  Scenario: --validate accepts a valid spec without generating output
    Given a valid stack spec with name "vocal-app", platform "mobile"
    When the user runs the scaffold generator with --validate
    Then the generator exits successfully
    And no output directory is created

  Scenario: --validate rejects an invalid spec
    Given a stack spec file with an invalid platform value "tablet"
    When the user runs the scaffold generator with --validate
    Then the generator exits with a non-zero code
    And an error is printed to stderr mentioning "platform"

  # AC-6
  Scenario: Unwritable output path fails before generation
    Given a valid stack spec with name "vocal-app", platform "mobile"
    And the spec declares backend component "fastapi"
    And the output path is inside an unwritable directory
    When the user runs the scaffold generator with the spec
    Then the generator exits with a non-zero code
    And an error is printed to stderr mentioning "not writable"
    And no output directory is created

  # AC-7
  Scenario: Bundled library generates a contract-clean scaffold out of the box
    Given the component library and core templates bundled with this repository
    And a valid stack spec with name "vocal-app", platform "mobile"
    And the spec declares frontend component "react-native"
    And the spec declares backend component "fastapi"
    And the spec declares database component "firebase"
    When the user runs the scaffold generator with the spec
    Then the generator exits successfully
    And no warnings are printed
    And the scaffold contains "AGENTS.md"
    And the scaffold contains "ci.yml"
    And "ARCHITECTURE.md" contains a section for "react-native"
    And "docs/RELIABILITY.md" contains a section for "fastapi"
    And "docs/SECURITY.md" contains a section for "firebase"
    And "ci.yml" contains a job block for "react-native"
    And "ci.yml" contains a job block for "fastapi"
    And "ci.yml" contains a job block for "firebase"
    And "AGENTS.md" contains a repository map row for "react-native"
    And "AGENTS.md" contains a repository map row for "fastapi"
    And "AGENTS.md" contains a repository map row for "firebase"

  # AC-7
  Scenario: Bundled library covers a web stack with inference
    Given the component library and core templates bundled with this repository
    And a valid stack spec with name "web-app", platform "web"
    And the spec declares frontend component "nextjs"
    And the spec declares backend component "fastapi"
    And the spec declares database component "postgres"
    And the spec declares inference component "pytorch"
    When the user runs the scaffold generator with the spec
    Then the generator exits successfully
    And no warnings are printed
    And "ARCHITECTURE.md" contains a section for "nextjs"
    And "docs/RELIABILITY.md" contains a section for "postgres"
    And "docs/SECURITY.md" contains a section for "pytorch"
    And "ci.yml" contains a job block for "nextjs"
    And "ci.yml" contains a job block for "postgres"
    And "ci.yml" contains a job block for "pytorch"
    And "AGENTS.md" contains a repository map row for "nextjs"
    And "AGENTS.md" contains a repository map row for "postgres"
    And "AGENTS.md" contains a repository map row for "pytorch"

  # AC-5
  Scenario: --list-components prints available modules by category
    When the user runs the scaffold generator with --list-components
    Then the generator exits successfully
    And the output lists "react-native" under "frontend"
    And the output lists "fastapi" under "backend"
    And the output lists "firebase" under "database"
