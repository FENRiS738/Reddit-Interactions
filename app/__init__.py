# Built Ins
import os

# Installeds
from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

# Custom Builts
from .middlewares import rate_limit
from .routes import reddit

app = FastAPI(docs_url="/app")

# Loading environment variables
load_dotenv()
SESSION_SECRET = os.getenv("SESSION_SECRET")

# Server Configurations
app.include_router(reddit.routes)
app.add_middleware(rate_limit.RateLimitMiddleware)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# Server Health Check Endpoints
@app.get('/')
async def read_root():
    try: 
        return JSONResponse({
            "message": "Server is running...",
        }, status_code=200)
    except Exception as ex:
        return JSONResponse({
            "message": "Something went wrong..."
        }, status_code=500)