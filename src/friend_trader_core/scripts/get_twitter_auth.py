import sys
import requests
from requests_oauthlib import OAuth1Session
from decouple import config

#Prompt developer to enter App credentials
print("Enter the credentials for your developer App below.")
CONSUMER_KEY = config("TWITTER_CONSUMER_KEY_1")
CONSUMER_SECRET = config("TWITTER_CONSUMER_SECRET_1")
ACCESS_TOKEN = config("TWITTER_ACCESS_TOKEN_1")
TOKEN_SECRET = config("TWITTER_ACCESS_TOKEN_SECRET_1")

# Request an OAuth Request Token. This is the first step of the 3-legged OAuth flow. This generates a token that you can use to request user authorization for access.
def request_token():

    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri='oob')

    url = "https://api.twitter.com/oauth/request_token"

    try:
        response = oauth.fetch_request_token(url)
        resource_owner_oauth_token = response.get('oauth_token')
        resource_owner_oauth_token_secret = response.get('oauth_token_secret')
    except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(120)
    
    return resource_owner_oauth_token, resource_owner_oauth_token_secret

# Use the OAuth Request Token received in the previous step to redirect the user to authorize your developer App for access.
def get_user_authorization(resource_owner_oauth_token):

    authorization_url = f"https://api.twitter.com/oauth/authorize?oauth_token={resource_owner_oauth_token}"
    authorization_pin = input(f" \n Send the following URL to the user you want to generate access tokens for. \n → {authorization_url} \n This URL will allow the user to authorize your application and generate a PIN. \n Paste PIN here: ")

    return(authorization_pin)

# Exchange the OAuth Request Token you obtained previously for the user’s Access Tokens.
def get_user_access_tokens(resource_owner_oauth_token, resource_owner_oauth_token_secret, authorization_pin):

    oauth = OAuth1Session(CONSUMER_KEY, 
                            client_secret=CONSUMER_SECRET, 
                            resource_owner_key=resource_owner_oauth_token, 
                            resource_owner_secret=resource_owner_oauth_token_secret, 
                            verifier=authorization_pin)
    
    url = "https://api.twitter.com/oauth/access_token"

    try: 
        response = oauth.fetch_access_token(url)
        access_token = response['oauth_token']
        access_token_secret = response['oauth_token_secret']
        user_id = response['user_id']
        screen_name = response['screen_name']
    except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(120)

    return(access_token, access_token_secret, user_id, screen_name)

if __name__ == '__main__':
    resource_owner_oauth_token, resource_owner_oauth_token_secret = request_token()
    authorization_pin = get_user_authorization(resource_owner_oauth_token)
    access_token, access_token_secret, user_id, screen_name = get_user_access_tokens(resource_owner_oauth_token, resource_owner_oauth_token_secret, authorization_pin)
    print(f"\n User @handle: {screen_name}", f"\n User ID: {user_id}", f"\n User access token: {access_token}", f" \n User access token secret: {access_token_secret} \n")
    