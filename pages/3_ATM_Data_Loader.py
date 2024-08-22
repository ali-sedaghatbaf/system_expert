import streamlit as st
from streamlit.logger import get_logger

from io import StringIO
from adapters.neo4j_adapter import ATMNeo4j
from adapters.nvd_adapter import NVD
import traceback
import datetime
from st_pages import add_page_title, add_indentation

url = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]

ollama_base_url = st.secrets["OLLAMA_BASE_URL"]
embedding_model_name = st.secrets["EMBEDDING_MODEL"]


logger = get_logger(__name__)


# Streamlit
# add_indentation()
st.set_page_config("ATM Data Loader", page_icon=":copilot:", layout="wide")


def get_uploder():
    col1, *_ = st.columns(4)
    with col1:
        return st.file_uploader("Choose the ATM file")


def render_page():

    st.header("ATM Data Loader")
    st.divider()
    st.subheader("Load ATM data into SystemExpert")

    uploaded_file = get_uploder()

    if uploaded_file is not None:
        atm_data = None

        neo4j = None

        with st.spinner("Uploading data"):

            try:
                import json

                atm_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()

            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                return

        with st.spinner("Connecting to Neo4j"):
            try:

                neo4j = ATMNeo4j()

            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                return

        with st.spinner("Inserting data into Neo4j"):
            try:

                neo4j.import_data(atm_data)
                col1, _ = st.columns(2)
                with col1:
                    st.success("Import successful", icon="✅")

            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")


render_page()
