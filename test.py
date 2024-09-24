import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import AssistantMessage, SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential


token = "b4cc5e0893f24f1f97067e75a1b0d763"
githubtoken="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"
endpoint = "https://law-bot-openai812410961668.openai.azure.com/openai/deployments/Legal-Expert-OpenAi-4o"
model_name = "Legal-Expert-OpenAi-4o"


client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(""),  # Pass in an empty value.
    headers={"api-key": token},
    api_version="2024-06-01"
)

messages = [
    SystemMessage(content="You are a helpful assistant."),
    UserMessage(content="What is the capital of France?"),
    AssistantMessage(content="The capital of France is Paris."),
    UserMessage(content="What about Spain?"),
]

response = client.complete(messages=messages,model=model_name)

print(response.choices[0].message.content)


def Law_bot(message: list, question: str) -> str:
    return "Currently Offline Please Try Again Later"
