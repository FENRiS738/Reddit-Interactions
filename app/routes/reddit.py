# Built Ins
import os
from urllib.parse import urlencode
import time

# Installeds
from fastapi import APIRouter, responses, status, Request, Depends, HTTPException
from dotenv import load_dotenv

# Custom Builts
from ..helpers.reddit import get_reddit_access_token, get_reddit_user_info, validate_reddit_token, fetch_new_posts, format_reddit_response

routes = APIRouter(prefix="/reddit", tags=["Reddit APIs"])

# Loading environment variables
load_dotenv()
CLIENT_ID=os.getenv("ID")
CLIENT_SECRET=os.getenv("SECRET")
REDIRECT_URI=os.getenv("REDIRECT_URI")
REDDIT_APP_SECRET=os.getenv("REDDIT_APP_SECRET")

# Reddit Authentication starting step
@routes.get('/auth')
async def auth():
    try: 
        # Checking for any missing required parameters
        if not CLIENT_ID or not REDDIT_APP_SECRET or not REDIRECT_URI:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Credentials are missing or invalid.")        

        params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "state": REDDIT_APP_SECRET,
            "redirect_uri": REDIRECT_URI,
            "duration": "permanent",
            "scope": "identity,read"
        }
        
        # Redirecting to the authorization url
        url = "https://www.reddit.com/api/v1/authorize?" + urlencode(params)
        return responses.RedirectResponse(url)

    except Exception as ex:
        return responses.JSONResponse({
            "message": "Something went wrong!"
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@routes.get('/auth/callback')
async def token(request: Request):
    try: 

        # Checking if use denied account access to app
        if dict(request.query_params)['error'].__contains__('access_denied'):
            raise HTTPException(status_code=status.HTTP_200_OK, detail="You chose not to grant permissions")        
    
        code = dict(request.query_params)['code']

        # Checking if valid code is return or not
        if not code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code or code not found.")
        
        # Generating access token and saving use session
        response = await get_reddit_access_token(code)
        
        request.session['user'] = {
            "access_token": response['access_token'],
            "refresh_token": response['refresh_token'],
            "expires_at": time.time() + response.get('expires_in', 86400)
        }
        return responses.JSONResponse(
            {
                "message": "You are logged in successfully.",
                "status": status.HTTP_201_CREATED
            },
            status_code=status.HTTP_201_CREATED
        )

    except Exception as ex:
        return responses.JSONResponse({
            "message": "Something went wrong!"
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@routes.get('/me', dependencies=[Depends(validate_reddit_token)])
async def user(request: Request):
    try: 
        access_token = request.session.get('user')['access_token']
        
        # Extracting the user info to validate if access token is proprely working or not
        response = await get_reddit_user_info(access_token)
        return responses.JSONResponse(
            {
                "data": response,
                "status": status.HTTP_200_OK
            },
            status_code=status.HTTP_200_OK
        )
    
    except Exception as ex:
        return responses.JSONResponse({
            "message": "Something went wrong!"
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@routes.get('/fetch', dependencies=[Depends(validate_reddit_token)])
async def get_subreddit_latest_posts(request: Request, subreddit: str, limit: int = 5, after :str = None):
    try:
        access_token = request.session.get('user')['access_token']
        
        # Fetching latest post data, if there is no limit the default to 5 posts
        response = await fetch_new_posts(access_token, subreddit, limit, after)
        
        # Formatting the response to extract relevant information out of fetched data
        formatted_response = format_reddit_response(response)
        return responses.JSONResponse(
            {
                "data": formatted_response,
                "status": status.HTTP_200_OK
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as ex:
        return responses.JSONResponse({
            "message": "Something went wrong!"
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)