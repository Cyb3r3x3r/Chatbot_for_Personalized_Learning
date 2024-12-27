# Personalized Learning Chatbot

A conversational AI chatbot with a UI using Streamlit and built using Rasa that provides personalized recommendations for learning resources, including videos, books, and courses. Additionally, the chatbot leverages a Hugging Face GPT-2 model to generate detailed explanations for various topics.

## Features

- **Personalized Recommendations**: Suggests videos, books, and courses based on user preferences and topics of interest.
- **Dynamic Explanations**: Uses Hugging Face's GPT-2 model to provide concise and accurate explanations for user-asked topics.

## Requirements

- Python 3.7 or later
- Rasa Open Source
- Hugging Face Transformers library

## Installation

1. **Clone the Repository**
   ```cmd
   git clone https://github.com/your-username/personalized-learning-chatbot.git
   cd personalized-learning-chatbot

2. **Install dependencies**
   ```cmd
   pip install -r requirements.txt

3. **Train the Model**
   ```
   rasa train
   ```
Trained models are saved in models folder.

## Running the bot
Start the Rasa action server
```
rasa run actions
```
Start the rasa shell
```
rasa shell
```
