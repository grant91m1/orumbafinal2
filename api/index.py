from app import app

# Vercel serverless handler
def handler(event, context):
    return app(event, context)

