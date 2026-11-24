# Contributing

Start with the [project setup](README.md#setup). Whether you write the change
yourself or work with a coding agent, a reviewer should be able to follow the
behavior from the product requirement to a test they can run.

## Describe the change

For a bug report, include the smallest steps that reproduce it, what you expected,
and what happened. For a feature, describe who needs it and what they should be
able to do. Use synthetic examples in public issues and pull requests.

## Make a behavior change

1. Find the relevant acceptance criterion in the [product specs](docs/product-specs/index.md).
   If the behavior has no spec, use the template there to write one.
2. Write or update an [acceptance scenario](tests/features/) before implementation.
   Describe an action and an observable outcome. For example, if the spec
   promises duplicate protection, submit the same request twice and check that
   only one record appears.
3. Write one unit test for the next increment. Run it against the existing code
   and check that its assertion fails for the expected reason. Capture the test
   command, failing assertion, and test-only revision or patch for the reviewer.
4. Make the smallest implementation change that passes the test. Once the suite
   is green, refactor as needed. Follow the [project architecture](ARCHITECTURE.md)
   and cover failure paths where the change touches an external dependency.
5. Run every command in the [project's quality gates](AGENTS.md#quality-gates).
   Update the README when setup, commands, or visible behavior changes.

For a documentation-only correction, identify the inaccurate instruction and
verify the corrected command, example, or link.

## Submit for review

Use the [review handoff](docs/EVALUATOR.md#review-handoff) in the pull request
or versioned task record. Link the acceptance criterion, the exact revision or
patch, the original failing run, and the final gate results. Include the steps
a reviewer can use to exercise the change. If the original failing run is
missing, mark the sequence unverified.

Keep customer data, credentials, and raw private logs out of public review
records. Use a synthetic fixture or a public-safe summary. Share restricted
evidence with an authorized reviewer separately.

A separate reviewer or a solo contributor performing self-review records the
review mode, four grades with evidence, and a verdict for the reviewed revision.
If a gate fails or any grade falls below B, address the finding and hand the
updated revision back for evaluation.
