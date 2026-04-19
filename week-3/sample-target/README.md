# Sample Target — Week 2 URL Shortener

This directory contains a copy of the Week 2 URL shortener used as the target
for the Governed AI Pipeline's slash commands and hooks.

## Why This Exists

The Week 3 pipeline needs a realistic codebase to demonstrate `/review`,
`/test-gen`, `/commit`, and `/ship` workflows. Rather than modifying `week-2/`
directly (which is frozen as a completed deliverable), we copy the source here
and operate on it.

## What's Committed

- `README.md` — this file
- `tests/shorten.test.ts` — representative test file for demo purposes

## What's Gitignored

Source files (`src/`, `node_modules/`, `dist/`, `*.lock`) are gitignored because
they are exact copies of `week-2/src/`. The pipeline operates on the local copy
but only curated demo files are committed to avoid duplication.

## Stack

- Hono + TypeScript (ESM)
- Vitest for testing
- In-memory data store
- REQ-SHORT-001 through REQ-SHORT-007 traceability
