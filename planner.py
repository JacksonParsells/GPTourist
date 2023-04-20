"""
planner.py uses the MakCorps API in addition to the chatGPT and google maps API
to plan a trip for the user. It will take in a starting location, a destination,
a time frame, and a budget. It will then return a place to stay as well as a
list of places to visit in the area, with directions on how to get there from
the hotel.

current limitations: the MakCorps API doesn't let us specify country :")
"""
import openai
import googlemaps
import os
from dotenv import load_dotenv
import json
import sys

load_dotenv('.env')


class Planner:
    def __init__(self, openai_api_key: str, googlemaps_api_key: str,
                 markops_username: str, markops_password: str) -> None:
        self.openai = openai
        self.openai.api_key = openai_api_key
        self.googlemaps = googlemaps.Client(key=googlemaps_api_key)

        # compute JWT token for MakCorps API in order to not store username and
        # password in plaintext
        JWT = os.popen(
            "curl --request POST \
                --url 'https://api.makcorps.com/auth' \
                    --header 'Content-Type: application/json' \
                        --data '{ \"username\":\"" + str(markops_username) +
            "\", \"password\":\"" + str(markops_password) + "\" }'").read()
        JWT_json = json.loads(JWT)
        self.JWTtoken = JWT_json["access_token"]

    def get_hotel(self, location: str, budget: str) -> str:
        """
        get_hotel takes in a location and a budget and returns the name of the
        hotel with the lowest price in the area, as well as the price of the
        hotel.
        """
        hotels = os.popen(
            "curl --request GET \
                --url https://api.makcorps.com/free/" + location + "\
                    --header 'Authorization: JWT " + self.JWTtoken + "'"
        ).read()

        hotels_json = json.loads(hotels)

        # find the hotel with the lowest price
        lowest_price = sys.maxsize
        lowest_price_hotel = None

        for hotel in hotels_json['Comparison']:
            if type(hotel) is list:
                for i, rate_json in enumerate(hotel[1]):
                    if rate_json['price' + str(i + 1)] and int(rate_json['price' + str(i + 1)]) < lowest_price:
                        lowest_price = int(rate_json['price' + str(i + 1)])
                        lowest_price_hotel = hotel[0]['hotelName']

        self.hotel_name = lowest_price_hotel
        self.hotel_price = lowest_price
        self.hotel_city = location

        if lowest_price < int(budget):
            return lowest_price_hotel + " costs $" + str(lowest_price)
        else:
            return "Sorry, there are no available hotels in your budget."

    def generate_trip(self, time_frame: str) -> str:
        """
        generate_trip asks chatGPT to generate 3 activities per day
        for the time frame specified by the user. It then returns directions
        from the hotel to each of the activities.
        """
        # ask chatGPT to generate a trip and put it in a newline separated list
        ans = self.openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "I want to go to " + self.hotel_city + " for " + time_frame +
                    " days. I need two activities per day. Please generate 2 activities per day and format the output so that each activity is on it's own line with 'day [day number], activity [activity number]: [activity]"}
            ]
        )

        # get the response from chatGPT
        activities = ans.choices[0].message.content.split("\n")

        # get directions from hotel to each activity
        directions = []
        hotel_geocode = self.googlemaps.geocode(
            self.hotel_name + " " + self.hotel_city)
        for activity in activities:
            if activity == "":
                continue
            geocode = self.googlemaps.geocode(
                activity.split(": ")[1] + " " + self.hotel_city)
            directions.append(self.googlemaps.directions(
                hotel_geocode[0]['geometry']['location'],
                geocode[0]['geometry']['location'],
                mode="walking"
            )[0]['legs'][0]['steps'])

        # format directions into a string
        directions_str = ""
        for i, day in enumerate(directions):
            directions_str += "Day " + str(i + 1) + ":\n"
            for j, activity in enumerate(day):
                directions_str += "Activity " + \
                    str(j + 1) + ": " + activity['html_instructions'] + "\n"
            directions_str += "\n"

        return directions_str


# test code
openai_api_key = os.getenv('OPENAI_API_KEY')
googlemaps_api_key = os.getenv('GOOGLEMAPS_API_KEY')
markops_username = os.getenv('MARKOPS_USERNAME')
markops_password = os.getenv('MARKOPS_PASSWORD')

planner = Planner(openai_api_key, googlemaps_api_key, markops_username,
                  markops_password)
planner.get_hotel("Islamabad", "100")
print(planner.generate_trip("3"))
