import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import openai

env_path = Path('.') / '.env' #set env path
load_dotenv(dotenv_path=env_path) #load env vars

app = Flask(__name__) #instantiate app

slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app) #configure event endpoint
client = slack.WebClient(token=os.environ['SLACK_TOKEN']) #slackwebclient auth
openai.api_key=os.environ['CHATGPT_KEY'] #chatgpt auth

BOT_ID = client.api_call("auth.test")['user_id'] #grab bot ID

def detect_key(message): #function to detect API keys
    prompt = "reply to this message with one word only. say yes if the following message appears to contain an API key, no if it does not contain an api key, or maybe it potentially contains an api key: " + message
    message = [
    {"role": "system", "content": prompt},
]

    response = openai.ChatCompletion.create( #generate detection response
        model="gpt-4", #highest success rate model
        messages=message,
        #max_tokens=1,
        #n=1,
        #top_p=0.8,
    )
    
    answer = response.choices[0].message.content #parse answer
    return(answer) #return answer

@slack_event_adapter.on('message') #invoke function upon message event
def message(payLoad):
    #relevant event details
    event = payLoad['event']
    channel = event['channel']
    user_id = event['user']
    text = event['text']
    ts = event['ts']

    detection = detect_key(text).lower() #run detection prompt

    if(BOT_ID!=user_id): #if message event is not from self
        if(detection == 'yes' or detection == "maybe"): #if message potentially contain API key
            client.chat_postMessage(channel=channel, text='Sharing secret keys in an insecure manner is strictly prohibited and against security policy.\n\nIf this message contains a secret key, please delete this message immediately.\n\nIf this detection was made in error, please disregard this message.\n\nCC:@OrgAdmin', thread_ts=ts)


if __name__ == "__main__":
    app.run(debug=True, port=8000)