# Built Ins
import os
import base64
import time

# Installeds
from fastapi import Request, HTTPException, status
import httpx
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()
CLIENT_ID=os.getenv("ID")
CLIENT_SECRET=os.getenv("SECRET")
REDIRECT_URI=os.getenv("REDIRECT_URI")


async def get_reddit_access_token(code: str):
    url = 'https://www.reddit.com/api/v1/access_token'

    # Construct HTTP Basic Auth header
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    basic_auth = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    # Calling reddit endpoint to generate parmanent access token
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, headers=headers, data=data)
    
        return response.json()



async def refresh_reddit_access_token(refresh_token: str):
    url = 'https://www.reddit.com/api/v1/access_token'

    # Construct HTTP Basic Auth header
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    basic_auth = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token' : refresh_token
    }

    # Calling reddit endpoint to refresh parmanent access token
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, headers=headers, data=data)
    
        return response.json()


async def validate_reddit_token(request: Request):
    user_data = request.session.get('user')

    # Checking if the user data is in session or not 
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Reddit session found.")

    expires_at = user_data.get("expires_at")
    now = time.time()

    # Checking if the access token expires, if yes then refresh it and update it
    if expires_at and now > expires_at:
        new_tokens = await refresh_reddit_access_token(user_data['refresh_token'])
        
        user_data['access_token'] = new_tokens['access_token']
        user_data['expires_at'] = time.time() + new_tokens.get('expires_in', 3600)  # Default 1hr expiry
        request.session['user'] = user_data

async def get_reddit_user_info(access_token: str):
    url = 'https://oauth.reddit.com/api/v1/me'

    headers = {"Authorization": "bearer " + access_token}

    # Extracting the user info and returning the relevant data 
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)
        data = response.json()
        name = data.get('name')
        inbox_count = data.get('inbox_count')
        total_karma = data.get('total_karma')

        return {
            "name": name,
            "inbox_count": inbox_count,
            "total_karma": total_karma
        }

async def fetch_new_posts(access_token: str, subreddit: str, limit: int, after :str = None):
    url = f'https://oauth.reddit.com/r/{subreddit}/new'
    headers = {
        "Authorization": f"bearer {access_token}"
    }
    params = {
        "limit": limit
    }

    if after:
        params["after"] = after

    # Calling the reddit endpoint with all given parameters 
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        return response.json()
    
def format_reddit_response(data):

    # Formatting the reddit post data
    posts_list = data.get('data').get('children')
    modified_list = [
        {
            "title": post["data"]["title"],
            "url": post["data"]["url"],
            "author": post["data"]["author"],
            "upvotes": post["data"]["ups"]
        }
        for post in posts_list
    ]   
    return modified_list