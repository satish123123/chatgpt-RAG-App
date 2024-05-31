# Import required libraries
import os
import re
from dotenv import load_dotenv

import streamlit as st
from streamlit_chat import message

from langchain_openai import AzureChatOpenAI
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor

from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)

from langchain.memory import ConversationBufferMemory

from .tools.sql import run_sql_query_tool, describe_table_tool, fetch_tables

# Load environment variables
load_dotenv()

if 'tables' not in st.session_state:
    tables = fetch_tables()
    st.session_state['tables'] = tables
else:
    tables = st.session_state['tables']

# Set streamlit page configuration
# st.set_page_config(page_title="Dream 11 Chatbot")
# st.title("Dream 11 Chatbot - FunctionCalling")
st.set_page_config(page_title="Travelbot")
st.title("Travelbot")

# Initialize session state variables
if 'entered_prompt' not in st.session_state:
    st.session_state['entered_prompt'] = ""  # Store the latest user input

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []  # Store the chat history st.session_state['memory_object']

if 'memory_object' not in st.session_state:
    st.session_state['memory_object'] = []  # Store the memory object

# Initialize the ChatOpenAI model
chat = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT"),
    verbose=True
)

prompt = ChatPromptTemplate(
    messages=[
        SystemMessage(content=(
            "You are an AI that has access to a SQL Server database. Generate T-SQL statements to be executed on Microsoft SQL Server.\n"
 #           "Whenever there is any question related to cricket, please refer to the SQL Server database only. Strictly do not refer to your knowledge base.\n"
 #           "Fuzzy lookup the player name, try to identify abbreviations used for player names, try to identify the stadium names (venue names) if city is provided.\n"
 #           "When evaluating performance of a batter or a bowler, please consider the maximum.\n"
            "Whenever there is any question related to travel or vacation, please refer to the SQL Server database only. Strictly do not refer to your knowledge base.\n"
            f"The SQL Server database has these tables - {tables}\n"
            "As a first step, please always use the 'describe_table' function to know the columns of any table for faster results. Slower results are not appreciated."
            "Do not make any assumptions about what column names in a particular table. "            
        )),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

tools = [
    run_sql_query_tool, 
    describe_table_tool
    ]

agent = OpenAIFunctionsAgent(
    llm=chat,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(
    agent=agent,
    verbose=True,
    tools=tools,
    memory=memory    
)

# Define function to submit user input
def submit():
    # Set entered_prompt to the current value of prompt_input
    st.session_state.entered_prompt = st.session_state.prompt_input
    # Clear prompt_input
    st.session_state.prompt_input = ""
    
    # Re-instate the earlier messages in the memory object
    memory.chat_memory.messages = []
    memory.chat_memory.messages = st.session_state['memory_object']
    
    #Send the user input to the LLM
    ai_response = agent_executor(st.session_state.entered_prompt)

    # Find the start and end indices of the messages part. The recent response is also part of the memory object
    start_index = str(memory).find("[") + 1
    end_index = str(memory).find("]", start_index)

    # Extract the messages string
    messages_string = str(memory)[start_index:end_index]

    #Create an array of string where individual element is either the string representation of HumanMessage or AIMessage
    pattern = r"(\w+\(.*?\))"
    matches = re.findall(pattern, messages_string)

    message_list = [] # Redundant code but feeling lazy to amend
    message_list.extend(matches) # Redundant code but feeling lazy to amend

    st.session_state['chat_history'] = []
    st.session_state['chat_history'].extend(message_list)
    st.session_state['memory_object'] = []

if  st.session_state['chat_history']:
    # Display the chat history and populate the memory_object session variable
    if st.session_state['chat_history']:
        for i in range(len(st.session_state['chat_history'])):
            # Display Human message
            if "HumanMessage" in st.session_state['chat_history'][i]:
                message(re.sub(r"HumanMessage\(content='|'\)|AIMessage\(content='", "", st.session_state['chat_history'][i]),
                        is_user=True, key=str(i) + '_user')
                st.session_state['memory_object'].append(HumanMessage(content=re.sub(r"HumanMessage\(content='|'\)|AIMessage\(content='", "", st.session_state['chat_history'][i])))
            else:
            # Display AI message
                message(re.sub(r"HumanMessage\(content='|'\)|AIMessage\(content='", "", st.session_state['chat_history'][i]), key=str(i))
                st.session_state['memory_object'].append(AIMessage(content=re.sub(r"HumanMessage\(content='|'\)|AIMessage\(content='", "", st.session_state['chat_history'][i])))

       

#Create a text input for user
st.text_input('YOU: ', key='prompt_input', on_change=submit)


