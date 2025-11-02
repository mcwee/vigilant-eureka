# requirements.txt should contain:
# streamlit
# google-generativeai

import streamlit as st
from google import genai
from google.genai import types

# --- App Configuration ---
st.set_page_config(
    page_title="Conversational Smart Search",
    page_icon="🤖",
    layout="centered",
)

# --- App Title and Description ---
st.title("🤖✨ Dave0's Smart Search")
st.write("Conversational search with citations. Ask follow-ups.")


# --- API Key and Client Configuration ---
# Securely configure the API key from Streamlit's secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    # In this style, we instantiate a Client object
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("API key not found. Please add `GOOGLE_API_KEY` to your Streamlit secrets.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred during client configuration: {e}")
    st.stop()


# --- Model Configuration Objects ---
# In this style, configuration is done through explicit "types" objects
system_instruction = types.Part.from_text(
    """Concisely answer questions, referring to reliable sources. Cite your sources. Rely on high-quality sources and treat lower quality sources (such as YouTube) with skepticism. """
)

# Using the tool name from the error logs
tools = [
    types.Tool.from_google_search_retrieval()
]

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
                # Build the full conversation history in the 'types.Content' format
                # The old client does not have a stateful 'chat' object
                contents = []
                for message in st.session_state.messages:
                    role = "user" if message["role"] == "user" else "model"
                    contents.append(
                        types.Content(role=role, parts=[types.Part.from_text(message["content"])])
                    )

                # Call the API using the client's stream method
                response_stream = client.models.generate_content_stream(
                    model="models/gemini-1.0-pro", # This model name is from the 'v1beta' endpoint
                    contents=contents,
                    system_instruction=system_instruction,
                    tools=tools
                )

                # Stream the text from each chunk of the response
                def stream_chunks(stream):
                    for chunk in stream:
                        yield chunk.text

                full_response = st.write_stream(stream_chunks(response_stream))

                # Add the complete AI response to the session state
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                # Display the actual error message from the API on the app page
                st.error(e)
