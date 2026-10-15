# Orumba North LGA — Master Production Plan

## Information Gathered

**Project Type:** Flask web application for Orumba North Local Government Area (Nigeria)
**Deployment Target:** Vercel (serverless Python)
**Templates:** 25+ HTML templates across `app/templates/` and subfolders
**Styling:** Mixed glassmorphism + government green/gold theme, multiple CSS files with some conflicts
**Mobile State:** Navbar has dedicated mobile drawer (`navbar.css`), but many pages lack proper mobile breakpoints, have oversized text/images, broken grids, or inline styles that override responsive behavior
**Content Quality:** Inconsistent — some pages have placeholder names like "[Vice Chairman Name]", duplicate HTML sections (`newsroom.html` has duplicated hero), broken timeline on mobile (`history.html`), awkward phrasing
**Vercel Config:** `vercel.json` exists but references `api/index.py`; `wsgi.py` exists but imports from `app` which uses `app/__init__.py` with dynamic module loading — this chain needs verification

## Critical Issues Found

1. **CSS Conflicts:** `header-enhancements.css` starts with `display: none !important` on navbar classes, effectively disabling itself
2. **Duplicate HTML:** `newsroom.html` has two hero sections back-to-back (one outside `<section>`, one inside)
3. **Broken Mobile Layouts:** `history.html` timeline uses float-based 42% widths that collapse on mobile; `contact.html` has nested duplicate `.glass-card`; many heroes use `font-size: 3.5rem`/`4.5rem` without mobile scaling
4. **Placeholder Content:** Multiple pages contain `[Vice Chairman Name]`, `[Secretary Name]`, `Hon. Ward A Rep`, etc.
5. **Inconsistent CSS Linking:** Some pages link `glassmorphism.css`, some don't; some use inline `<style>` blocks with 100+ lines instead of external files
6. **Vercel Readiness:** Need to verify `requirements.txt` has all deps; `vercel.json` routes need static file handling confirmation

## Plan

### Phase 1 — Global Infrastructure Fixes
1. **Fix `vercel.json`** — confirm builds/routes, ensure static files served correctly
2. **Fix `requirements.txt`** — add missing dependencies (Flask, gunicorn already present; verify no others needed)
3. **Create `static/css/mobile-global.css`** — unified mobile-first utility file with responsive typography, spacing, container padding, and touch-friendly sizing
4. **Fix `_header.html`** — ensure all pages include consistent meta tags, viewport, and link `mobile-global.css`
5. **Fix `_footer.html`** — make it responsive, add useful links, professional copyright
6. **Consolidate CSS imports** — every template should link: `global-theme.css` → `navbar.css` → `mobile-global.css` → page-specific CSS

### Phase 2 — Content & Mobile Refactor (Page by Page)

**Batch A — Core Public Pages**
- `home.html` — reduce hero text sizes on mobile, fix stat-number overflow, ensure grid gaps don't cause horizontal scroll
- `about.html` — mobile grid to 1 column, professional copy rewrite
- `about/history.html` — replace float timeline with CSS Grid/Flexbox mobile-safe timeline, rewrite historical copy for clarity
- `about/landmarks-culture.html` — mobile grid, professional copy
- `about/people.html` — mobile grid, professional copy, fix `margin-top: 120px` causing hero cut-off
- `contact.html` — fix nested duplicate card, mobile form sizing, professional copy
- `services.html` — mobile grid, professional copy, fix placeholder contact links (1234567890)
- `map-explore.html` — responsive map iframe height, mobile info grid

**Batch B — Government Pages**
- `government.html` — mobile tabs, card grid to 1 column, professional copy, replace placeholder names
- `government/administration.html` — mobile tabs, card sizing, professional copy, replace placeholders
- `government/management-team.html` — mobile grid, professional bios, replace placeholders
- `members.html` — mobile grid (minmax too small at 200px), professional copy, add real names where known
- `departments.html` — verify existing mobile CSS works, professional copy

**Batch C — News & Media**
- `news_hub.html` — mobile grid, professional copy
- `newsroom.html` — REMOVE duplicate hero section, mobile grid, professional copy
- `news-announcements.html` — mobile grid, professional copy
- `upcoming-events.html` — mobile countdown sizing, card height on mobile, professional copy
- `post.html` — mobile article padding, typography scaling
- `gallery.html` — already has good mobile CSS, verify album title display

**Batch D — Auth & Create Pages**
- `login.html` — mobile container padding, form touch sizing
- `register.html` — same as login
- `create_post.html` — already has excellent mobile CSS, verify links
- `create_album.html` — already has excellent mobile CSS, verify links
- `create_event.html` — mobile form layout, unify styling with create_post/create_album
- `profile/profile.html` — mobile sidebar (transform off-canvas), main panel margin, card grids

### Phase 3 — Vercel Production Polish
1. Ensure `app.py` has proper `if __name__ == '__main__':` guard and doesn't run debug in production
2. Verify all `url_for` and static paths use correct leading slashes
3. Add error handlers (404, 500) templates
4. Final link audit — every `<link>` and `<script src>` uses absolute `/static/...` paths
5. Add `robots.txt` and basic SEO meta tags to all pages

## Dependent Files to Edit

- `vercel.json`
- `requirements.txt`
- `app.py` (minor production guard)
- `app/templates/_header.html`
- `app/templates/_footer.html`
- `static/css/mobile-global.css` (new)
- `static/css/global-theme.css` (add mobile utilities)
- ALL templates in `app/templates/` and subfolders (~25 files)

## Follow-up Steps
1. Local testing with `python app.py` or `flask run`
2. `vercel --prod` deployment
3. Mobile device testing (Chrome DevTools + actual device if possible)
4. Lighthouse audit for performance/accessibility/best-practices

