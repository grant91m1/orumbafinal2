# Orumba North LGA

Flask website for Orumba North Local Government Area.

## Run locally

Install the dependencies with `pip install -r requirements.txt`, then run `python run.py`.
The local site is served at `http://127.0.0.1:5000`.

## Host on Render

Use the included `render.yaml` Blueprint. Before deploying, create a Supabase project, run
the current `supabase_schema.sql` in its SQL Editor (including when upgrading an existing
project, to add the event image and private contact-message storage), and set `SECRET_KEY`,
`SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY` in Render. Keep the service role key server-side only. The app
intentionally fails to start in production if required credentials or cloud-storage mode are
missing, because local JSON storage is not durable on Render. Create a public Supabase Storage
bucket named `uploads` with a 5 MB image-only limit; the Render blueprint selects it.
Contact form submissions are stored in the private `contact_messages` table; configure an
operational process to review and respond to those submissions.

For rate limits that persist across restarts or multiple instances, set `RATELIMIT_STORAGE_URI`
to a shared Redis-compatible service. The Vercel configuration is not a supported deployment
path yet; use Render for now.