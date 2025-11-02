# requirements.txt should contain:
# streamlit
# google-generativeai

import streamlit as st
import google.generativeai as genai

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
# FINAL CORRECTION BASED ON ERROR LOGS:
# The logs show the API call is to the 'v1beta' endpoint.
# The correct model name for that endpoint is "gemini-1.0-pro".
# The tool name "google_search_retrieval" is confirmed correct by the logs.
model = genai.GenerativeModel(
    model_name="gemini-1.0-pro",
    system_instruction="""Concisely answer questions, referring to reliable sources. Cite your sources. Rely on high-quality sources and treat lower quality sources (such as YouTube) with skepticism. """,
    tools=["google_search_retrieval"],
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
                # Create a chat session with the full history
                chat = model.start_chat(history=[
                    {"role": msg["role"], "parts": [msg["content"]]}
                    for msg in st.session_state.messages[:-1]
                ])

                # Send the new prompt and stream the response
                response = chat.send_message(user_prompt, stream=True)

                # Use st.write_stream to display the output as it comes in
                full_response = st.write_stream(response)

                # Add the complete AI response to the session state
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                # Display the actual error message from the API on the app page
                st.error(e)
