import streamlit as st
from streamlit.logger import get_logger

from llm.chat_agent import ChatAgent

logger = get_logger(__name__)
# tag::setup[]
# Page Config
st.set_page_config(page_title="Chatbot", page_icon=":copilot:", layout="wide")
# end::setup[]
chat_agent = ChatAgent()
# tag::session[]
# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi, I'm SystemExpert!  How can I help you?",
        },
    ]
# end::session[]


def write_message(role, content, save=True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        st.session_state.messages.append({"role": role, "content": content})

    # Write to UI

    with st.chat_message(role):
        st.markdown(content)


# tag::submit[]
# Submit handler
def handle_submit(message):
    """
    Submit handler:

    You will modify this method to talk with an LLM and provide
    context using data from Neo4j.
    """

    # Handle the response
    with st.spinner("Thinking..."):

        # from time import sleep
        # sleep(1)
        # write_message('assistant', message)
        response = chat_agent.generate_response(message)
        write_message("assistant", response)


# end::submit[]


# tag::chat[]
# Display messages in Session State
for message in st.session_state.messages:
    write_message(message["role"], message["content"], save=False)

# Handle any user input
if prompt := st.chat_input("What's up?"):
    # Display user message in chat message container
    write_message("user", prompt)

    # Generate a response
    handle_submit(prompt)
# end::chat[]
