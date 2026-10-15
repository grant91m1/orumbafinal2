# Render Deployment Instructions for Flask Beautiful Website

This document provides step-by-step instructions to deploy your Flask app on Render.

## 1. Prepare Your Project

- Ensure your project has a `render.yaml` file configured for your service.
- Confirm your `requirements.txt` includes all dependencies.
- Make sure your app listens on the port Render expects (default 10000).
- Use `gunicorn` as the production server in your start command.

## 2. Connect to Render

- Log in to your Render account.
- Click "New" > "Web Service".
- Connect your GitHub repository containing the project.

## 3. Configure the Web Service

- Name your service (e.g., `flask-beautiful-website`).
- Select the branch to deploy (e.g., `main`).
- Set the environment to Python.
- Use the build command: `pip install -r requirements.txt`.
- Use the start command: `gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:application`.
- Add environment variables:
  - `SECRET_KEY`: A long, random production secret.
  - `SUPABASE_URL`: Your Supabase project URL.
  - `SUPABASE_SERVICE_ROLE_KEY`: Server-only service role key; never expose it in frontend code.
  - `USE_CLOUD_STORAGE`: `true`.
  - `SUPABASE_STORAGE_BUCKET`: Public Supabase Storage bucket name, normally `uploads`.

Run `supabase_schema.sql` in the Supabase SQL Editor before deploying. Create a public Storage
bucket named `uploads` with a 5 MB limit and image-only MIME types. The application fails to
start in production if required credentials or cloud-storage mode are missing. User and content
data require this Supabase connection; local JSON files are not durable on Render.

## 4. Deploy and Monitor

- Click "Create Web Service" to start deployment.
- Monitor the build and deploy logs for errors.
- Once deployed, Render will provide a URL for your app.

## 5. Post-Deployment

- Test your app by visiting the Render URL.
- Check logs and metrics in the Render dashboard.
- Update your code and push to GitHub to trigger automatic redeploys.
- Set `RATELIMIT_STORAGE_URI` to a shared Redis-compatible service if rate limits must persist
  across restarts or multiple instances; the default in-memory limiter resets on restart.

## Troubleshooting

- If deployment fails, check for missing dependencies or syntax errors.
- Ensure your app uses the correct port and start command.
- Use Render's documentation and support for help.

## Additional Resources

- [Render Flask Deployment Docs](https://render.com/docs/deploy-flask)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/latest/deploying/)
