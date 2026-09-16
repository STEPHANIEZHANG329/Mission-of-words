# Scriveno Integration Boundary

Scriveno is integrated as a third-party workflow engine for long-form writing and publishing preparation. It does not own the KDP production pipeline.

## Scriveno responsibilities

- project/work initialization for writing workflows
- outline and planning support
- drafting and revision
- editor review
- continuity checking
- Voice DNA / style consistency
- front matter and back matter preparation
- manuscript state/progress
- publishing-preparation workflow

## Responsibilities that remain outside Scriveno

- paid image generation and provider selection
- image budget / spend controls
- coloring, maze, search-and-find, matching, or other activity generation
- KDP trim-size calculations
- bleed and gutter calculations
- spine calculations
- cover rendering
- final PDF composition and preflight
- KDP upload or release approval

The production contract in `PRODUCTION_TASK.md` remains authoritative for the current book.

## Local setup

Requires Node.js 20 or newer.

```bash
npm install
npm run scriveno:init
npm run scriveno:status
npm run scriveno:sync:check
```

The repository pins Scriveno to 3.8.0 so upstream changes do not silently alter the production workflow.

## Change-control rule

Do not allow Scriveno initialization or generated workflow files to overwrite the existing production contract or paid-image rules. Inspect generated changes before committing them. Major architecture changes require separate approval.
