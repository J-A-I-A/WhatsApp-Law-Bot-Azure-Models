import os
import time
import azure.functions as func
import logging
from urllib.parse import parse_qs
import messages
import bot
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()
sid = os.getenv("TWILIO_SID")
token=os.getenv("TWILIO_TOKEN")
messaging_service_sid=os.getenv("TWILIO_MESSAGING_SERVICE_SID")


sender= Client(sid, token)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="Twilio_Webhook")
async def Twilio_Webhook(req: func.HttpRequest) -> func.HttpResponse:
    response=None
    logging.info('Python HTTP trigger function processed a request.')
    request = req.get_body().decode('utf-8')
    decoded = parse_qs(request)
    data={}
    for key, value in decoded.items():
        data[f"{key}"]=value[0]

    if data["AccountSid"]!=sid:
        return func.HttpResponse(
             #"This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             body="Unauthorized Request",
             status_code=401
        )
    if data["MessageType"]!="text":
        return func.HttpResponse(
             #Returns a Message is user sent a non-text message,
             body="I currently only understand text messages please only send text messages",
             status_code=200
        )
    question=str(data["Body"])
    phone_number=str(data["From"].split(":",1)[1])

    past_conversations=messages.get_messages(phone_number)
    response=bot.Law_bot(previous_message=past_conversations,question=question)
    logging.info(f'Question has been sent to the bot: {question}.')
    messages.add_messages(phone_number=phone_number,question=question,response=response)
    logging.info(f'Response has been returned from the bot:{response}.')

    recieved=False
    if response!=None:
        message_list=split_message(response)
        # Sends the response to the user.
        for m in message_list:
            time.sleep(3)
            status=sender.messages.create(
                from_=data["To"],
                body=m,
                to=data["From"],   
                messaging_service_sid=messaging_service_sid
            )
            message_sid=status.sid
            logging.info(f'Message sent to the user: {m}.')
            recieved=False
            while recieved==False:
                message_status= sender.messages(f"{message_sid}").fetch()
                if message_status.status=="sent":
                    recieved=True
                    break
        return func.HttpResponse(status_code=200)
    else:
        return func.HttpResponse(
             #This HTTP triggered function executed successfully. But no response for the Bot.
             body="Currently Offline Please Try Again Later",
             status_code=200
        )
    



def split_message(text: str, max_length=1600) -> list:
    # Split the text by newlines first to work with individual chunks
    lines = text.split('\n')
    subsets = []
    current_subset = ""

    for line in lines:
        # If adding the line exceeds the max_length, store the current subset
        if len(current_subset) + len(line) + 1 > max_length:  # +1 for newline char
            subsets.append(current_subset)
            current_subset = "\n"+line   # Start a new subset
        else:
            # Otherwise, keep adding lines to the current subset
            current_subset += "\n"+line 

    # Don't forget to add the last subset
    if current_subset:
        subsets.append(current_subset)
    return subsets