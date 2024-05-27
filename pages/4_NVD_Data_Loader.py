import streamlit as st
from streamlit.logger import get_logger


from adapters.neo4j_adapter import NVDNeo4j
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
st.set_page_config("NVD Data Loader", page_icon=":copilot:",layout="wide")


def get_database():
    return st.radio(
        "Select the database",
        ["CVE", "CPE"],
        captions=[
            "Common Vulnerability Enumeration",
            "Common Platform Enumeration",
        ],
    )


def get_timestamp():
    col1,_,_, _ = st.columns(4)
    with col1:
        return st.date_input(
            "Fetch data created/updated after", datetime.date(2023, 1, 6)
        )


def render_page():

    st.header("NVD Data Loader")
    st.divider()
    st.subheader("Connect to NVD and load CVE/CPE data into SystemExpert")

    database = get_database()
    timestamp = get_timestamp()

    if st.button("Import data"):
        nvd_data = None
        
        nvd = None
        neo4j = None
        with st.spinner("Connecting to the access point"):
            try:

                nvd = NVD(database)

            except Exception as e:
                st.error(f"Error: {e}", icon="🚨")
                return
        with st.spinner("Fetching data"):

            try:

                nvd_data = nvd.fetch_data(timestamp)
                
            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                return

        with st.spinner("Connecting to Neo4j"):
            try:

                neo4j = NVDNeo4j("Vulnerability" if database == "CVE" else "Product")
                
            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")
                return

        with st.spinner("Inserting data into Neo4j"):
            try:

                neo4j.import_data(nvd_data)
                col1,_ = st.columns(2)
                with col1:
                    st.success("Import successful", icon="✅")

            except Exception as e:
                st.error(f"Error: {e}\n{traceback.format_exc()}", icon="🚨")


render_page()
