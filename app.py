# app.py

import streamlit as st
import openai
import os
from dotenv import load_dotenv
import uuid  # For generating unique conversation IDs

# Import agent scripts
from agents import ceo_agent, cto_agent, cio_agent, cfo_agent

# Import utility functions
from utils.company_info import get_company_name
from utils.database import save_conversation, get_conversation, list_conversations

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_version = "2020-11-07"

# Check if the API key was loaded
if not openai.api_key:
    st.error("OpenAI API key not found. Please set it in the .env file.")
    st.stop()

# Streamlit App Title
st.title("AI Client Persona Chat")

# Sidebar Inputs
st.sidebar.header("Chat Configuration")

# Conversation selection
st.sidebar.subheader("Select Conversation")
conversations = list_conversations()
conversation_options = ['New Conversation']
conversation_mapping = {}

# Build the list of conversation options
for item in conversations:
    conv_id = item['id']
    persona = item.get('persona', '')
    company_name = item.get('company_name', '')
    # Create a label for each conversation
    option_label = f"{conv_id} - {persona} ({company_name})"
    conversation_options.append(option_label)
    conversation_mapping[option_label] = conv_id

# Select box for conversation selection
selected_option = st.sidebar.selectbox("Select a previous conversation", conversation_options)

# Determine whether to start a new conversation or load an existing one
if selected_option == 'New Conversation':
    # Start a new conversation
    if 'conversation_id' not in st.session_state or st.session_state.get('conversation_id') != 'new':
        st.session_state.conversation_id = 'new'
        st.session_state.conversation = []
        st.session_state.linkedin_url = ''
        st.session_state.persona = 'CEO'  # Set a default valid persona
        st.session_state.company_name = ''
else:
    # Load existing conversation
    selected_conversation_id = conversation_mapping[selected_option]
    if 'conversation_id' not in st.session_state or st.session_state.conversation_id != selected_conversation_id:
        st.session_state.conversation_id = selected_conversation_id
        conversation_data = get_conversation(st.session_state.conversation_id)
        if conversation_data:
            st.session_state.conversation = conversation_data.get('conversation_data', [])
            st.session_state.linkedin_url = conversation_data.get('linkedin_url', '')
            st.session_state.persona = conversation_data.get('persona', 'CEO')  # Default to 'CEO' if not set
            st.session_state.company_name = conversation_data.get('company_name', '')
        else:
            st.error("Failed to load conversation.")
            st.stop()

# Persona selection and LinkedIn URL input
st.sidebar.subheader("Start a Conversation")

# Define the list of personas
persona_list = ["CEO", "CTO", "CIO", "CFO"]

# Get the current persona from session state or default to 'CEO' if not set or invalid
current_persona = st.session_state.get('persona', 'CEO')
if not current_persona or current_persona not in persona_list:
    current_persona = 'CEO'

# Find the index of the current persona
persona_index = persona_list.index(current_persona)

# Persona selection
persona = st.sidebar.selectbox(
    "Select Client Persona:",
    persona_list,
    index=persona_index
)

# Update session state
st.session_state.persona = persona

# LinkedIn URL input
linkedin_url = st.sidebar.text_input(
    "Enter LinkedIn Company URL:",
    value=st.session_state.get('linkedin_url', '')
)

# Update session state if inputs have changed
if 'linkedin_url' not in st.session_state or linkedin_url != st.session_state.linkedin_url:
    st.session_state.linkedin_url = linkedin_url
    # Extract Company Name
    company_name = get_company_name(linkedin_url)
    if company_name:
        st.session_state.company_name = company_name
    else:
        st.sidebar.error("Invalid LinkedIn URL. Please try again.")
        st.stop()

# Proceed only if LinkedIn URL is provided
if st.session_state.linkedin_url:
    st.sidebar.success(f"Company Name: {st.session_state.company_name}")

    # Prepare company data for the agent
    company_data = {"name": st.session_state.company_name}

    # Display Conversation
    st.header("Conversation")
    for message in st.session_state.conversation:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**{st.session_state.persona}:** {message['content']}")

    # Chat Input using form
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("You:")
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        # Append User Input to Conversation
        st.session_state.conversation.append({"role": "user", "content": user_input})

        # Generate Agent Response
        try:
            if st.session_state.persona == "CEO":
                response = ceo_agent.respond(st.session_state.conversation, company_data)
            elif st.session_state.persona == "CTO":
                response = cto_agent.respond(st.session_state.conversation, company_data)
            elif st.session_state.persona == "CIO":
                response = cio_agent.respond(st.session_state.conversation, company_data)
            elif st.session_state.persona == "CFO":
                response = cfo_agent.respond(st.session_state.conversation, company_data)
            else:
                st.error("Invalid persona selected.")
                st.stop()
        except Exception as e:
            st.error(f"Error generating response: {e}")
            st.stop()

        # Append Agent Response to Conversation
        st.session_state.conversation.append({"role": "assistant", "content": response})

        # If it's a new conversation, generate a unique ID
        if st.session_state.conversation_id == 'new':
            st.session_state.conversation_id = str(uuid.uuid4())

        # Save updated conversation to database
        save_conversation(
            st.session_state.conversation_id,
            st.session_state.conversation,
            st.session_state.persona,
            st.session_state.linkedin_url,
            st.session_state.company_name
        )

        # Display the agent's response
        st.markdown(f"**{st.session_state.persona}:** {response}")

else:
    st.info("Please enter a LinkedIn Company URL to start the conversation.")
