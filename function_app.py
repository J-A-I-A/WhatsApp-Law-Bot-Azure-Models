import os
import azure.functions as func
import logging
from urllib.parse import parse_qs
import messages
from relevant_info import relevant_info
import bot
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()
sid = os.getenv("TWILIO_SID")
token=os.getenv("TWILIO_TOKEN")

sender= Client(sid, token)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="Twilio_Webhook")
def Twilio_Webhook(req: func.HttpRequest) -> func.HttpResponse:
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
             #"This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             body="I currently only understand text messages please only send text messages",
             status_code=200
        )
    question=str(data["Body"])
    phone_number=str(data["From"].split(":",1)[1])

    past_conversations=messages.get_messages(phone_number)
    knowledge=relevant_info(question)
    response=bot.Law_bot(relevant_laws=knowledge,
    previous_message=past_conversations,question=question)
    messages.add_messages(phone_number=phone_number,question=question,response=response)
    logging.info('Request has been sent to the bot.')
    if response:
        if len(response)>1600:
            res_first = response[0:len(response)//2] 
            res_second = response[len(response)//2 if len(response)%2 == 0 else ((len(response)//2)+1):]
            sender.messages.create(
                from_=data["To"],
                body=res_first,
                to=data["From"]
            )
            sender.messages.create(
                from_=data["To"],
                body=res_second,
                to=data["From"]
            )
        else:
            sender.messages.create(
            from_=data["To"],
            body=response,
            to=data["From"]
            )
            return func.HttpResponse(status_code=200)
    else:
        return func.HttpResponse(
             #"This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             body="Currently Offline Please Try Again Later",
             status_code=200
        )