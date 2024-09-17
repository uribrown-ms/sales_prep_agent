# app.py

import streamlit as st
from agents import ceo_agent, cto_agent, cio_agent, cfo_agent
from utils.company_info import get_company_name
import openai
import os
from dotenv import load_dotenv

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
persona = st.sidebar.selectbox("Select Client Persona:", ["CEO", "CTO", "CIO", "CFO"])
linkedin_url = st.sidebar.text_input("Enter LinkedIn Company URL:")

# Initialize Session State
if 'conversation' not in st.session_state or linkedin_url != st.session_state.get('linkedin_url') or persona != st.session_state.get('persona'):
    st.session_state.conversation = []
    st.session_state.linkedin_url = linkedin_url
    st.session_state.persona = persona

if linkedin_url:
    # Extract Company Name
    company_name = get_company_name(linkedin_url)
    if company_name:
        st.sidebar.success(f"Company Name: {company_name}")
    else:
        st.sidebar.error("Invalid LinkedIn URL. Please try again.")
        st.stop()

    # Placeholder for additional company data
    company_data = {"name": company_name}

    # Chat Input using form
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("You:")
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        # Append User Input to Conversation
        st.session_state.conversation.append({"role": "user", "content": user_input})

        # Generate Agent Response
        try:
            if persona == "CEO":
                response = ceo_agent.respond(st.session_state.conversation, company_data)
            elif persona == "CTO":
                response = cto_agent.respond(st.session_state.conversation, company_data)
            elif persona == "CIO":
                response = cio_agent.respond(st.session_state.conversation, company_data)
            elif persona == "CFO":
                response = cfo_agent.respond(st.session_state.conversation, company_data)
            else:
                st.error("Invalid persona selected.")
                st.stop()
        except Exception as e:
            st.error(f"Error generating response: {e}")
            st.stop()

        # Append Agent Response to Conversation
        st.session_state.conversation.append({"role": "assistant", "content": response})

    # Display Conversation
    for message in st.session_state.conversation:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**{persona}:** {message['content']}")
