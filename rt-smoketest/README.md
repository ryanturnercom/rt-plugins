# rt-smoketest

Playwright-powered website smoke testing for Claude Code.

## Installation

Add to your Claude Code settings or install via the rt-plugins marketplace.

## Available Commands

### `/rt-smoketest:url`

Runs a complete smoke test on a website URL using Playwright MCP.

**Usage:**
```
/rt-smoketest:url https://example.com
```

**What it does:**

1. **Crawls all on-domain pages** starting from the provided URL
2. **Checks for broken links** (both internal and external)
3. **Captures console errors and warnings** on every page
4. **Detects network failures** (non-200 responses)
5. **Reports everything** in a structured table

**Features:**
- Parallel page crawling using multiple browser pages (batches of 5)
- Automatic link discovery and deduplication
- External link validation via HEAD requests
- Falls back to tab-based crawling if needed
- Handles large sites with pagination warnings

**Output:**

Produces three tables:
- **Issues Table** — All errors and warnings with severity, type, page, and detail
- **Pages Visited** — Every on-domain page with its HTTP status and error/warning counts
- **Broken External Links** — Any off-domain links that returned non-200 status

## Requirements

- Playwright MCP server must be configured and running
- Browser must be installed (agent will auto-install if needed)
