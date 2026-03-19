# Task: OpenAPI Renderer with Collapsible Endpoints

**Status:** [x] Completed

**Dependencies:** Epic 03 task-01 (script structure and loader must exist)

## Context

- Language: Python
- Framework: None (uses `json` stdlib and `pyyaml`)
- Testing: Manual (test with a sample OpenAPI spec)
- Database: None

Renders OpenAPI/Swagger specs as collapsible endpoint cards. Each endpoint shows method badge, path, description, parameters, and request/response schemas. Collapsed by default in browser, fully expanded in print.

## Needed from User

None

## Instructions

1. Add a `render_openapi(content: str, file_path: str) -> str` function to `generate_docs.py`

2. Parse the spec:
   ```python
   import json
   import yaml

   def render_openapi(content: str, file_path: str) -> str:
       if file_path.endswith('.json'):
           spec = json.loads(content)
       else:
           spec = yaml.safe_load(content)
   ```

3. Extract API metadata:
   - `info.title`, `info.version`, `info.description`
   - Render as a header block:
     ```html
     <div class="api-header">
       <h2>{title} <span class="api-version">v{version}</span></h2>
       <p>{description}</p>
     </div>
     ```

4. Iterate over `paths` and render each endpoint:
   ```html
   <div class="endpoint">
     <button class="endpoint-toggle" onclick="this.parentElement.classList.toggle('expanded')">
       <span class="method-badge method-{method}">{METHOD}</span>
       <span class="endpoint-path">{path}</span>
       <span class="endpoint-summary">{summary}</span>
       <span class="toggle-icon">&#9660;</span>
     </button>
     <div class="endpoint-details collapsible-content">
       <p class="endpoint-description">{description}</p>

       <!-- Parameters -->
       <div class="endpoint-params">
         <h4>Parameters</h4>
         <table>
           <tr><th>Name</th><th>In</th><th>Type</th><th>Required</th><th>Description</th></tr>
           <!-- for each parameter -->
           <tr><td>{name}</td><td>{in}</td><td>{type}</td><td>{required}</td><td>{description}</td></tr>
         </table>
       </div>

       <!-- Request Body -->
       <div class="endpoint-request">
         <h4>Request Body</h4>
         <pre><code>{schema_json}</code></pre>
       </div>

       <!-- Responses -->
       <div class="endpoint-responses">
         <h4>Responses</h4>
         <!-- for each response code -->
         <div class="response-code">
           <span class="status-code">{code}</span>: {description}
           <pre><code>{response_schema_json}</code></pre>
         </div>
       </div>
     </div>
   </div>
   ```

5. Add CSS for endpoint styling (append to the template CSS):

   **Method badges:**
   - `.method-get` — green (#10b981), white text
   - `.method-post` — blue (#3b82f6), white text
   - `.method-put` — orange (#f59e0b), white text
   - `.method-patch` — yellow (#eab308), dark text
   - `.method-delete` — red (#ef4444), white text

   **Collapsible behavior:**
   ```css
   .endpoint-details { display: none; padding: 16px; border: 1px solid #e0e0e0; border-top: none; }
   .endpoint.expanded .endpoint-details { display: block; }
   .endpoint-toggle { width: 100%; text-align: left; padding: 12px; border: 1px solid #e0e0e0; background: #fafafa; cursor: pointer; display: flex; align-items: center; gap: 8px; }
   .method-badge { padding: 2px 8px; border-radius: 3px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
   ```

6. Handle edge cases:
   - Missing `description` fields: use empty string
   - Missing `parameters`: skip the parameters section
   - Missing `requestBody`: skip the request body section
   - Schema `$ref` references: show the ref path as-is (don't resolve)
   - Nested objects in schemas: pretty-print with `json.dumps(schema, indent=2)`

## Acceptance Criteria

- [x] Parses both JSON and YAML OpenAPI specs
- [x] Renders API title, version, and description header
- [x] Each endpoint is a collapsible card (collapsed by default)
- [x] Method badges are color-coded (GET=green, POST=blue, PUT=orange, DELETE=red)
- [x] Parameters rendered as a table
- [x] Request body and response schemas rendered as formatted JSON
- [x] Gracefully handles missing fields (no crashes)
- [x] `@media print` CSS expands all endpoints (from Epic 03 task-03)

## Implementation Notes

- `render_openapi()` added to `rt-agents/scripts/generate_docs.py` (lines 289-463)
- `import json` added at top of file; `import yaml` placed after `ensure_dependencies()` call
- Parses JSON (`.json` extension) or YAML (all other extensions) via `json.loads` / `yaml.safe_load`
- API header renders `info.title`, `info.version`, `info.description` with HTML escaping
- Each endpoint renders as a `<div class="endpoint">` with toggle button and hidden details div
- Toggle uses inline `onclick` to add/remove `.expanded` class on the parent endpoint div
- Parameters section only rendered when parameters exist; uses a 5-column table (Name, In, Type, Required, Description)
- Parameter type extracted from `param.schema.type` (OpenAPI 3) or falls back to `param.type` (Swagger 2); `$ref` shown as-is
- Request body section only rendered when `requestBody` is present and non-empty
- Response schemas rendered per media type; also handles Swagger 2 style (`schema` directly on response object)
- All user-facing strings HTML-escaped via `html.escape()`; schemas pretty-printed with `json.dumps(indent=2)`
- CSS added to `rt-agents/templates/documentation.html` with double curly braces for `.format()` compatibility
- Print styles: `.endpoint-details` forced visible, `.toggle-icon` hidden, `.endpoint-toggle` border-bottom removed
