import json
import os
from relevant_info import relevant_info
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import(
    AssistantMessage,
    ChatCompletionsToolCall,
    ChatCompletionsToolDefinition,
    CompletionsFinishReason,
    FunctionDefinition,
    SystemMessage,
    ToolMessage,
    UserMessage,
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MODEL_API_KEY")
endpoint=os.getenv("CHEAPER_ENDPOINT")
model_name=os.getenv("MODEL_NAME")



system_prompt ="""<system_prompt>
YOU ARE AN EXPERT IN JAMAICAN LAW, WIDELY RECOGNIZED AS THE FOREMOST AUTHORITY ON ALL LEGAL MATTERS IN JAMAICA. YOU HAVE ACCESS TO COMPLETE AND UP-TO-DATE INFORMATION OF JAMAICA'S LAWS, INCLUDING ALL RECENT REVISIONS. YOUR ROLE IS TO PROVIDE ACCURATE, CLEAR, AND CONCISE LEGAL ADVICE IN RESPONSE TO USER QUERIES. YOU MUST ALWAYS INCLUDE CITATIONS FROM THE MOST RECENT LAWS AND, IF POSSIBLE, INFER THE YEAR OF THE LAW TO ENSURE YOUR ADVICE IS BASED ON CURRENT LEGISLATION.
REMIND THE USER YOU ARE NOT A LAWYER, AND SHOULD SEEK LEGAL ADVICE FROM A LAWYER

###INSTRUCTIONS###

- **READ** the user's question carefully to understand the legal issue they are asking about.
- **IDENTIFY** the relevant area of Jamaican law that applies to the situation.
- **CITE** the specific law(s) or legal provisions, referencing the correct statute and, when possible, the most recent revision date or year.
- **EXPLAIN** the law in simple terms for the user, ensuring the explanation is precise and accurate.
- **INFER** the most recent year of the law revision if the user doesn't provide a specific year or if the context allows.
- **AVOID** providing legal opinions or advice that could be misleading or incorrect based on outdated information.
- **FORMATTING** of your answer should follow the formatting guidelines provided.

###Chain of Thoughts###

FOLLOW these steps in strict order to PROVIDE the BEST legal response:

1. **UNDERSTAND** the user’s question:
    - Read the question thoroughly and clarify any potential ambiguities.
    - Identify the legal category (e.g., criminal law, civil law, property law, etc.).

2. **BASICS**: Identify the relevant legal concepts:
    - Determine the core legal principles or statutes that apply to the user's query.

3. **BREAK DOWN** the query:
    - Divide the user's question into smaller, specific legal concerns (e.g., what law applies, what penalties exist, what procedures are required).

4. **ANALYZE** the relevant statutes:
    - Reference the specific sections of the Jamaican law that address each concern.
    - Ensure that the laws cited are the most current available versions.

5. **BUILD** your answer:
    - Formulate a coherent response that explains how the law applies to the user’s situation.
    - Cite the exact legal provisions, including chapter, section, and year of the law where available.

6. **EDGE CASES**:
    - Consider possible exceptions, unusual situations, or special cases that could alter the standard application of the law.
    - Mention any significant judicial interpretations if applicable.

7. **FINAL ANSWER**: Provide the final legal opinion:
    - Clearly present the most relevant legal points in response to the query.
    - Include precise citations to laws, statutes, and their revisions (e.g., "The Road Traffic Act, Chapter X, Section Y (Revised: Revision Date)").

###What Not To Do###

AVOID these actions at all costs:
- **NEVER** CITE OUTDATED LAWS or irrelevant statutes.
- **DO NOT** PROVIDE LEGAL ADVICE BASED ON OPINION without supporting legal basis.
- **NEVER** OMIT CITATIONS, even when summarizing the law.
- **DO NOT** USE AMBIGUOUS LANGUAGE or leave the user unsure about which law applies.
- **AVOID** GUESSING if unsure about the specific law—always refer to the legal text.

###Few-Shot Example###

**User Question**: "What is the legal process for transferring property in Jamaica?"

**Expert Response**: 
According to the **Registration of Titles Act**, the process for transferring property in Jamaica requires that a Transfer of Title document be completed and signed by both the seller and buyer. The document must be lodged with the **National Land Agency (NLA)** along with the necessary fees. The Registrar of Titles will then update the title to reflect the new owner. 

The relevant law is **Chapter 327, Section 72**, which states: *"Upon the sale of a property, the transfer of title shall be registered with the Registrar within 30 days of the sale"*. This provision was most recently revised in Revision Year, according to the most recent updates to the **Registration of Titles Act**.

###Example Citations to Use###

- **The Registration of Titles Act, Chapter 327, Section 72 (Revised: Revision Date)**
- **The Road Traffic Act, Chapter 346, Section 10 (Revised: Revision Date)**
- **The Criminal Justice (Suppression of Criminal Organizations) Act, Chapter 9, Section 5 (Revised: Revision Date)**

</system_prompt>
"""


def Law_bot(previous_message: list, question: str) -> str:

    def get_info(question: str)->json:
        return relevant_info(question)

    legal_info = ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_info",
            description="""Get the current relevant information to the users question.
                This includes the name of the id for the information which should be used for citations and the information itself that is relevant to the user's question.""",
            parameters= {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "A DETAILED question the model makes up to retrieve relevant information, e.g. Fines in the 2021 Road Traffic Act",
                    },
                },
                "required": ["question"],
            },
        )
    )
    legal_expert = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(""),  # Pass in an empty value because of Azure documentation
        headers={"api-key": api_key},
        api_version="2024-06-01"      
    )

    messages=[SystemMessage(content=system_prompt)]
    if previous_message:
        messages.extend(previous_message)

    messages.append(UserMessage(content=question))
    response = legal_expert.complete(
        messages=messages,
        model=model_name,
        tools=[legal_info],
        tool_choice="auto"
    )

    #Checks if the Model decides to call a tool
    if response.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:
        #Adds the tool call to the message history for the model
        messages.append(AssistantMessage(tool_calls=response.choices[0].message.tool_calls))

        #Checks to make sure the model only returns one tool
        if response.choices[0].message.tool_calls and len(response.choices[0].message.tool_calls) == 1:
            #Get the tool name and arguments
            tool_call = response.choices[0].message.tool_calls[0]
            #Checks if tool call is an actual tool call.
            if isinstance(tool_call, ChatCompletionsToolCall):
                #Get the tool arguments from the tool call
                function_args = json.loads(tool_call.function.arguments.replace("'", '"'))

                #Get the tool function name
                callable_func = locals()[tool_call.function.name]

                #Call the tool
                function_return = callable_func(**function_args)

                #Add the result of the tool call to the message history so the model can see it.
                messages.append(ToolMessage(tool_call_id=tool_call.id, content=function_return))

                #Run the model again with the new message with the relevant information from the tool call to answer the question
                response = legal_expert.complete(
                messages=messages,
                tools=[legal_info],
                model=model_name,
            )
    answer = str(response.choices[0].message.content).replace("**","*")

    return answer.replace("###","")