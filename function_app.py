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
    

def split_message(text: str):
    limit = 1600
    messages = []
    new_line_indexes = find_new_lines_indexes(text)
    start = 0
    end, new_line_index = find_closest_less_or_equal(new_line_indexes, limit)
    messages.append(text[start:end])
    while (end != None and new_line_index != None and new_line_index < len(new_line_indexes) - 1):
        start = end
        end, new_line_index = find_closest_less_or_equal(new_line_indexes, limit + start)
        messages.append(text[start:end])

    return messages
    
def find_new_lines_indexes(text: str):
    return [i for i, ltr in enumerate(text) if ltr == "\n"]

def find_closest_less_or_equal(numbers, target):
    # Filter the list to only include numbers less than or equal to the target
    less_or_equal_numbers = [(num, idx) for idx, num in enumerate(numbers) if num <= target]
    
    # If the filtered list is not empty, return the closest number and its index
    if less_or_equal_numbers:
        closest_num, closest_idx = max(less_or_equal_numbers, key=lambda x: x[0])
        return closest_num, closest_idx
    else:
        return None, None  # Return None for both if no such number exists