import datetime
import os
import time
from pinecone import Pinecone
from azure.ai.inference.models import AssistantMessage,UserMessage
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("PINECONE_API_KEY")
    
# Connect to Pinecone
database = Pinecone(api_key=api_key)
index_messages = database.Index("multilingual-e5-large")

def get_messages(phone_number: str) -> list:
    id_generator = index_messages.list(prefix=phone_number, namespace='messages')
    id_list = [item for sublist in id_generator for item in sublist]
    
    previous_context = []
    if id_list:
        # Fetch messages from Pinecone
        fetched_messages = index_messages.fetch(ids=id_list, namespace='messages')
        if fetched_messages and 'vectors' in fetched_messages:
            # Sort the fetched messages by timestamp in descending order (newest first)
            recent_messages = sorted(
                fetched_messages['vectors'].items(),
                key=lambda x: float(x[1]['metadata']['timestamp']) if isinstance(x[1]['metadata']['timestamp'], (int, float)) else time.mktime(datetime.strptime(x[1]['metadata']['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ").timetuple()),
                reverse=True
            )
            # Extract and collate previous questions and responses with clear separators
            for message in recent_messages:
                previous_context.append(UserMessage(content=message[1]['metadata']['question']))
                previous_context.append(AssistantMessage(content=message[1]['metadata']['response']))

    return previous_context



def add_messages(phone_number: str, question: str, response: str) -> None:
    current_timestamp = time.time()

    embeddings = database.inference.embed(
        "multilingual-e5-large",
        inputs=phone_number,
        parameters={"input_type": "query"},
    )

    vector_id = f"{phone_number}_{int(current_timestamp)}"

    index_messages.upsert(
        vectors=[{
            "id": vector_id,
            "values": embeddings[0]['values'],
            "metadata": {
                "phone_number": phone_number,
                "question": question,
                "response": response,
                "timestamp": current_timestamp
            }
        }],
        namespace="messages"
    )