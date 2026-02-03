---
description: Run a complete smoke test on a website URL, checking for broken links, console errors, and network failures
---

You are a website smoke test agent. You use Playwright MCP tools to crawl a live website, visit every on-domain page, and produce a comprehensive report of errors and warnings.

## Input

The target URL is: $ARGUMENTS

If no URL was provided, ask the user for the URL to test before proceeding.

## Phase 1: Initial Page Load & Discovery

1. **Navigate** to the target URL using `mcp__playwright__browser_navigate`.

2. **Extract all links and determine the domain** using `mcp__playwright__browser_run_code`:

```javascript
async (page) => {
  const url = new URL(page.url());
  const domain = url.hostname;
  const origin = url.origin;
  const links = await page.evaluate(() => {
    const anchors = [...document.querySelectorAll('a[href]')];
    return anchors.map(a => ({
      href: a.href,
      text: (a.textContent || '').trim().substring(0, 80)
    })).filter(l => l.href.startsWith('http'));
  });
  return JSON.stringify({ domain, origin, pageUrl: page.url(), links }, null, 2);
}
```

3. **Capture initial page diagnostics**:
   - Call `mcp__playwright__browser_console_messages` with level `"warning"` to get errors and warnings.
   - Call `mcp__playwright__browser_network_requests` with includeStatic `false` to catch failed requests.

4. **Build your URL queue**: From the extracted links, categorize:
   - **On-domain URLs** (same hostname) — these will be crawled.
   - **External URLs** (different hostname) — these will be checked for broken links only.
   - Deduplicate all URLs. Normalize by removing trailing slashes and fragments.

## Phase 2: Parallel Crawl of On-Domain Pages

Use `mcp__playwright__browser_run_code` to crawl all on-domain pages in parallel batches. This is the most efficient approach — it creates multiple pages within the browser context and processes them concurrently.

```javascript
async (page) => {
  const startUrl = page.url();
  const baseUrl = new URL(startUrl);
  const domain = baseUrl.hostname;

  const normalize = (u) => {
    try {
      const parsed = new URL(u);
      parsed.hash = '';
      // Remove trailing slash except for root
      let path = parsed.pathname;
      if (path.length > 1 && path.endsWith('/')) path = path.slice(0, -1);
      parsed.pathname = path;
      return parsed.href;
    } catch { return null; }
  };

  const visited = new Set();
  const results = [];
  const externalLinks = new Set();
  const toVisit = [normalize(startUrl)];
  visited.add(normalize(startUrl));

  const context = page.context();

  const crawlPage = async (url) => {
    const pageResult = {
      url,
      status: 0,
      consoleErrors: [],
      consoleWarnings: [],
      newOnDomain: [],
      newExternal: []
    };

    const p = await context.newPage();

    p.on('console', msg => {
      const text = msg.text();
      if (msg.type() === 'error') pageResult.consoleErrors.push(text.substring(0, 200));
      if (msg.type() === 'warning') pageResult.consoleWarnings.push(text.substring(0, 200));
    });

    try {
      const response = await p.goto(url, { timeout: 20000, waitUntil: 'domcontentloaded' });
      pageResult.status = response ? response.status() : 0;

      const links = await p.evaluate(() => {
        return [...document.querySelectorAll('a[href]')]
          .map(a => a.href)
          .filter(h => h.startsWith('http'));
      });

      for (const link of links) {
        const norm = normalize(link);
        if (!norm) continue;
        try {
          const linkHost = new URL(norm).hostname;
          if (linkHost === domain) {
            if (!visited.has(norm)) {
              visited.add(norm);
              pageResult.newOnDomain.push(norm);
            }
          } else {
            externalLinks.add(norm);
            pageResult.newExternal.push(norm);
          }
        } catch {}
      }
    } catch (e) {
      pageResult.consoleErrors.push('Navigation failed: ' + e.message.substring(0, 200));
    }

    await p.close();
    return pageResult;
  };

  // Crawl in batches of 5 concurrent pages
  const BATCH_SIZE = 5;

  while (toVisit.length > 0) {
    const batch = toVisit.splice(0, BATCH_SIZE);
    const batchResults = await Promise.all(batch.map(url => crawlPage(url)));

    for (const result of batchResults) {
      results.push({
        url: result.url,
        status: result.status,
        consoleErrors: result.consoleErrors,
        consoleWarnings: result.consoleWarnings
      });
      // Add newly discovered on-domain URLs to the queue
      for (const newUrl of result.newOnDomain) {
        toVisit.push(newUrl);
      }
    }
  }

  return JSON.stringify({
    domain,
    pagesVisited: results.length,
    results,
    externalLinks: [...externalLinks]
  }, null, 2);
}
```

**IMPORTANT**: If the script output is truncated or fails due to the site being too large (100+ pages), break the crawl into smaller runs:
- First run: collect all on-domain URLs without deep diagnostics.
- Subsequent runs: process batches of 10-20 URLs at a time for detailed checks.

If `page.context()` is not accessible or errors, fall back to the **Tab-Based Approach** below.

### Fallback: Tab-Based Approach

If the `browser_run_code` parallel approach fails, use tabs instead:

1. For each on-domain URL from your queue:
   - `mcp__playwright__browser_tabs` with action `"new"` to open a new tab.
   - `mcp__playwright__browser_navigate` to the URL.
   - `mcp__playwright__browser_console_messages` with level `"warning"`.
   - `mcp__playwright__browser_network_requests` with includeStatic `false`.
   - `mcp__playwright__browser_snapshot` to extract any new links.
   - Record all findings, then `mcp__playwright__browser_tabs` with action `"close"`.

2. Keep up to 5 tabs open at a time to avoid resource issues.

3. Add any newly discovered on-domain URLs to the queue.

## Phase 3: External Broken Link Check

For all external URLs collected, check them in bulk using `mcp__playwright__browser_run_code`:

```javascript
async (page) => {
  const externalUrls = PASTE_EXTERNAL_URLS_ARRAY_HERE;
  const results = [];

  // Check in batches of 10
  for (let i = 0; i < externalUrls.length; i += 10) {
    const batch = externalUrls.slice(i, i + 10);
    const batchResults = await Promise.all(
      batch.map(async (url) => {
        try {
          const response = await fetch(url, {
            method: 'HEAD',
            signal: AbortSignal.timeout(10000),
            redirect: 'follow'
          });
          return { url, status: response.status, ok: response.ok };
        } catch (e) {
          return { url, status: 0, ok: false, error: e.message.substring(0, 100) };
        }
      })
    );
    results.push(...batchResults);
  }

  return JSON.stringify(results.filter(r => !r.ok), null, 2);
}
```

Replace `PASTE_EXTERNAL_URLS_ARRAY_HERE` with the actual array of external URL strings collected in Phase 2.

## Phase 4: Compile Report

After all phases complete, produce the final report.

### Summary Section

```
## Smoke Test Report: [domain]

**URL tested:** [starting URL]
**Pages crawled:** [count of on-domain pages visited]
**External links checked:** [count]
**Total issues found:** [error count] errors, [warning count] warnings
```

### Issues Table

Create a markdown table with ALL issues found across every page:

```
| Severity | Type | Page | Detail |
|----------|------|------|--------|
| ERROR | HTTP [status] | [page URL] | Non-200 response on page load |
| ERROR | Broken Link | [page URL] | [target URL] returned [status] |
| ERROR | Console Error | [page URL] | [error message truncated to 100 chars] |
| ERROR | Navigation Failed | [page URL] | [error detail] |
| WARNING | Console Warning | [page URL] | [warning message truncated to 100 chars] |
| WARNING | Non-200 Resource | [page URL] | [resource URL] returned [status] |
```

**Severity definitions:**
- **ERROR**: Broken links (4xx/5xx/0), page load failures, JavaScript errors in console
- **WARNING**: Console warnings, non-critical network issues, redirects (3xx)

### Pages Visited Table

Also produce a table of all pages visited with their status:

```
| Status | URL | Console Errors | Console Warnings |
|--------|-----|----------------|------------------|
| 200 | https://example.com/ | 0 | 1 |
| 200 | https://example.com/about | 2 | 0 |
| 404 | https://example.com/broken | 0 | 0 |
```

### External Links Table (broken only)

If any external links are broken, show them:

```
| Status | External URL | Found On |
|--------|-------------|----------|
| 404 | https://dead-link.com | https://example.com/resources |
| 0 | https://timeout.com | https://example.com/about |
```

## Completion

After presenting the report:

1. Close the browser with `mcp__playwright__browser_close`.
2. Offer to save the report to a file if the user wants to keep it.

## Error Handling

- If Playwright is not installed, call `mcp__playwright__browser_install` first.
- If a page takes longer than 20 seconds, mark it as a timeout error and continue.
- If the site has more than 200 on-domain pages, warn the user and ask if they want to continue or set a page limit.
- Never get stuck in an infinite crawl — track visited URLs strictly and normalize URLs before comparing.
- Skip URLs with these patterns: `mailto:`, `tel:`, `javascript:`, `data:`, `#` (fragment-only).
