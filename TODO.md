# Project TODO

- [x] Inspect Flask entrypoints/routes and deployment configs (`app.py`, `wsgi.py`, `api/index.py`, `render.yaml`, `vercel.json`).
- [x] Identify global deployment misrouting risk: Render/Vercel configured to route to `api/index.py` instead of Flask WSGI.
- [x] Create `TODO-global-deployment-fix.md` to track the global deployment fixes.
- [x] Fix `vercel.json` to build/route using `wsgi.py` (instead of `api/index.py`).

- [x] Confirm `render.yaml` is valid YAML/has correct indentation and correct gunicorn target.

- [x] Fix/verify `wsgi.py` export name matches gunicorn target.


- [ ] Deploy and verify key paths:

  - [ ] `GET /` returns homepage
  - [ ] `GET /api/public/posts` returns JSON
  - [ ] `GET /static/css/...` returns 200

