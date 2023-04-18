# Wrapper for twilio
from twilio.rest import Client
import os
from dotenv import load_dotenv


load_dotenv('.env')

# variables and tokens
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(account_sid, auth_token)

# simple message to text
message = client.messages.create(
    to="+6176535618",
    from_="",
    body="Hello world")

print(message.sid)

# ask question
# get info from client
# go through chatgpi API
# respond.
