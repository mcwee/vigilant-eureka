# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
import google.generativeai as genai

# from google import genai
# from google.genai import types
import streamlit as st

# --- App Title and Description ---
st.title("🤖✨ Dave0's Smart Search")
st.write("Conversational search with citations. Ask follow-ups.")

# --- API Key Configuration ---
# IMPORTANT: This line looks for the API key in Streamlit's secret management
# You will set this in the Streamlit Community Cloud settings.
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("API key not found. Please add it to your Streamlit secrets.")
    st.stop()

# --- Chat Interface ---
# Get user input from a text area
user_prompt = st.text_area("Enter your message to the AI:", height=150)

# Create a button to send the prompt
if st.button("Send"):
    if user_prompt: # Check if the user has entered anything
        with st.spinner("The AI is thinking..."): # Show a loading message
            try:
                # Send the prompt to the model
                response = model.generate_content(user_prompt)
                # Display the AI's response
                st.write("### AI Response:")
                st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a message first.")

# def generate():
#    client = genai.Client(
#        api_key=os.environ.get("GEMINI_API_KEY"),
#    )

    model = "gemini-2.5-pro"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    tools = [
        types.Tool(url_context=types.UrlContext()),
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        tools=tools,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""Concisely answer questions, referring to reliable sources. Cite your sources. Rely on high-quality sources and treat lower quality sources (such as YouTube) with skepticism. """),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
