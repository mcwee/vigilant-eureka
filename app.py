# requirements.txt should contain:
# streamlit
# google-generativeai

import streamlit as st
import google.generativeai as genai
# We may need to import the lower-level 'Tool' object if the simple string doesn't work.
# For now, we will try the simplest correct format.

# --- App Configuration ---
st.set_page_config(
    page_title="Conversational Smart Search",
    page_icon="🤖",
    layout="centered",
)

# --- App Title and Description ---
st.title("🤖✨ Dave0's Smart Search")
st.write("Conversational search with citations. Ask follow-ups.")


# --- API Key Configuration ---
# Securely configure the API key from Streamlit's secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("API key not found. Please add `GOOGLE_API_KEY` to your Streamlit secrets.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred during API key configuration: {e}")
    st.stop()


# --- Model Configuration ---
# CORRECTED SECTION:
# We enable the Google Search tool. The correct way is to use a Tool object.
# However, let's try the simplest form that specifies grounding directly.
try:
    from google.generativeai.types import Tool

    # The modern and explicit way to define the search tool
    google_search_tool = Tool.from_google_search_retrieval()

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        system_instruction="""Concisely answer questions, referring to reliable sources. Cite your sources. Rely on high-quality sources and treat lower quality sources (such as YouTube) with skepticism. """,
        tools=[google_search_tool], # Pass the correctly defined tool object
    )
except (ImportError, AttributeError):
    # Fallback for slightly different library versions or simpler cases
    # This enables grounding which uses Google Search.
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        system_instruction="""Concisely answer questions, referring to reliable sources. Cite your sources. Rely on high-quality sources and treat lower quality sources (such as YouTube) with skepticism. """,
        tools=["google_search_retrieval"], # Using the name from the error log
    )


# --- Chat Interface ---
# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input from a chat input box
if user_prompt := st.chat_input("Ask your question here:"):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate and display the AI's response
    with st.chat_message("assistant"):
        with st.spinner("Searching and thinking..."):
            try:
                # Start a chat session to maintain context
                chat = model.start_chat(history=[
                    {"role": msg["role"], "parts": [msg["content"]]}
                    for msg in st.session_state.messages[:-1] # Exclude the last user message
                ])
                # Send the new prompt and stream the response
                response = chat.send_message(user_prompt, stream=True)
                # Use st.write_stream to display the output as it comes in
                full_response = st.write_stream(response)
                # Add the complete AI response to session state
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred: {e}")
