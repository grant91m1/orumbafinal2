# TODO: Global deployment fixes (static assets/CSS 404)

## Problem
Deployed site shows console errors like:
- `Failed to load resource: the server responded with a status of 404` for:
  - `/static/css/navbar.css`
  - `/static/css/mobile-global.css`
  - `/static/css/global-theme.css`
  - images like `/static/images/orumba-north-logo.jpg`

This causes the navbar + typography/theme styles to not apply.

## Fix implemented
### 1) Ensure Flask points to correct static + template directories
- File: `app.py`
- Updated `Flask(... static_folder=..., template_folder=...)` to use absolute paths from `BASE_DIR`.

This ensures that when the app runs in different environments (including Vercel), `/static/*` resolves correctly.

## Next steps
1) Re-deploy to Vercel.
2) Verify in browser DevTools Network tab that these return 200:
   - `/static/css/navbar.css`
   - `/static/css/mobile-global.css`
   - `/static/css/global-theme.css`
   - `/static/images/orumba-north-logo.jpg`
3) If any still 404, then the issue is Vercel static-file routing/build config.
   - In that case, adjust Vercel config/build to ensure `static/` is included and served.

