# Task: Sidebar Navigation and Search

**Status:** [x] Completed

**Dependencies:** Epic 03 task-03 (HTML template must exist)

## Context

- Language: JavaScript (inline in HTML template)
- Framework: None (vanilla JS)
- Testing: Manual (open in browser)
- Database: None

Implement the two-level sidebar navigation with search filtering and active section tracking via scroll position. All JavaScript must be inline in the HTML template's `<script>` tag.

## Needed from User

None

## Instructions

1. Add navigation generation logic to `generate_docs.py`:
   - Function `generate_sidebar_html(sections: list) -> str`
   - For each section, generate:
     ```html
     <div class="nav-section" data-section-id="section-{slug}">
       <a href="#section-{slug}" class="nav-link">{title}</a>
       <div class="nav-subsections">
         <!-- For each h2/h3 found in the section content -->
         <a href="#subsection-{sub-slug}" class="nav-sublink">{subtitle}</a>
       </div>
     </div>
     ```
   - Add an appendix separator before sections with `order >= 99`:
     ```html
     <div class="nav-separator"></div>
     ```

2. Subsection extraction:
   - After converting markdown to HTML, parse the output for `<h2>` and `<h3>` tags
   - Extract their text content as subsection labels
   - Generate unique IDs for each: `subsection-{section-slug}-{heading-slug}`
   - Inject `id` attributes into the heading tags in the HTML content

3. Add the search input at the top of the sidebar:
   ```html
   <div class="sidebar-header">
     <h2 class="sidebar-title">{project_name}</h2>
     <input type="text" class="sidebar-search" placeholder="Search sections..." />
   </div>
   ```

4. Implement search filtering in JavaScript (inline in template `<script>`):
   ```javascript
   // Search: filter nav items by title text
   const searchInput = document.querySelector('.sidebar-search');
   searchInput.addEventListener('input', function() {
       const query = this.value.toLowerCase();
       document.querySelectorAll('.nav-section').forEach(section => {
           const title = section.querySelector('.nav-link').textContent.toLowerCase();
           const subsections = section.querySelectorAll('.nav-sublink');
           let matchesAny = title.includes(query);
           subsections.forEach(sub => {
               const subMatch = sub.textContent.toLowerCase().includes(query);
               sub.style.display = subMatch || title.includes(query) ? '' : 'none';
               if (subMatch) matchesAny = true;
           });
           section.style.display = matchesAny ? '' : 'none';
       });
   });
   ```

5. Implement scroll-based active section tracking in JavaScript:
   ```javascript
   // Scroll tracking: highlight active nav item
   const observer = new IntersectionObserver((entries) => {
       entries.forEach(entry => {
           if (entry.isIntersecting) {
               document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
               const id = entry.target.id;
               const navLink = document.querySelector(`[href="#${id}"]`);
               if (navLink) navLink.classList.add('active');
           }
       });
   }, { rootMargin: '-20% 0px -80% 0px' });

   document.querySelectorAll('.section-heading').forEach(h => observer.observe(h));
   ```

6. Add smooth scrolling CSS:
   ```css
   html { scroll-behavior: smooth; }
   ```

## Acceptance Criteria

- [x] Sidebar shows all sections as top-level nav links
- [x] Each section expands to show h2/h3 subsections
- [x] Search input filters both sections and subsections as user types
- [x] Active section is highlighted based on scroll position
- [x] Clicking a nav link smooth-scrolls to the section
- [x] Appendix sections are visually separated from main sections
- [x] All heading tags in content have unique `id` attributes for linking
- [x] All JavaScript is inline (no external scripts)

## Implementation Notes

- Added `extract_subsections(html_content, section_slug)` to `generate_docs.py` that uses regex to find `<h2>`/`<h3>` tags, injects unique `id` attributes (`subsection-{section_slug}-{heading_slug}`), and returns subsection metadata for sidebar generation.
- Added `generate_sidebar_html(sections)` to `generate_docs.py` that builds nav-section divs with nav-link and nav-subsections, inserting an `appendix-separator` div before sections with `order >= 99`.
- Updated the HTML template sidebar to include a `sidebar-header` with project name and search input, wrapping nav content in a `sidebar-nav` div.
- Added inline JavaScript for search filtering (filters nav-section visibility by matching query against nav-link and nav-sublink text) and IntersectionObserver-based scroll tracking (highlights active nav-link/nav-sublink based on viewport position).
- All JS uses doubled curly braces for Python `.format()` template compatibility.
- Updated CSS selectors from `.nav-subsection a` to `.nav-subsections .nav-sublink` to match generated HTML class names.
