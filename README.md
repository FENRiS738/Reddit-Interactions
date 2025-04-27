# Reddit Interactions App

- ## How to setup this application
    1. ### Clone repository
        Clone repository from [here](https://github.com/FENRiS738/Reddit-Interactions). 
    2. ### Create development enviornment
        Create a development environment using the command  
        `python -m venv <environment_name>`
    3. ### Start environment
        Start development environment using the command  
        `source <environment_name>\Scripts\activate`
    4. ### Install dependencies
        Install dependencies into development environment using the command  
        `pip install -r requirements.txt`
- ## How to setup reddit app for the application
    1. ### Create custom app
        Create an app on developer platform of reddit from [here](https://www.reddit.com/prefs/apps). 
    2. ### Get credentials
        Fill the required information and generate app_id and secret to use.
    3. ### Save in environment file
        Create a .env file into your application location and store add values like:  
        `ID=<App ID>`  
        `SECRET=<App Secret>`  
        `REDIRECT_URI=<Redirect Uri>`  
        `REDDIT_APP_SECRET=<Random State>`  
        `SESSION_SECRET=<App Secret Key>`
- ## How to run this 
    1. ### Start server
        After configuring all necessary things start the server using command  
        `uvicorn app:app`


---
> ## Refrences: 
> Reddit auth process from [here](https://github.com/reddit-archive/reddit/wiki/OAuth2).  
>  Reddit api documentation [here](https://www.reddit.com/dev/api).  
> Reddit developer portal [here](https://www.reddit.com/prefs/apps)

    
