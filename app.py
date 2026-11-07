import os
import streamlit as st

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import get_weather, calculate
from tool_schemas import agent_tools


# API KEY
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        API_KEY = None

if not API_KEY:
    st.error("GEMINI_API_KEY is missing.")
    st.stop()


# GEMINI CLIENT
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash"


# STREAMLIT UI
st.set_page_config(
    page_title="AI Agent",
    page_icon="🤖"
)

st.title("🤖 Week 5: AI Agent")

st.write(
    "Ask me about live weather or mathematical calculations."
)


if "history" not in st.session_state:
    st.session_state.history = []

if "api_history" not in st.session_state:
    st.session_state.api_history = []


# DISPLAY CHAT
for message in st.session_state.history:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# CLEAR CHAT
if st.button("Clear Chat"):

    st.session_state.history = []
    st.session_state.api_history = []

    st.rerun()


# USER INPUT
prompt = st.chat_input("Ask your question...")


if prompt:

    st.session_state.history.append({
        "role": "user",
        "content": prompt
    })

    st.session_state.api_history.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
    )

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):

        with st.spinner("AI is thinking..."):

            try:

                final_answer = None

                # AGENT EXECUTION LOOP
                for attempt in range(3):

                    response = client.models.generate_content(

                        model=MODEL,

                        contents=st.session_state.api_history,

                        config=types.GenerateContentConfig(
                            tools=[agent_tools]
                        )

                    )

                    function_calls = response.function_calls

                    # NORMAL TEXT RESPONSE
                    if not function_calls:

                        final_answer = response.text or (
                            "Sorry, no response received."
                        )

                        st.session_state.api_history.append(
                            response.candidates[0].content
                        )

                        break

                    # SAVE MODEL FUNCTION CALL
                    st.session_state.api_history.append(
                        response.candidates[0].content
                    )

                    tool_parts = []

                    # EXECUTE PYTHON FUNCTIONS
                    for call in function_calls:

                        st.info(
                            f"Using Tool: {call.name}"
                        )

                        try:

                            if call.name == "get_weather":

                                result = get_weather(
                                    **call.args
                                )

                            elif call.name == "calculate":

                                result = calculate(
                                    **call.args
                                )

                            else:

                                result = {
                                    "error": "Unknown tool"
                                }

                        except Exception as e:

                            result = {
                                "error": str(e)
                            }

                        tool_parts.append(

                            types.Part.from_function_response(

                                name=call.name,

                                response={
                                    "result": result
                                }

                            )

                        )

                    # SEND TOOL RESULTS BACK TO GEMINI
                    st.session_state.api_history.append(

                        types.Content(

                            role="user",

                            parts=tool_parts

                        )

                    )

                if final_answer is None:

                    final_answer = (
                        "Maximum tool attempts reached. "
                        "Please try again."
                    )

                st.write(final_answer)

                st.session_state.history.append({

                    "role": "assistant",

                    "content": final_answer

                })

            except Exception as e:

                st.error(f"Error: {e}")