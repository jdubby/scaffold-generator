"""Shared pytest configuration.

Module unit tests substitute the FileSystem boundary with
scaffold_generator.filesystem.InMemoryFileSystem. BDD scenarios and CLI-level
tests deliberately run against the real filesystem inside pytest tmp_path
sandboxes — see the mocking rules in AGENTS.md.
"""
