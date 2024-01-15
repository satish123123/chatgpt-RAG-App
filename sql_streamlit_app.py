# Import required libraries
import os
from dotenv import load_dotenv
from itertools import zip_longest

import streamlit as st
from streamlit_chat import message

#from langchain.chat_models import ChatOpenAI
from langchain_openai import AzureChatOpenAI

# SQL stuff
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy.engine.url import URL


from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

# Load environment variables
load_dotenv()

#SQL stuff
db_config = {
                'drivername': 'mssql+pyodbc',
                'username': os.environ["SQL_SERVER_USERNAME"] +'@'+ os.environ["SQL_SERVER_NAME"],
                'password': os.environ["SQL_SERVER_PASSWORD"],
                'host': os.environ["SQL_SERVER_NAME"],
                'port': 1433,
                'database': os.environ["SQL_SERVER_DATABASE"],
                'query': {'driver': 'ODBC Driver 17 for SQL Server'}
            }

#SQL stuff Create a URL object for connecting to the database
db_url = URL.create(**db_config)
db = SQLDatabase.from_uri(db_url)

# Set streamlit page configuration
st.set_page_config(page_title="Dream 11 Chatbot")
st.title("Dream 11 Chatbot")

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

# SQL stuff 
toolkit = SQLDatabaseToolkit(db=db, llm=chat)

agent_executor = create_sql_agent(
    # prefix=MSSQL_AGENT_PREFIX,
    # format_instructions = MSSQL_AGENT_FORMAT_INSTRUCTIONS,
    llm=chat,
    toolkit=toolkit,
    top_k=30,
    verbose=True
)

def build_message_list():
    """
    Build a list of messages including system, human and AI messages.
    """
    # Start zipped_messages with the SystemMessage
    zipped_messages = [SystemMessage(
        #content="You are a helpful AI assistant talking with a human. If you do not know an answer, just say 'I don't know', do not make up an answer.")]
        # SQL stuff
        content="""You are a helpful AI assistant talking with a human. If there are any questions not related to cricket, you may look up the in your knowledge base. 
        If there are any questions on cricket, you will need to find the answer in the SQL Server database.
        """
        
        )]

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
    #ai_response = chat(zipped_messages)
    # SQL stuff
    ai_response = agent_executor.run(zipped_messages)
    print("*****Response aalaa re*****")
    print(ai_response)
    return ai_response


# Define function to submit user input
def submit():
    # Set entered_prompt to the current value of prompt_input
    st.session_state.entered_prompt = st.session_state.prompt_input
    # Clear prompt_input
    st.session_state.prompt_input = ""


if st.session_state.entered_prompt != "":
    # Get user query
    user_query = st.session_state.entered_prompt

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


