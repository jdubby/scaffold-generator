Feature: Scaffold package import
  As a user holding a scaffold package exported by an upstream tool
  I want to pass the package directory straight to the generator
  So that the scaffold is generated and the package content lands in place
  without manual copying

  Background:
    Given the component library contains modules for "react-native", "fastapi", and "firebase"

  # AC-1
  Scenario: Package directory generates a scaffold with content overlaid
    Given a scaffold package with a valid stack spec named "snapsell"
    And the package contains "docs/product-specs/snapsell.md"
    And the package contains "docs/exec-plans/active/snapsell-mvp.md"
    And the package contains "tests/features/discovery.feature"
    And the package contains a hidden file ".DS_Store"
    When the user runs the scaffold generator with the package directory
    Then the generator exits successfully
    And the scaffold contains "AGENTS.md"
    And the scaffold contains "docs/product-specs/snapsell.md"
    And the scaffold contains "docs/exec-plans/active/snapsell-mvp.md"
    And the scaffold contains "tests/features/discovery.feature"
    And the scaffold does not contain "stack-spec.yml"
    And the scaffold does not contain ".DS_Store"

  # AC-2
  Scenario: Imported product specs are indexed
    Given a scaffold package with a valid stack spec named "snapsell"
    And the package contains "docs/product-specs/snapsell.md"
    When the user runs the scaffold generator with the package directory
    Then the generator exits successfully
    And "docs/product-specs/index.md" links to "snapsell.md"
    And "docs/product-specs/index.md" does not contain "_none yet_"

  # AC-3
  Scenario: Domain map table is merged into ARCHITECTURE.md
    Given a scaffold package with a valid stack spec named "snapsell"
    And the package contains a domain map with a row for "SnapSell Core"
    When the user runs the scaffold generator with the package directory
    Then the generator exits successfully
    And "ARCHITECTURE.md" contains a domain map row for "SnapSell Core"
    And the scaffold does not contain "docs/domain-map.md"

  # AC-4
  Scenario: Directory without a stack spec fails clearly
    Given a directory that is not a scaffold package
    When the user runs the scaffold generator with the package directory
    Then the generator exits with a non-zero code
    And an error is printed to stderr mentioning "stack-spec.yml"
    And no output directory is created

  # AC-5
  Scenario: Every scaffold includes the workflow directories
    Given a valid stack spec with name "vocal-app", platform "mobile"
    And the spec declares backend component "fastapi"
    When the user runs the scaffold generator with the spec
    Then the generator exits successfully
    And the scaffold has directory "tests/features"
    And the scaffold has directory "docs/exec-plans/active"

  # AC-6
  Scenario: Unknown component warning names the available category modules
    Given the component library also contains inference module "pytorch"
    And a valid stack spec with name "snapsell", platform "hybrid"
    And the spec declares inference component "python-based-ai-models"
    When the user runs the scaffold generator with the spec
    Then the generator exits successfully
    And a warning is printed for unknown component "python-based-ai-models"
    And the warning suggests available inference module "pytorch"

  # AC-7
  Scenario: Import summary lists the overlaid content
    Given a scaffold package with a valid stack spec named "snapsell"
    And the package contains "docs/product-specs/snapsell.md"
    And the package contains "tests/features/discovery.feature"
    And the package contains a domain map with a row for "SnapSell Core"
    When the user runs the scaffold generator with the package directory
    Then the generator exits successfully
    And the output reports overlaid file "docs/product-specs/snapsell.md"
    And the output reports overlaid file "tests/features/discovery.feature"
    And the output reports the domain map was merged
