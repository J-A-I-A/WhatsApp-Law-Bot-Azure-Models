---

# WhatsApp Law Bot (Azure Models)

This repository contains the code and resources for a WhatsApp Law Bot that utilizes Azure Models. The bot is designed to assist users with legal inquiries and information through WhatsApp. By leveraging Azure's AI capabilities, this bot can provide relevant legal guidance based on user input.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The WhatsApp Law Bot is a conversational agent built on Azure's AI models, designed to provide basic legal assistance to users via WhatsApp. It can answer general legal questions and guide users to the relevant legal information they seek.

## Features

- **Legal Assistance**: Provides legal information based on predefined knowledge.
- **Natural Language Understanding**: Leverages Azure's NLP models for understanding user queries.
- **WhatsApp Integration**: Communicates with users via WhatsApp through an API.
- **Azure Cognitive Services**: Uses various Azure models and services for text analysis and processing.

## Architecture

1. **User Interaction**: Users interact with the bot via WhatsApp.
2. **Message Processing**: Messages are routed through an API that connects to Azure's AI services.
3. **Natural Language Understanding**: Azure's NLP models process the queries and determine the relevant response.
4. **Response Delivery**: The bot sends back an appropriate legal response or directs the user to further resources.

## Technologies

- **Azure Cognitive Services**: AI models for natural language processing and analysis.
- **Azure Bot Service**: For managing the chatbot functionalities.
- **Twilio API**: For WhatsApp messaging.
- **Python Flask**: Backend service for routing and processing.

## Prerequisites

Before you begin, ensure you have the following:

- Azure Functions Extension installed on your machine
- Ngrok Tunneling Service install on your machine.
- An Azure account with access to Cognitive Services and Bot Service
- A Twilio account for WhatsApp API integration
- WhatsApp Business API setup
- `git` installed for cloning the repository

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/J-A-I-A/WhatsApp-Law-Bot-Azure-Models.git
   cd WhatsApp-Law-Bot-Azure-Models
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Set up environment variables:**

   Create a `.env` file in the root of the project and add the following:

   ```env
   AZURE_API_KEY=your_azure_api_key
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   WHATSAPP_NUMBER=your_whatsapp_number
   ```

4. **Start the application:**

   ```bash
   flask --app hello run
   ```

## Usage

This implementation can be used with any knowledge base thats is stored on pinecone, to change to bot to respond to the relevant information stored in a pinecone vector store the system prompt will need to be changed.

To test the bot:

1. Open WhatsApp.
2. Send a message to the bot's WhatsApp number.
3. The bot will analyze your message and provide a response.

## Contributing

We welcome contributions! If you would like to improve this project, feel free to submit a pull request or open an issue.

### Steps to Contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to adjust the sections and instructions as needed!
