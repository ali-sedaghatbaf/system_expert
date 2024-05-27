import streamlit as st
from streamlit.logger import get_logger


from adapters.neo4j_adapter import MITRENeo4j
from adapters.mitre_adapter import MITRE
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
st.set_page_config("MITRE ATT&CK Data Loader", page_icon=":copilot:",layout="wide")


def get_access():
    return st.radio(
        "Select the access type",
        ["ATT&CK TAXII server", "MITRE/CTI"],
        captions=[
            "Access live ATT&CK content over the internet.",
            "Download the latest published version.",
        ],
    )


def get_timestamp():
    col1,_,_, _ = st.columns(4)
    with col1:
        return st.date_input(
            "Fetch data created/updated after", datetime.date(2024, 1, 6)
        )


def render_page():

    st.header("MITRE ATT&CK Data Loader")
    st.divider()
    st.subheader("Connect to MITRE ATT&CK and load data into SystemExpert")

    access_type = get_access()
    timestamp = get_timestamp().strftime("%Y-%m-%dT%H:%M:%SZ")

    if st.button("Import data"):
        mitre_objects = None
        mitre_relations = None
        mitre = None
        neo4j = None
        with st.spinner("Connecting to the access point"):
            try:

                mitre = MITRE(access_type == "ATT&CK TAXII server")

            except Exception as e:
                st.error(f"Error: {e}", icon="🚨")
                return
        with st.spinner("Fetching data"):

            try:

                mitre_objects = mitre.fetch_data(timestamp)
                mitre_relations = mitre.get_relations()
            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                return

        with st.spinner("Connecting to Neo4j"):
            try:

                neo4j = MITRENeo4j()

            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                return

        with st.spinner("Inserting data into Neo4j"):
            try:

                neo4j.import_data(mitre_objects, mitre_relations)
                col1,_ = st.columns(2)
                with col1:
                    st.success("Import successful", icon="✅")

            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")


render_page()
