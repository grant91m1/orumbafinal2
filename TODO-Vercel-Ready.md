# Vercel Production Readiness Plan
Status: Planning - Not Ready

**Information Gathered:**
- vercel.json points to `api/index.py` but app.py is main Flask app.
- Local SQLite `app/instance/app.db` + JSON files - needs PostgreSQL/cloud storage.
- No env vars for SECRET_KEY, DB_URL.
- Flask app needs serverless function wrapper.
- render.yaml exists but Vercel needs specific config.

**Plan:**
1. **vercel.json**: Update to Flask app.py builds/routes.
2. **api/vercel.py**: Create serverless entrypoint (`from app import app`).
3. **Database**: Migrate to Vercel Postgres, env vars.
4. **Static**: Ensure templates/static served.
5. **requirements.txt**: Add gunicorn/psycopg2-binary.

**Dependent Files:**
- vercel.json (edit)
- New: api/vercel.py
- app.py (DB migrate)
- requirements.txt (add deps)

**Followup:**
- Add Vercel Postgres.
- Test deploy.
- Create PR.

**Ready Status: ⚠️ Partially Ready - DB migration pending**

Approve plan to proceed?
