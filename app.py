import streamlit as st
import requests
import time

# Initialize session state variables for storing chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to send user message to the Rasa server and get a response
def get_bot_response(user_input):
    try:
        rasa_url = "http://localhost:5005/webhooks/rest/webhook"
        headers = {"Content-Type": "application/json"}
        data = {"sender": "user", "message": user_input}

        response = requests.post(rasa_url, json=data, headers=headers)
        if response.status_code == 200:
            bot_responses = response.json()
            if bot_responses:
                # Concatenate all bot responses
                bot_reply = "<br>".join([resp.get("text", "") for resp in bot_responses])
                return bot_reply if bot_reply else "No response"
            else:
                return "No response from the bot."
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# UI
st.title("Ask the bot")
st.write("Interact with the chatbot to get recommendations or ask for explanations.")

# Sidebar
st.sidebar.title("Personalized Chatbot for Learning")
sidebox = st.sidebar
sidebox.write("You can ask the bot to:")
sidebox.write("\n")
sidebox.write("- Give me resources on blockchain")
sidebox.write("- Suggest me some books on Java")
sidebox.write("- Give me some videos on IoT")

# Input field for user message
user_input = st.text_input("Type your message:")

# Send button to submit the user input
if st.button("Send"):
    if user_input.strip():
        with st.spinner('Waiting for response...'):
            # Get bot response
            bot_response = get_bot_response(user_input)
            
            # Append user input and bot response to chat history
            st.session_state.chat_history.append(f'<p style="color:white;background-color:#2a2a2a;"><b>🧑‍💻 You:</b> {user_input}</p>')
            st.session_state.chat_history.append(f'<p style="color:white;background-color:#2a2a2a;"><b>🤖 Bot:</b> {bot_response}</p>')
    else:
        st.warning("Please enter a message.")

# Display the entire chat history
chat_display = "".join(st.session_state.chat_history)
st.markdown(chat_display, unsafe_allow_html=True)
