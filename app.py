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
st.title("🤖 Conversational Smart Search")
st.write("This app uses Google Search to answer questions conversationally, with citations.")

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
# This is where we translate the logic from your original script
# We define the system instruction and enable the Google Search tool.
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    system_instruction="""Concisely answer questions, referring to reliable sources. Cite your sources. Rely on high-quality sources and treat lower quality sources (such as YouTube) with skepticism. """,
    tools=['google_search'],
)

# --- Chat Interface ---
# Get user input from a text area
user_prompt = st.text_area("Enter your question:", height=100)

# Create a button to send the prompt
if st.button("Generate Answer"):
    if user_prompt:  # Check if the user has entered anything
        with st.spinner("Searching and generating response..."):  # Show a loading message
            try:
                # To stream the response, we call generate_content with stream=True
                response_stream = model.generate_content(user_prompt, stream=True)

                # Use st.write_stream to display the output as it comes in
                st.write("### AI Response:")
                st.write_stream(response_stream)

            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
    else:
        st.warning("Please enter a question first.")
