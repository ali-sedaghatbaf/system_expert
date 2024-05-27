import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)


st.write("# Welcome to SystemExpert! 👋")
st.markdown(
        """<span style="word-wrap:break-word;">Welcome to our SystemExpert, your dedicated companion for mastering the intricacies of SystemWeaver effortlessly! 
        Whether you're a seasoned user or just getting started, SystemExpert is here to provide you with expert guidance and support every step of the way. 
        From navigating the interface to maximizing productivity, our AI-powered assistant is equipped with the knowledge and tools to address your SystemWeaver queries and challenges. 
        Engage in conversational interactions, access helpful resources, and unlock the full potential of SystemWeaver with ease. 
        Say goodbye to complexity and hello to seamless collaboration – with SystemExpert, you're always in control.</span>
    """
    )
st.markdown("""
            <style>
                div[data-testid="column"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                }
                
            </style>
            """, unsafe_allow_html=True)
col1, col2 = st.columns([1,1])
with col1:
    if st.button("Chat with the AI Agent"):
        st.switch_page("pages/1_Chatbot.py")
with col2:
    if st.button("Get assistance with TARA"):
            st.switch_page("pages/2_TARA_Assistant.py")