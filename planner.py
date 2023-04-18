"""
planner.py uses the MakCorps API in addition to the chatGPT and google maps API
to plan a trip for the user. It will take in a starting location, a destination,
a time frame, and a budget. It will then return a place to stay as well as a 
list of places to visit in the area, with directions on how to get there from 
the hotel.
"""
import openai
import googlemaps
import os
from dotenv import load_dotenv

load_dotenv('.env')


class Planner:
    def __init__(self, openai_api_key: str, googlemaps_api_key: str,
                 markops_username: str, markops_password: str) -> None:
        self.openai = openai
        self.openai.api_key = openai_api_key
        self.googlemaps = googlemaps.Client(key=googlemaps_api_key)

        JWT = os.popen(
            "curl --request POST \
                --url 'https://api.makcorps.com/auth' \
                    --header 'Content-Type: application/json' \
                        --data '{ \"username\":\"" + str(markops_username) +
            "\", \"password\":\"" + str(markops_password) + "\" }'").read()

        print(JWT)
        print(JWT.split(":")[1][2:-4])
        self.JWTtoken = JWT.split(":")[1][2:-4]


# test code
openai_api_key = os.getenv('OPENAI_API_KEY')
googlemaps_api_key = os.getenv('GOOGLEMAPS_API_KEY')
markops_username = os.getenv('MARKOPS_USERNAME')
markops_password = os.getenv('MARKOPS_PASSWORD')

planner = Planner(openai_api_key, googlemaps_api_key, markops_username,
                  markops_password)
