# Import required libraries
import os
from dotenv import load_dotenv
from itertools import zip_longest
import streamlit as st
from streamlit_chat import message
from langchain_openai import AzureChatOpenAI

from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

from rag_query_helper import similarity_search

# Load environment variables
load_dotenv()

# Set streamlit page configuration
st.set_page_config(page_title="Osama AI + Langchain - RAG")
st.title("Osama AI App + Langchain - RAG")

# Initialize session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []  # Store AI generated responses

if 'past' not in st.session_state:
    st.session_state['past'] = []  # Store past user inputs

if 'entered_prompt' not in st.session_state:
    st.session_state['entered_prompt'] = ""  # Store the latest user input

# Initialize the ChatOpenAI model
chat = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT"),
    verbose=True
)

information = ""

def build_message_list():
    """
    Build a list of messages including system, human and AI messages.
    """
    # Start zipped_messages with the SystemMessage
    zipped_messages = [SystemMessage(
        content= f"""You are a helpful AI assistant talking with a human. You are suppossed to derive an answer from the contextual information sent to you.
                   The contextual information for you in this case is {information}""")]

    # Zip together the past and generated messages
    for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
        if human_msg is not None:
            zipped_messages.append(HumanMessage(
                content=human_msg))  # Add user messages
        if ai_msg is not None:
            zipped_messages.append(
                AIMessage(content=ai_msg))  # Add AI messages

    return zipped_messages


def generate_response():
    """
    Generate AI response using the ChatOpenAI model.
    """
    # Build the list of messages
    zipped_messages = build_message_list()

    # Generate response using the chat model
    ai_response = chat(zipped_messages)
    return ai_response.content


# Define function to submit user input
def submit():
    # Set entered_prompt to the current value of prompt_input
    st.session_state.entered_prompt = st.session_state.prompt_input
    # Clear prompt_input
    st.session_state.prompt_input = ""


if st.session_state.entered_prompt != "":
    # Get user query
    user_query = st.session_state.entered_prompt
    
    docs = similarity_search(user_query)

    # Concatenate the page_content of each document
    information = "".join(doc.page_content for doc in docs)

    print(information)

    # Append user query to past queries
    st.session_state.past.append(user_query)

    # Generate response
    output = generate_response()

    # Append AI response to generated responses
    st.session_state.generated.append(output)

# Display the chat history
if st.session_state['generated']:
#    for i in range(len(st.session_state['generated'])-1, -1, -1):
    for i in range(len(st.session_state['generated'])):
        # Display user message
        message(st.session_state['past'][i],
                is_user=True, key=str(i) + '_user')
        # Display AI response
        message(st.session_state["generated"][i], key=str(i))
        
# Create a text input for user
st.text_input('YOU: ', key='prompt_input', on_change=submit)


